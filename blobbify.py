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

import base64
import click
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
print(z.decompress(b.b64decode(blob)).decode())
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

def blobbify(name, code, compress=False, minify=False, minify_obfuscate=False,
             line_width=79, store_method='direct', export_symbol=None):
  assert store_method in (None, 'direct', 'default')
  assert not (store_method and export_symbol), \
      "store_method and export_symbol can not be combined"

  if minify:
    code = globals()['minify'](code, minify_obfuscate)

  # Compress the code, if desired, and convert to Base64.
  data = code.encode('utf8')
  if compress:
    data = zlib.compress(data)
    template = EXEC_TEMPLATE_COMPRESSED
  else:
    template = EXEC_TEMPLATE
  data = base64.b64encode(data).decode('ascii')

  if export_symbol:
    storemethod = STOREMETHOD_SYMBOL.format(name=name, symbol=export_symbol)
  elif store_method in ('default', None):
    storemethod = STOREMETHOD_DEFAULT.format(name=name)
  elif store_method == 'direct':
    storemethod = STOREMETHOD_DIRECT.format(name=name)

  lines = '\\\n'.join(textwrap.wrap(data, width=line_width))
  return template.format(name=name, blobdata=lines, storemethod=storemethod)

@click.command()
@click.argument('sourcefile', type=click.File('r'))
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
@click.option('-c', '--compress', is_flag=True)
@click.option('-m', '--minify', is_flag=True)
@click.option('-O', '--minify-obfuscate', is_flag=True)
@click.option('-w', '--line-width', type=int, default=79)
@click.option('-s', '--store-method', type=click.Choice(['direct', 'default']))
@click.option('-e', '--export-symbol')
def main(file, output, compress, minify, minify_obfuscate, line_width,
    store_method, export_symbol):
  """
  Create a base64 encoded, optionally compressed and minified blob of a
  Python source file. Note that the -O,--minify-obfuscate option does not
  always work (eg. when using a variable 'file' in a Python 3.6 source
  file) due to incompatibilities in pyminifier.
  """

  if export_symbol:
    if store_method:
      parser.error('--export-symbol and --store-method can not be combined')

  name = os.path.splitext(os.path.basename(file.name))[0]
  output.write(blobbify(name=name, code=file.read(), minify=minify,
      compress=compress, minify_obfuscate=minify_obfuscate,
      line_width=line_width, store_method=store_method,
      export_symbol=export_symbol))

exports = blobbify

if require.main == module:
  sys.exit(main())
