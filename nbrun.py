#!/usr/bin/env python
# from https://gist.github.com/2620735
"""
simple example script for running and testing notebooks.

Usage: `ipnbdoctest.py foo.ipynb [bar.ipynb [...]]`

Each cell is submitted to the kernel, and the outputs are compared with those stored in the notebook.
"""

import os,sys,time
import base64
import re

from collections import defaultdict
from Queue import Empty

from IPython.zmq.blockingkernelmanager import BlockingKernelManager
from IPython.nbformat.current import reads, writes, NotebookNode

import logging
logging.basicConfig(format='%(message)s')
log = logging.getLogger(os.path.basename(__file__))

def compare_png(a64, b64):
    """compare two b64 PNGs (incomplete)"""
    try:
        import Image
    except ImportError:
        pass
    adata = base64.decodestring(a64)
    bdata = base64.decodestring(b64)
    return True

def sanitize(s):
    """sanitize a string for comparison.
    
    fix universal newlines, strip trailing newlines, and normalize likely random values (memory addresses and UUIDs)
    """
    # normalize newline:
    s = s.replace('\r\n', '\n')
    
    # ignore trailing newlines (but not space)
    s = s.rstrip('\n')
    
    # normalize hex addresses:
    s = re.sub(r'0x[a-f0-9]+', '0xFFFFFFFF', s)
    
    # normalize UUIDs:
    s = re.sub(r'[a-f0-9]{8}(\-[a-f0-9]{4}){3}\-[a-f0-9]{12}', 'U-U-I-D', s)
    
    return s


def consolidate_outputs(outputs):
    """consolidate outputs into a summary dict (incomplete)"""
    data = defaultdict(list)
    data['stdout'] = ''
    data['stderr'] = ''
    
    for out in outputs:
        if out.type == 'stream':
            data[out.stream] += out.text
        elif out.type == 'pyerr':
            data['pyerr'] = dict(ename=out.ename, evalue=out.evalue)
        else:
            for key in ('png', 'svg', 'latex', 'html', 'javascript', 'text', 'jpeg',):
                if key in out:
                    data[key].append(out[key])
    return data


def compare_outputs(test, ref, skip_compare=('png', 'traceback', 'latex', 'prompt_number')):
    for key in ref:
        if key not in test:
            log.info("missing key: %s != %s" % (test.keys(), ref.keys()))
            return False
        elif key not in skip_compare and sanitize(test[key]) != sanitize(ref[key]):
            log.info("mismatch %s:" % key)
            log.info(test[key])
            log.info('  !=  ')
            log.info(ref[key])
            return False
    return True


def run_cell(km, cell):
    shell = km.shell_channel
    iopub = km.sub_channel
    # print "\n\ntesting:"
    # print cell.input
    shell.execute(cell.input)
    # wait for finish, maximum 20s
    shell.get_msg(timeout=20)
    outs = []
    
    while True:
        try:
            msg = iopub.get_msg(timeout=0.2)
        except Empty:
            break
        msg_type = msg['msg_type']
        if msg_type in ('status', 'pyin'):
            continue
        elif msg_type == 'clear_output':
            outs = []
            continue
        
        content = msg['content']
        # print msg_type, content
        out = NotebookNode(output_type=msg_type)
        
        if msg_type == 'stream':
            out.stream = content['name']
            out.text = content['data']
        elif msg_type in ('display_data', 'pyout'):
            for mime, data in content['data'].iteritems():
                attr = mime.split('/')[-1].lower()
                # this gets most right, but fix svg+html, plain
                attr = attr.replace('+xml', '').replace('plain', 'text')
                setattr(out, attr, data)
            if msg_type == 'pyout':
                out.prompt_number = content['execution_count']
        elif msg_type == 'pyerr':
            out.ename = content['ename']
            out.evalue = content['evalue']
            out.traceback = content['traceback']
        else:
            print "unhandled iopub msg:", msg_type
        
        outs.append(out)
    return outs
    

def test_notebook(nb, halt_on_error=True):
    km = BlockingKernelManager()
    km.start_kernel(extra_arguments=['--pylab=inline'], stderr=open(os.devnull, 'w'))
    km.start_channels()
    # run %pylab inline, because some notebooks assume this
    # even though they shouldn't
    km.shell_channel.execute("pass")
    km.shell_channel.get_msg()
    while True:
        try:
            km.sub_channel.get_msg(timeout=1)
        except Empty:
            break
    
    successes = 0
    failures = 0
    errors = 0
    for ws in nb.worksheets:
        for cell in ws.cells:
            if cell.cell_type != 'code':
                continue
            try:
                outs = run_cell(km, cell)
            except Exception as e:
                print "failed to run cell:", repr(e)
                print cell.input
                errors += 1
                continue
            c = '.'
            for out in outs:
                if out['output_type'] == 'pyerr':
                    c = 'E'
            if log.getEffectiveLevel() < logging.FATAL:
                sys.stderr.write(c)
            
            failed = False
            for out, ref in zip(outs, cell.outputs):
                if not compare_outputs(out, ref):
                    failed = True
            if failed:
                failures += 1
            else:
                successes += 1
            cell.outputs = outs
            if c == 'E' and halt_on_error:
                break;

    if log.getEffectiveLevel() <= logging.WARNING:
        sys.stderr.write('\n')
    log.info("tested notebook %s" % nb.metadata.name)
    log.info("    %3i cells successfully replicated" % successes)
    if failures:
        log.info("    %3i cells mismatched output" % failures)
    if errors:
        log.info("    %3i cells failed to complete" % errors)
    km.shutdown_kernel()
    del km
    return nb

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description=__doc__)
    parser.add_argument('inputs', nargs='+', metavar='input',
                        help='Paths to notebook files.')
    parser.add_argument('-i', '--inplace', '--in-place', default=False,
            action='store_true',
            help='Overwrite existing notebook when given.')

    parser.add_argument('-p', '--prefix', default='',
                        help='Path for the destination of converted output')
    parser.add_argument('-v', '--verbose', default=False, action='store_true',
                        help='be verbose about cells comparisons')
    parser.add_argument('-q', '--quiet', default=False, action='store_true',
                        help='be verbose about cells comparisons')
    parser.add_argument('-O', '--stdout', default=False, action='store_true',
        help='Print converted output instead of sending it to a file')
    parser.add_argument('-A', '--all', default=False, action='store_true', 
            help="Try to run all cells (by default will halt on first error)")

    args = parser.parse_args()

    if args.verbose:
        log.setLevel(logging.INFO)
    if args.quiet:
        log.setLevel(logging.CRITICAL)


    for ipynb in args.inputs:
        log.info('Running '+ ipynb)
        with open(ipynb) as f:
            nb = reads(f.read(), 'json')
        output_nb = test_notebook(nb, not args.all)    
        nb_as_json = writes(output_nb, 'json')
        if args.stdout:
            sys.stdout.write(nb_as_json)
        else:
            outfile = args.prefix+ipynb
            with open(outfile, 'w') as f:
                f.write(nb_as_json)
            if log.getEffectiveLevel() < logging.CRITICAL:
                print outfile
            log.info("Wrote file " + outfile)
