ipywidgetvar
===============================

vars between python and js

Installation
------------

To install use pip:

    $ pip install ipywidgetvar

For a development installation (requires [Node.js](https://nodejs.org) and [Yarn version 1](https://classic.yarnpkg.com/)),

    $ git clone https://github.com/gbrault/ipywidgetvar.git
    $ cd ipywidgetvar
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --overwrite --sys-prefix ipywidgetvar
    $ jupyter nbextension enable --py --sys-prefix ipywidgetvar

When actively developing your extension for JupyterLab, run the command:

    $ jupyter labextension develop --overwrite ipywidgetvar

Then you need to rebuild the JS when you make a code change:

    $ cd js
    $ yarn run build

You then need to refresh the JupyterLab page when your javascript changes.
