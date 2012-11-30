#!/usr/bin/env python
# from https://gist.github.com/2620735
"""
Explode a parametrized notebook into as many notebooks as there are
combinations of parameters.

Takes a notebook where the first cell looks something like this::
    
    ## Parameters
    x = [ 1, 5, 10, 20 ]
    y = 'I love python'.split()

and creates 12 notebooks, with the first cell replaced by all combinations of
members of `x` and `y`, for example, the first notebook that will get exploded
will have this as it's first cell::

    ## Parameterized by sample.ipynb
    x = 1
    y = 'I'

and the last exploded notebook will have its first cell be::

    ## Parameterized by sample.ipynb
    x = 20 
    y = 'python'
"""

import os
import logging
import itertools
from collections import OrderedDict
from IPython.nbformat.current import reads, writes

logging.basicConfig(format='%(message)s')
log = logging.getLogger(os.path.basename(__file__))

def explode(nb, quiet=False, stdout=False):
    """
    Explode a parametrized notebook

    Parameters
    ----------
    nb : IPython Notebook object
        The parameterized notebook to be exploded
    quiet : bool (default=False)
        whether to print out filenames of the exploded notebooks
    
    
    """
    first_cell = nb.worksheets[0].cells[0]
    if not first_cell.input.lower().startswith("## parameters"):
        log.warning("no parameters found in this notebook")
        return
    params = OrderedDict()
    exec(first_cell.input, globals(), params)
    for i, p in enumerate(itertools.product(*params.values())):
        log.info("p = %s", p)
        header = "## Parameterized by %s\n" % ipynb
        assignments = []
        for k,v in zip(params.keys(), p):
            assignments.append('%s = %s #damnit' % (k,repr(v)))
        first_cell.input = header + "\n".join(assignments)

        nb_as_json = writes(nb, 'json')
        basename = ipynb.rsplit('.ipynb')[0]
        outfile = args.prefix + basename +"%04d.ipynb" % i
        with open(outfile, 'w') as f:
            f.write(nb_as_json)
        log.info('writing file...')
        if not quiet:
            print outfile

if __name__ == '__main__':
    from argparse import ArgumentParser, RawTextHelpFormatter

    parser = ArgumentParser(description=__doc__,
            formatter_class=RawTextHelpFormatter)
    parser.add_argument('inputs', nargs='+', metavar='input',
                        help='Paths to notebook files.')
    parser.add_argument('-i', '--inplace', '--in-place', default=False,
            action='store_true',
            help='Overwrite existing notebook when given.')

    parser.add_argument('-p', '--prefix', default='',
                        help='prefix for the resulting filenames')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help='Be verbose')
    parser.add_argument('-q', '--quiet', default=False, action='store_true',
                        help='Be quiet, or I shall taunt you a second time!')
    parser.add_argument('-O', '--stdout', default=False, action='store_true',
        help='Print converted output instead of sending it to a file')

    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.INFO)
    if args.quiet:
        log.setLevel(logging.CRITICAL)


    for ipynb in args.inputs:
        log.info('Exploding '+ ipynb)
        with open(ipynb) as f:
            nb = reads(f.read(), 'json')

        explode(nb, quiet=args.quiet, stdout=args.stdout)
