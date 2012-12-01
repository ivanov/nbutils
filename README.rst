Notebook utilities
==================

Here are some utilities that help manage .ipynb files.

* nbcat : concatenate multiple notebook files
* nbstrip : strips the output of code cells, writes to stdout or --in-place
* nbrun : runs a notebook, and saves results back into it.
* nbsimplecheck : runs a notebook and reports exceptions.


Parametrized notebooks
----------------------
nbexplode : takes a notebook where the first cell looks something like this::

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

By default, the output of this command is just the filenames of the created
notebooks, this way you can do something like this::

    nbexplode params.ipynb | parallel nbrun

In this example, we used `GNU parallel
<http://www.gnu.org/software/parallel/>`_ to run a bunch of notebooks at the
same time.
