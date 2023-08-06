#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""Python interpretation of utok.
"""
from __future__ import division, print_function, absolute_import, unicode_literals

# Standard libraries.
import argparse
import itertools

__date__ = "2022/08/02 16:06:04 hoel"
__author__ = "Berthold Höllmann"
__copyright__ = "Copyright © 2020 by Berthold Höllmann"
__credits__ = ["Berthold Höllmann"]
__maintainer__ = "Berthold Höllmann"
__email__ = "berhoel@gmail.com"

__version__ = "1.1.3"

PARSER = argparse.ArgumentParser(
    prog="utok", formatter_class=argparse.ArgumentDefaultsHelpFormatter
)
PARSER.add_argument(
    "--delimiter",
    "-s",
    type=str,
    default=":",
    help="""
Allows one to change the delimiter. If you use csh you might want to set your
path with something like: set path = (`utok -s \\  /usr/local/bin $path`) """,
)
PARSER.add_argument(
    "--delete-list",
    "-d",
    type=str,
    help="""\
Allows one to remove tokens from a list, to remove /usr/sbin and . from a path \
in Bourne Shell one might use: PATH=`utok $PATH -d .:/usr/sbin` 
""",
)
PARSER.add_argument("tokens", nargs="+", type=str)
PARSER.add_argument(
    "--version",
    "-V",
    action="version",
    version="%(prog)s {version}".format(version=__version__),
)


def utok(tokens, delimiter=":", delete_list=""):
    """Process token.

The token chains are splitted at `delimiter` into tokens, and then
the tokens joined again using `delimiter` after removing double
tokens.

Args:
    tokens (list[str]): List of strings representing tokens chains.
    delimiter (str): Character used to construct token chains.
    delete_list (str): Chain of tokens to be deleted from `tokens`.

Returns:
    str: Token chain with all tokens.
"""
    res = []
    _delete_list = delete_list.split(delimiter) if delete_list else []
    for t in itertools.chain(*(j.split(delimiter) for j in tokens)):
        if t not in res and t not in _delete_list:
            res.append(t)
    return delimiter.join(res)


def prog():
    """``utok [-s delimiter] [ tokens...  [-d delete-list ] tokens...]``

Processing the command line arguments and executing the joining of
the elements.

Returns:
    str: Newly constructed string.
"""
    args = PARSER.parse_args()

    return utok(args.tokens, delimiter=args.delimiter, delete_list=args.delete_list)


def main():
    """Main entry point for command line.

    Printing the result string.
    """
    print(prog())


if __name__ == "__main__":
    print(prog())

# Local Variables:
# mode: python
# compile-command: "poetry run tox"
# time-stamp-pattern: "30/__date__ = \"%:y/%02m/%02d %02H:%02M:%02S %u\""
# End:
