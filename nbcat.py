#!/usr/bin/env python
#https://github.com/ipython/ipython-in-depth/blob/master/tools/nbmerge.py
"""
usage:

python nbmerge.py A.ipynb B.ipynb C.ipynb > merged.ipynb
"""

import io
import os
import sys
import fileinput

from IPython.nbformat import current

def merge_notebooks(filenames):
    merged = None
    for fname in filenames:
        with io.open(fname, 'r', encoding='utf-8') as f:
            nb = current.read(f, 'json')
        if merged is None:
            merged = nb
        else:
            # TODO: add an optional marker between joined notebooks
            # like an horizontal rule, for example, or some other arbitrary
            # (user specified) markdown cell)
            merged.worksheets[0].cells.extend(nb.worksheets[0].cells)
    merged.metadata.name += "_merged"
    print current.writes(merged, 'json')

if __name__ == '__main__':
    #files = [x[:-1] for x in fileinput.input()]
    # reading from stdin (needs modification)
    merge_notebooks(sys.argv[1:])

