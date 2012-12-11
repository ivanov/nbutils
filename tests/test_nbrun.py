import os
import numpy.testing as npt
import shutil
import glob
from IPython.nbformat.current import reads

# XXX: make a temporary directory to keep all of this stuff in, and delete it
# after running the tests, so it doesn't become too much of a mess

prefix = 'delete_me_'
def setup():
    for x in glob.glob(prefix + '*'):
        os.remove(x)

def teardown():
    import glob
    for x in glob.glob(prefix + '*'):
        os.remove(x)

def test_error_saving():
    "save portions of notebooks thave an error in them"
    fname = 'test_error_saving'
    try:
        os.remove(prefix+fname+'0000_error.npz')
    except OSError:
        pass
    os.system('nbexplode -p %s -q %s.ipynb' % (prefix, fname))
    os.system('nbrun -q -s %s%s0000.ipynb' % (prefix, fname))
    if not os.path.exists(prefix+fname+'0000_error.npz'):
        raise UserError("didn't save file on errror")

def test_running_renamed():
    "running a renamed notebook file renames its internal metadata"
    newname = prefix+'renamed_notebook'
    shutil.copy('simple_notebook.ipynb', newname + '.ipynb')
    with file(newname + '.ipynb') as nbf:
        nb = reads(nbf.read(), 'ipynb')
        npt.assert_(nb.metadata.name != newname)
    os.system('nbrun -q ' + newname + '.ipynb')
    with file(newname + '.ipynb') as nbf:
        nb = reads(nbf.read(), 'ipynb')
        npt.assert_(nb.metadata.name == newname)


