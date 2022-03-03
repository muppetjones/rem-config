# rem-config
Configuration files for various tools and software

## BASH

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