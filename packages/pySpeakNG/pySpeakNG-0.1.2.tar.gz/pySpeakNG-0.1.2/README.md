## pySpeakNG
A thin wrapper around [eSpeak-NG](https://github.com/espeak-ng/espeak-ng) for
off-line text-to-speech synthesis. pySpeakNG is very simple, consisting of a
single function which wraps
[eSpeak-NG](https://github.com/espeak-ng/espeak-ng)'s command line interface.

## Requirements
A working installation of the
[eSpeak-NG](https://github.com/espeak-ng/espeak-ng) command line utility for
Linux (and, presumably, for Windows, though this is not officially supported at
this stage). eSpeak-NG is available in the repositories most common GNU/Linux
distributions, and is also buildable with standard tools.

For Debian/Ubuntu/Mint-type systems:
```
sudo apt install espeak-ng
```

For Red Hat/Fedora/Rocky-type systems:
```
sudo dnf install espeak-ng
```

## Installation
Install the latest stable release from PyPI with:
```
python3 -m pip install --upgrade pySpeakNG
```

## Usage
See the `speak()` function and module documentation.