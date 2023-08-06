# buildincr

Increment the value in the build-serial-file by one.

## Install

```
pip install buildincr
```

## Usage

```
Usage: buildincr.py [OPTIONS] BUILD_SERIAL_FILE

  Increment the value in the build-serial-file by one.

Options:
  -l, --lock-file TEXT
  --help                Show this message and exit.
```

## Example

```
cat build.serial.txt
# show the value: 123

buildincr build.serial.txt
# show the result: 124

cat build.serial.txt
# show the value: 124
```

## Release

### v0.1.0

- First release.
