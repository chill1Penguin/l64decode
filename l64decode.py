#!/usr/bin/python3
#
# The MIT License (MIT)
#
# Copyright (c) 2020 Andrew Hirst
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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

from pprint import pprint

import argparse
import os

_lut3 = [ 0x14, 0x0B, 0x09, 0x02, 0x08, 0x03, 0x03, 0x03 ]
_lut4 = [ 0x06, 0x10, 0x0C, 0x02, 0x09, 0x03, 0x04, 0x04, 0x09, 0x05, 0x04, 0x02, 0x05, 0x08, 0x09, 0x15 ]

def DecodeFile(src, dest, overwrite):
    print('Processing {0}...'.format(src))
    try:
        with open(src, 'rb') as f:
            srcFile = bytearray(f.read())
    except FileNotFoundError:
        print('File "{0}" not found.'.format(src))
        return
    except:
        print('Failed to read file "{0}".'.format(src))
        return

    if len(srcFile) < 4 or srcFile[0] != 0x1B or srcFile[1] != 0x4C or srcFile[2] != 0x4A:
        print('File "{0}" contains an invalid .l64 header.'.format(src))
        return

    if srcFile[3] == 0x03:
        srcFile[3] = 2
        for i in range(4, len(srcFile)):
            srcFile[i] = (srcFile[i] + (_lut3[i & 0x07] + i)) & 0xFF
    elif srcFile[3] == 0x04:
        srcFile[3] = 2
        for i in range(4, len(srcFile)):
            srcFile[i] = (srcFile[i] + (_lut4[i & 0x0F] + i)) & 0xFF
    else:
        print('This decoder cannot decode "{0}". The file is encoded using version {1} which is not supported.'.format(src, srcfile[3]))
        return

    if os.path.isdir(dest):
        fullDestPath = os.path.join(dest, os.path.splitext(os.path.split(src)[1])[0] + '.lua')
    else:
        fullDestPath = dest

    try:
        with open(fullDestPath, 'wb' if overwrite else 'xb') as f:
            f.write(srcFile)
    except FileExistsError:
        print('The file "{0}" already exists. To overwrite, please specify the -o command line argument.'.format(fullDestPath))
        return
    except:
        print('Could not open file "{0}" for writing.'.format(fullDestPath))
        return

def DecodeFolder(src, subpath, dest, recursive, overwrite):
    srcDir = os.path.join(src, subpath)
    destDir = os.path.join(dest, subpath)
    os.makedirs(destDir, exist_ok=True)
    with os.scandir(srcDir) as it:
        for f in it:
            if f.name.endswith('.l64'):
                DecodeFile(os.path.join(srcDir, f.name), destDir, overwrite)
            elif recursive and f.is_dir():
                DecodeFolder(src, os.path.join(subpath, f.name), dest, recursive, overwrite)

parser = argparse.ArgumentParser(prog='l64decode.py')
parser.add_argument('input', help='The input filename or folder. If a folder is specified, the program decodes all .l64 file in the folder.')
parser.add_argument('output', help='The output filename or folder.')
parser.add_argument('-r', '--recursive', action='store_true', help='Recursively decode .l64 files the specified folder and all subdirectories.')
parser.add_argument('-o', '--overwrite', action='store_true', help='Overwrite destination file(s) if they already exist.')

args = parser.parse_args()

if os.path.isfile(args.input):
    DecodeFile(args.input, args.output, args.overwrite)
else:
    DecodeFolder(args.input, '', args.output, args.recursive, args.overwrite)

print('Done!')
