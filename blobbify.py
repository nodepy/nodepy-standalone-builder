# Copyright (C) 2016  Niklas Rosenstein
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__author__ = 'Niklas Rosenstein <rosensteinniklas@gmail.com>'
__version__ = '1.3'

import argparse
import base64
import os
import subprocess
import sys
import tempfile
import textwrap
import zlib

EXEC_TEMPLATE = '''
import base64 as b, types as t; m=t.ModuleType({name!r}); blob=b'\\
{blobdata}'
exec(b.b64decode(blob), vars(m)); {storemethod}; del blob, b, t, m;
'''

EXEC_TEMPLATE_COMPRESSED = '''
import base64 as b, types as t, zlib as z; m=t.ModuleType({name!r}); blob=b'\\
{blobdata}'
exec(z.decompress(b.b64decode(blob)), vars(m)); {storemethod}
del blob, b, t, z, m;
'''

STOREMETHOD_SYMBOL = 'blobbify_store[{name!r}]=m;{symbol}=getattr(m,{symbol!r})'
STOREMETHOD_DIRECT = '{name}=m'
STOREMETHOD_DEFAULT = 'blobbify_store[{name!r}]=m'

def silent_remove(filename):
  try:
    os.remove(filename)
  except OSError as exc:
    if exc.errno != errno.ENONENT:
      raise

def minify(code, obfuscate=False):
  fp = None
  try:
    with tempfile.NamedTemporaryFile(delete=False) as fp:
      fp.write(code.encode('utf8'))
      fp.close()
      args = ['pyminifier', fp.name]
      if obfuscate:
        args.insert(1, '-O')
      popen = subprocess.Popen(args,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
      result = popen.communicate()[0].decode('utf8')
    if popen.returncode != 0:
      raise OSError('pyminifier exited with returncode {0!r}'.format(popen.returncode))
  finally:
    if fp is not None:
      silent_remove(fp.name)
  return result.replace('\r\n', '\n')

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('file', type=argparse.FileType('r'))
  parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=sys.stdout)
  parser.add_argument('-c', '--compress', action='store_true')
  parser.add_argument('-m', '--minify', action='store_true')
  parser.add_argument('-O', '--minify-obfuscate', action='store_true')
  parser.add_argument('-w', '--line-width', type=int, default=79)
  parser.add_argument('-s', '--store-method', choices=('direct', 'default'))
  parser.add_argument('-e', '--export-symbol')
  args = parser.parse_args()

  data = args.file.read()
  if args.minify:
    data = minify(data, obfuscate=args.minify_obfuscate)
  data = data.encode('utf8')
  if args.compress:
    data = zlib.compress(data)
    template = EXEC_TEMPLATE_COMPRESSED
  else:
    template = EXEC_TEMPLATE
  data = base64.b64encode(data).decode('ascii')

  name = os.path.splitext(os.path.basename(args.file.name))[0]
  if args.export_symbol:
    if args.store_method:
      parser.error('--export-symbol and --store-method can not be combined')
    storemethod = STOREMETHOD_SYMBOL.format(name=name, symbol=args.export_symbol)
  elif args.store_method in ('default', None):
    storemethod = STOREMETHOD_DEFAULT.format(name=name)
  elif args.store_method == 'direct':
    storemethod = STOREMETHOD_DIRECT.format(name=name)

  lines = '\\\n'.join(textwrap.wrap(data, width=args.line_width))
  result = template.format(name=name, blobdata=lines, storemethod=storemethod)
  args.output.write(result)

if __name__ == "__main__":
  sys.exit(main())
