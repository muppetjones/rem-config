# rem-config
Configuration files for various tools and software

## Python

### black

```shell
ln -s $(pwd)/python/black ~/.config/
```

### flake8

```shell
ln -s $(pwd)/python/flake8 ~/.config/
```

### isort

```shell
ln -s $(pwd)/python/isort ~/.isort.cfg
```

### Scripts

```shell
mkdir -p ~/.local/bin
ln -s $(pwd)/python/pydir.py ~/.local/bin/pydir
ln -s $(pwd)/python/mkvenv.py ~/.local/bin/mkvenv
```

## Shell

Most of this configuration assumes you're using BASH.

### Clear
```shell
rm -f ~/.bashrc
rm -f ~/.bash_profile
```

### Mac (Apple Silicon)

```shell
ln -s $(pwd)/shell/bashrc-mac-apple ~/.bashrc
ln -s $(pwd)/shell/bash_profile-mac ~/.bash_profile
```

### Mac (Intel)
```shell
ln -s $(pwd)/shell/bashrc-mac-intel ~/.bashrc
ln -s $(pwd)/shell/bash_profile-mac ~/.bash_profile
```

## Keymap

Follow [these instructions](https://github.com/ColemakMods/mod-dh/tree/master/macOS)

OR

```shell
cp -R ./keyboard_layouts/ColemakDH.bundle /Library/Keyboard\ Layouts/
```

The included bundle corrects the finger mapping for the bottom, left-hand row.

## Vim

Use the [ultimate vimrc](https://github.com/amix/vimrc)

```shell
git clone --depth=1 https://github.com/amix/vimrc.git ~/.vim_runtime
sh ~/.vim_runtime/install_awesome_vimrc.sh
```