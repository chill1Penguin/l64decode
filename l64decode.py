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

_lut = [ 0x14, 0x0B, 0x09, 0x02, 0x08, 0x03, 0x03, 0x03 ]

def DecodeFile(src, dest, overwrite):
    print('Processing ' + src + '...')
    try:
        with open(src, 'rb') as f:
            srcFile = bytearray(f.read())
    except FileNotFoundError:
        print('File "' + src + '" not found.')
        return
    except:
        print('Failed to read file "' + src + '".')
        return

    if len(srcFile) >= 4 and srcFile[0] == 0x1B and srcFile[1] == 0x4C and srcFile[2] == 0x4A and srcFile[3] == 0x03:
        srcFile[3] = 2
    else:
        print('File "' + src + '" contains an invalid .l64 header.')
        return

    for i in range(4, len(srcFile)):
        srcFile[i] = (srcFile[i] + (_lut[i & 0x07] + i)) & 0xFF

    if os.path.isdir(dest):
        fullDestPath = os.path.join(dest, os.path.splitext(os.path.split(src)[1])[0] + '.lua')
    else:
        fullDestPath = dest

    try:
        with open(fullDestPath, 'wb' if overwrite else 'xb') as f:
            f.write(srcFile)
    except FileExistsError:
        print('The file "' + fullDestPath + '" already exists. To overwrite, please specify the -o command line argument.')
        return
    except:
        print('Could not open file "' + fullDestPath + '" for writing.')
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
