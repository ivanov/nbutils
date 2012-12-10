import os
import numpy.testing as npt
import shutil
from IPython.nbformat.current import reads, writes

# XXX: make a temporary directory to keep all of this stuff in, and delete it
# after running the tests, so it doesn't become too much of a mess

def test_error_saving():
    "save portions of notebooks thave an error in them"
    try:
        os.remove('test_error_saving0000_error.npz')
    except OSError:
        pass
    os.system('nbexplode -q test_error_saving.ipynb')
    os.system('nbrun -q -s test_error_saving0000.ipynb')
    if not os.path.exists('test_error_saving0000_error.npz'):
        raise UserError("didn't save file on errror")

def test_running_renamed():
    "running a renamed notebook file renames its internal metadata"
    newname = 'renamed_notebook'
    shutil.copy('simple_notebook.ipynb', newname + '.ipynb')
    with file(newname + '.ipynb') as nbf:
        nb = reads(nbf.read(), 'ipynb')
        npt.assert_(nb.metadata.name != newname)
    os.system('nbrun -q ' + newname + '.ipynb')
    with file(newname + '.ipynb') as nbf:
        nb = reads(nbf.read(), 'ipynb')
        npt.assert_(nb.metadata.name == newname)
    os.remove(newname + '.ipynb')
