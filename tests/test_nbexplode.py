import os
import glob

prefix = 'delete_me_'
def setup():
    for x in glob.glob(prefix + '*'):
        os.remove(x)

def teardown():
    import glob
    for x in glob.glob(prefix + '*'):
        os.remove(x)


def test_non_iterable_params():
    "running a notebook with parameters that aren't iterable still works"
    os.system('nbexplode -q -p delete_me_ noniterable.ipynb')
    if not os.path.exists(prefix + 'noniterable0000.ipynb'):
        raise UserError("Non-iterable parameters not working")
