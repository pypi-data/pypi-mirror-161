==================================
 pyUTok - Unique TOKens in python
==================================

Inspired by a tool I can not find anymore on the internet: utok 1.5. I
use it to clean up path settings in large shell script configuration
setups.

``utok`` has the following options:

usage:
  utok [-h] [--delimiter DELIMITER] [--delete-list DELETE_LIST] [--version] tokens [tokens ...]

positional arguments:
  tokens

options:
  -h, --help            show this help message and exit
  --delimiter DELIMITER, -s DELIMITER
                        Allows one to change the delimiter. If you use csh you might want to set your path with something like: set path = (`utok -s \ /usr/local/bin $path`) (default: :)
  --delete-list DELETE_LIST, -d DELETE_LIST
                        Allows one to remove tokens from a list, to remove /usr/sbin and . from a path in Bourne Shell one might use: PATH=`utok $PATH -d .:/usr/sbin` (default: None)
  --version, -V         show program's version number and exit

Homepage
========

`<https://python.höllmanns.de/utok/>`_

Availability
============

The latest version should be available at my `GitLab
<https://gitlab.com/berhoel/python/pyutok>`_ repository, the package
is avaliable at `pypi <https://pypi.org/project/pyutok/>`_ via ``pip
install pyutok``.

Description
===========

utok, Unique TOKens, takes a list of arguments with delimiters and
reject all duplicate entries. Here is a example using ``MANPATH``:

.. code-block:: shell

    $ echo $MANPATH
    /usr/man:/usr/local/man
    $ MANPATH=`utok /home/local/man /usr/local/man $MANPATH /usr/openwin/man`
    $ export MANPATH
    $ echo $MANPATH
    /home/local/man:/usr/local/man:/usr/man:/usr/openwin/man


Even though ``/usr/local/man`` was included a second time it is only
in the ``MANPATH`` once, though it is now before the ``/usr/man``
entry instead of after it.

This version adds the ``-d`` option to remove tokens. To remove ``.``
from the ``PATH`` one would do the following:

.. code-block:: shell

    $ echo $PATH
    /usr/local/bin:.:/usr/bin:/usr/sbin
    $ PATH=`utok -d .: $PATH`
    $ echo PATH
    /usr/local/bin:/usr/bin:/usr/sbin
    $ export PATH


Requested Features
==================

* Have a way to to push an element further back in the path. A work
  around of this would be be something like:

  .. code-block:: shell

    utok `utok a:b:c:d -d b` b

  which returns: ``a:c:d:b``

* Have a way to include multiple ``-s`` options.

Feedback
========

Comments or bug reports/fixes go to Berthold Höllmann <berhoel@gmail.com>.

Copyright © 2020 Berthold Höllmann <berhoel@gmail.com>

Original C version:
Copyright © 1998 Sven Heinicke <sven@zen.org>

..
  Local Variables:
  mode: rst
  mmm-classes: (jinja2)
  End:
