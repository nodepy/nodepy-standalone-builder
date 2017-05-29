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

DECODE_NONE = 'blob'
DECODE_B64 = 'b.b64decode(blob)'
DECODE_B64ZLIB = 'z.decompress(b.b64decode(blob))'

EXEC_TEMPLATE = '''
import base64 as b, types as t, zlib as z; m=t.ModuleType({name!r});
m.__file__ = __file__; blob={blobdata}
exec({decode}, vars(m)); {storemethod}
del blob, b, t, z, m;
'''

STOREMETHOD_SYMBOL = '_{name}=m;{symbol}=getattr(m,"{symbol}")'
STOREMETHOD_DIRECT = '{name}=m'

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

def mkblob(name, code, compress=False, minify=False, minify_obfuscate=False,
           line_width=79, export_symbol=None, blob=True):
  if minify:
    code = globals()['minify'](code, minify_obfuscate)

  # Compress the code, if desired, and convert to Base64.
  if not compress and not blob:
    code = code.replace('\\', '\\\\').replace('"""', '\\"\\"\\"')
  data = code.encode('utf8')
  if compress:
    data = zlib.compress(data)
    decode = DECODE_B64ZLIB
  elif blob:
    decode = DECODE_B64
  else:
    decode = DECODE_NONE
  if compress or blob:
    data = base64.b64encode(data).decode('ascii')
    lines = "b'\\" + '\\\n'.join(textwrap.wrap(data, width=line_width)) + "'"
  else:
    lines = '"""' + data.decode('utf8') + '"""'

  if export_symbol:
    storemethod = STOREMETHOD_SYMBOL.format(name=name, symbol=export_symbol)
  else:
    storemethod = STOREMETHOD_DIRECT.format(name=name)

  return EXEC_TEMPLATE.format(name=name, blobdata=lines, storemethod=storemethod, decode=decode)

@click.command()
@click.argument('sourcefile', type=click.File('r'))
@click.option('-o', '--output', type=click.File('w'), default=sys.stdout)
@click.option('-c', '--compress', is_flag=True)
@click.option('-m', '--minify', is_flag=True)
@click.option('-O', '--minify-obfuscate', is_flag=True)
@click.option('-w', '--line-width', type=int, default=79)
@click.option('-e', '--export-symbol')
def main(sourcefile, output, compress, minify, minify_obfuscate,
    line_width, export_symbol):
  """
  Create a base64 encoded, optionally compressed and minified blob of a
  Python source file. Note that the -O,--minify-obfuscate option does not
  always work (eg. when using a variable 'file' in a Python 3.6 source
  file) due to incompatibilities in pyminifier.
  """

  name = os.path.splitext(os.path.basename(sourcefile.name))[0]
  output.write(mkblob(name=name, code=sourcefile.read(), minify=minify,
      compress=compress, minify_obfuscate=minify_obfuscate,
      line_width=line_width, export_symbol=export_symbol))

exports = mkblob

if require.main == module:
  sys.exit(main())
