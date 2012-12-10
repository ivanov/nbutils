import os
import numpy.testing as npt
import shutil
from IPython.nbformat.current import reads, writes

def test_running_renamed():
    "running a renamed notebook file renames its internal metadata"
    newname = 'renamed_notebook'
    shutil.copy('simple_notebook.ipynb', newname + '.ipynb')
    with file(newname + '.ipynb') as nbf:
        nb = reads(nbf.read(), 'ipynb')
        npt.assert_(nb.metadata.name != newname)
    os.system('nbrun ' + newname + '.ipynb')
    with file(newname + '.ipynb') as nbf:
        nb = reads(nbf.read(), 'ipynb')
        npt.assert_(nb.metadata.name == newname)
    os.remove(newname + '.ipynb')
