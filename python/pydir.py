#!/usr/bin/env python3
"""Given one or more directory paths, create dir and add __init__.py.

Example:
    $ pydir proj tests/{unit,functonal}/proj/

Example:
    $ pydir --project proj
"""

import itertools
import logging
import os.path
import sys
from argparse import ArgumentParser
from pathlib import Path
from pprint import pformat
from token import OP
from typing import Iterable, Mapping, Optional

LOGGER = logging.getLogger("pydir")

# section
# ======================================================================

if sys.version_info.major == 3 and sys.version_info.minor < 9:

    def is_relative_to(self, other: Path) -> bool:
        try:
            self.relative_to(other)
        except ValueError:
            return False
        return True

    setattr(Path, "is_relative_to", is_relative_to)


# section
# ======================================================================


def launch(
    config: Mapping,
    logger: logging.Logger = None,
) -> None:
    """Launch."""
    do_make_dirs = config.get("do_make_dirs")  # type: bool
    targets = config.get("target")  # type: Iterable[Path]

    if do_make_dirs:
        make_dirs(*targets)
    make_init_files(*targets, logger=logger)


# section
# ----------------------------------


def make_dirs(*targets: Path) -> None:
    for path in targets:
        path.mkdir(exist_ok=True, parents=True)


def make_init_files(*targets: Path, logger: logging.Logger = None) -> None:
    logger = logger or LOGGER
    allowed_parents = [Path.cwd(), ]  # Path.home()]
    targets = [p.resolve() for p in targets]
    common_prefix = Path(os.path.commonprefix(allowed_parents + targets))
    if not any(common_prefix.is_relative_to(x) for x in allowed_parents):
        raise ValueError(f"targets must be within allowed dir: {allowed_parents}")

    def _accumulate(path):
        # break down each part of the path
        relpath = path.relative_to(common_prefix)
        for acc in itertools.accumulate(relpath.parts, func=Path):
            init_path = Path(common_prefix, acc, "__init__.py")
            if init_path.exists():
                continue
            yield init_path

        # find all sub directories
        for root, directories, files in os.walk(path):
            for dpath in directories:
                init_path = Path(root, dpath, "__init__.py")
                if init_path.exists():
                    continue
                yield init_path

    paths = [acc_path for path in targets for acc_path in _accumulate(path)]
    for path in paths:
        path.touch()
    logger.info("Touched %d __init__.py files", len(paths))
    logger.debug(pformat(paths))
    if paths:
        logger.debug("\n  %s", "\n  ".join(str(x) for x in paths))


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
        "language": {
            "choices": ["python"],
            "default": "python",
            "help": "Language format",
            "options": ["--language"],
        },
        "target": {
            "nargs": "*",
            "type": Path,
        },
        "toggle_mkdir": {
            "dest": "do_make_dirs",
            "action": "store_false",
            "default": True,
            "options": ["--no-make-dirs"],
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
            format='%(asctime)s %(levelname)s:%(name)s %(message)s',
            level=logging.DEBUG,
        )

    main()


if __name__ == "__main__":
    run()


# __END__
