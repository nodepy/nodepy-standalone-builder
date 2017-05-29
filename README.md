# nodepy/standalone-builder

Builds the currently installed version of Node.py and incoorporates its
dependencies, which are namely `six` and `localimport`, into the same file
using optionally compressed and minified Python blobs.

## Install

    $ ppym install --global nodepy-standalone-builder

## CLI

    $ nodepy-standalone-builder --help
    Usage: nodepy-standalone-builder [OPTIONS]

    Generate a standalone-version of the installed Node.py version by inlining
    its dependencies. Optionally, Node.py can be inlined as a Python-blob,
    too.

    Note that the -O,--minify-obfuscate option does not always work (eg. when
    using a variable 'file' in a Python 3.6 source file) due to
    incompatibilities in pyminifier.

    Options:
    -c, --compress
    -m, --minify
    -O, --minify-obfuscate
    -f, --fullblob
    -o, --output TEXT
    --help                  Show this message and exit.

---

    $ nodepy-standalone-mkblob --help
    Usage: nodepy-standalone-mkblob [OPTIONS] SOURCEFILE

    Create a base64 encoded, optionally compressed and minified blob of a
    Python source file. Note that the -O,--minify-obfuscate option does not
    always work (eg. when using a variable 'file' in a Python 3.6 source file)
    due to incompatibilities in pyminifier.

    Options:
    -o, --output FILENAME
    -c, --compress
    -m, --minify
    -O, --minify-obfuscate
    -w, --line-width INTEGER
    -e, --export-symbol TEXT
    --help                          Show this message and exit.

## API

### `nodepy-standalone-builder:build(compress)`

```
build(compress=False, minify=False, fullblob=False)
```

Builds the single-file distribution of Node.Py using the specified
parameters. Blobs of modules are always base64 encoded.

__Arguments__

- compress (`bool`): True to compress the code using zlib.
- minify (`bool`): True to minify the source code using pyminifier.
- fullblob (`bool`): True to generate one single blob that results in
    the `nodepy` module, otherwise only replace non-standard library
    imports with such blobs.

__Returns__

`str`: The resulting standalone version of Node.Py.

## Changelog

### v0.0.5

- Add `--blob/--no-blob` option, allowing to use `--no-blob` to generate an
  uncompressed blob for debugging purposes
- Modules executed in blobs now inherit the global `__file__` member of the
  executing scope

### v0.0.4

- Rename from `nodepy-standalone-builder` to `@nodepy/standalone-builder`

### v0.0.3

- Removed `-s,--store-method` argument from `mkblob`

### v0.0.2

- Rename `blobbify.py` to `mkblob.py`
- Add `nodepy-standalone-mkblob` command
- Update `mkblob.py` to use Click instead of argparse
