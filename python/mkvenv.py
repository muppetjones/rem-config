#!/usr/bin/env python3
"""Make virtul environment.

Example:
    $ mkvenv my-env 3.10
"""
import itertools
import logging
import os.path
import re
import shlex
import subprocess
import sys
from argparse import ArgumentParser
from cgitb import text
from pathlib import Path
from pprint import pformat
from token import OP
from typing import Iterable, Mapping, Optional

try:
    from functools import cache  # type: ignore
except ImportError:  # pragma: no cover
    from functools import lru_cache, partial

    cache = lru_cache(maxsize=None)


LOGGER = logging.getLogger("mkenv")


# section
# ======================================================================


def launch(
    config: Mapping,
    logger: logging.Logger = None,
) -> None:
    """Launch."""
    location = config.get("location") or Path.cwd()
    name = config.get("name", "venv")
    version = config.get("version")
    exec_path = config.get("exec_path") or find_exec(version)
    do_autoenv = config.get("do_add_autoenv")

    try:
        create_venv(name, location, exec_path=exec_path)
    except FileExistsError:
        logger.warning('Found existing venv "%s" at "%s"', name, location)
    else:
        logger.info('Created venv "%s" (v%s) at "%s"', name, version, location)

    if do_autoenv:
        add_autoenv_binding(name, location)


# section
# ----------------------------------


def add_autoenv_binding(
    name: str, location: Path, logger: logging.Logger = None
) -> None:
    logger = logger or LOGGER
    _add_autoenv_binding_to_activate_venv(name, location, logger)
    _add_autoenv_binding_to_deactivate_venv(logger)


def _add_autoenv_binding_to_activate_venv(
    name: str, location: Path, logger: logging.Logger
) -> None:
    entry = f"source {location}/{name}"
    rx = re.compile(r"^(activate|source)\s+.+$", re.MULTILINE)
    path = Path(".env")
    content = path.read_text() if path.exists() else ""
    if match := rx.search(content):
        match_str = match.group()
        if match_str == entry:
            logger.info("Found matching autoenv entry. No change applied.")
            return  # no change -- don't bother user
        logger.warning("Found existing autoenv entry:\n\n\t%s\n", match_str)
        response = input(f'Replace existing entry? (n/Y)  ')
        if "Y" != response:
            return  # do not replace
        content.replace(match_str, f"source {location}/{name}")
        path.write_text(content.lstrip())
    else:
        lines = "\n\n# Activate venv upon entering the directory\n{entry}\n"
        content = content.rstrip() + lines
        path.write_text(content.lstrip())


def _add_autoenv_binding_to_deactivate_venv(logger: logging.Logger) -> None:
    path = Path(".env.leave")
    content = path.read_text() if path.exists() else ""
    if "deactivate" in content:
        return
    lines = [
        "",
        "# deactivate venv when leaving",
        "deactivate",
    ]
    content = content.rstrip() + "\n".join(lines)
    path.write_text(content.lstrip())


def create_venv(
    name: str, location: Path, exec_path: Path, logger: logging.Logger = None
) -> None:
    """Create a python venv at target location."""
    logger = logger or LOGGER
    target = Path(location, name)
    target = target.expanduser().resolve()
    if target.exists():
        raise FileExistsError(target)
    command = f"{exec_path} -m venv {target}"
    try:
        subprocess.run(
            shlex.split(command),
            capture_output=True,
            check=True,
            text=True,
        )
    except subprocess.CalledProcessError as err:
        logger.debug(err.stderr)
        raise RuntimeError("Error creating venv")


@cache
def get_pyenv_root(logger: logging.Logger = None) -> Path:
    """Return pyenv root. Raise on error."""
    logger = logger or LOGGER
    result = subprocess.run(
        shlex.split("pyenv root"),
        capture_output=True,
        text=True,
    )
    if 0 != result.returncode:
        logger.error(result.stderr)
        raise RuntimeError("error retrieving pyenv root")
    root = result.stdout.strip().split("\n")[-1]
    return Path(root)


@cache
def get_pyenv_versions(logger: logging.Logger = LOGGER) -> Iterable[str]:
    """Return pyenv versions. Raise on error."""
    logger = logger or LOGGER
    rx = re.compile(r"^\s*\*?\d+.\d")
    result = subprocess.run(
        shlex.split("pyenv versions"),
        capture_output=True,
        text=True,
    )
    if 0 != result.returncode:
        logger.error(result.stderr)
        raise RuntimeError("error retrieving pyenv versions")

    versions = [
        line.strip("* ") for line in result.stdout.split("\n") if rx.match(line)
    ]
    return versions


def find_exec(version: str, logger: logging.Logger = None) -> Path:
    """Find executable path and return it."""
    logger = logger or LOGGER
    if not version:
        raise ValueError("Version required to lookup python exec")
    pyenv_root = get_pyenv_root(logger)
    pyenv_vers = get_pyenv_versions(logger)

    version = match_version(version, pyenv_vers)
    logger.info("Using %s from pyenv", version)
    expected = Path(pyenv_root, "versions", version, "bin/python")
    if not expected.exists:
        raise FileNotFoundError(expected)
    return expected


def match_version(value: str, options: Iterable[str]) -> str:
    """Return best match or raise."""
    almost = []
    for opt in options:
        if value == opt:
            return opt  # EARLY EXIT
        elif opt.startswith(value):
            almost.append([int(x) for x in opt.split('.')])
        else:
            continue
    try:
        closest = sorted(almost, reverse=True)[0]  # latest, matching release
        return ".".join(str(x) for x in closest)
    except IndexError:
        raise ValueError(f"No matching python version: {value} ({options}")


# section
# ======================================================================


def safe_parse(
    parser: ArgumentParser, argv: Optional[Iterable] = None
) -> Mapping:
    try:
        args, _ = parser.parse_known_args(argv)
    except TypeError:
        args, _ = parser.parse_known_args()
    return args


def setup_parser(parser: Optional[ArgumentParser] = None) -> ArgumentParser:
    parser = parser or ArgumentParser()
    config = {
        "location": {
            "default": "~/venv",
            "help": "Where to create the venv (defuault: ~/venv)",
            "options": ["-C"],
        },
        "exec_path": {
            "help": "Explicit path to python executable. Uses pyenv by default.",
            "options": ["--exec"],
            "type": Path,
        },
        "version": {
            "help": "Python version",
            "type": str,
        },
        "name": {
            "help": "Venv name",
            "type": str,
        },
        "toggle_autoenv": {
            "action": "store_true",
            "dest": "do_add_autoenv",
            "default": False,
            "help": "Add activate to autoenv",
            "options": ["--autoenv"],
        },
    }
    for name, cfg in config.items():
        name_or_flags = cfg.get("options", [])
        cfg["dest"] = cfg.get("dest", name)
        try:
            del cfg["options"]
        except KeyError:
            pass
        parser.add_argument(*name_or_flags, **cfg)
    return parser


def main(
    argv: Iterable[str] = None,
    parser: Optional[ArgumentParser] = None,
    logger: logging.Logger = None,
):
    """Entrypoint."""
    logger = logger or LOGGER
    parser = setup_parser(parser)
    args = safe_parse(parser, argv)

    config = vars(args)
    launch(config, logger=logger)


def run():
    """Script."""
    try:
        import locutus  # type: ignore

        locutus.config_from_argv(
            defaults={"level": logging.DEBUG, "formatter": "color"}
        )
    except ImportError:  # pragma: no cover
        logging.basicConfig(
            format='%(asctime)s %(levelname)s %(name)s:%(lineno)s %(message)s',
            level=logging.DEBUG,
        )
    except Exception as err:
        logging.root.exception(locutus.__file__)
        raise

    main()


if __name__ == "__main__":
    run()


# __END__
