# Node.Py standalone builder

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

    Options:
      --info
      -c, --compress
      -m, --minify
      -f, --fullblob
      -o, --output TEXT
      --help             Show this message and exit.
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
    -s, --store-method [direct|default]
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

### v0.0.2

- Add `nodepy-standalone-mkblob` command
- Update `blobbify.py` to use Click instead of argparse
