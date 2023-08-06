# mp2hudcolor
Sets a user-defined HUD color for Metroid Prime 2: Echoes. Values are stored as R/G/B where values are 0.0 to 1.0.

Build instructions all are written for Linux, but should adapt fine for Windows.

# Usage

## Python Module
```sh
> pip install mp2hudcolor
> python
>>> import mp2hudcolor
>>> mp2hudcolor.mp2hudcolor_c("Standard.ntwk", "Standard-out.ntwk", 1.0, 0.5, 0.25) # (input, output, red, green, blue)
```

## Standalone
```sh
# mp2hudcolor <input> <output> <red> <green> <blue>
mp2hudcolor Standard.ntwk Standard-out.ntwk 1.0 0.5 0.25
```

# Build

## Python

```
tools/venv.sh
tools/build-cython.sh
```

## Standalone
```sh
tools/build-standalone.sh
```
