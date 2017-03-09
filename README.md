# Node.py standalone builder

Builds the currently installed version of Node.py and incoorporates its
dependencies, which are namely `six` and `localimport`, into the same file
using optionally compressed and minified Python blobs.

    $ node.py index.py
    Usage: index.py [OPTIONS]

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
