# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['utok']
entry_points = \
{'console_scripts': ['utok = utok:main']}

setup_kwargs = {
    'name': 'pyutok',
    'version': '1.1.3',
    'description': 'Inspired by a tool I can not find anymore on the internet: utok 1.5. I use it to clean up path settings in large shell script configuration setups.',
    'long_description': "==================================\n pyUTok - Unique TOKens in python\n==================================\n\nInspired by a tool I can not find anymore on the internet: utok 1.5. I\nuse it to clean up path settings in large shell script configuration\nsetups.\n\n``utok`` has the following options:\n\nusage:\n  utok [-h] [--delimiter DELIMITER] [--delete-list DELETE_LIST] [--version] tokens [tokens ...]\n\npositional arguments:\n  tokens\n\noptions:\n  -h, --help            show this help message and exit\n  --delimiter DELIMITER, -s DELIMITER\n                        Allows one to change the delimiter. If you use csh you might want to set your path with something like: set path = (`utok -s \\ /usr/local/bin $path`) (default: :)\n  --delete-list DELETE_LIST, -d DELETE_LIST\n                        Allows one to remove tokens from a list, to remove /usr/sbin and . from a path in Bourne Shell one might use: PATH=`utok $PATH -d .:/usr/sbin` (default: None)\n  --version, -V         show program's version number and exit\n\nHomepage\n========\n\n`<https://python.höllmanns.de/utok/>`_\n\nAvailability\n============\n\nThe latest version should be available at my `GitLab\n<https://gitlab.com/berhoel/python/pyutok>`_ repository, the package\nis avaliable at `pypi <https://pypi.org/project/pyutok/>`_ via ``pip\ninstall pyutok``.\n\nDescription\n===========\n\nutok, Unique TOKens, takes a list of arguments with delimiters and\nreject all duplicate entries. Here is a example using ``MANPATH``:\n\n.. code-block:: shell\n\n    $ echo $MANPATH\n    /usr/man:/usr/local/man\n    $ MANPATH=`utok /home/local/man /usr/local/man $MANPATH /usr/openwin/man`\n    $ export MANPATH\n    $ echo $MANPATH\n    /home/local/man:/usr/local/man:/usr/man:/usr/openwin/man\n\n\nEven though ``/usr/local/man`` was included a second time it is only\nin the ``MANPATH`` once, though it is now before the ``/usr/man``\nentry instead of after it.\n\nThis version adds the ``-d`` option to remove tokens. To remove ``.``\nfrom the ``PATH`` one would do the following:\n\n.. code-block:: shell\n\n    $ echo $PATH\n    /usr/local/bin:.:/usr/bin:/usr/sbin\n    $ PATH=`utok -d .: $PATH`\n    $ echo PATH\n    /usr/local/bin:/usr/bin:/usr/sbin\n    $ export PATH\n\n\nRequested Features\n==================\n\n* Have a way to to push an element further back in the path. A work\n  around of this would be be something like:\n\n  .. code-block:: shell\n\n    utok `utok a:b:c:d -d b` b\n\n  which returns: ``a:c:d:b``\n\n* Have a way to include multiple ``-s`` options.\n\nFeedback\n========\n\nComments or bug reports/fixes go to Berthold Höllmann <berhoel@gmail.com>.\n\nCopyright © 2020 Berthold Höllmann <berhoel@gmail.com>\n\nOriginal C version:\nCopyright © 1998 Sven Heinicke <sven@zen.org>\n\n..\n  Local Variables:\n  mode: rst\n  mmm-classes: (jinja2)\n  End:\n",
    'author': 'Berthold Höllmann',
    'author_email': 'berhoel@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://python.xn--hllmanns-n4a.de/utok/',
    'py_modules': modules,
    'entry_points': entry_points,
    'python_requires': '>=3.7.2,<4.0.0',
}


setup(**setup_kwargs)
