# Copyright 2022, Jean-Benoist Leger <jb@leger.tf>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


import os
import signal
import sys
import textwrap

from ._wrapper import Wrap


def breakable_list(
    iterable,
    *,
    gzip=True,
    directory="/tmp",
    filename_last=None,
    filename_all=None,
    quiet=False,
):
    """
    Build a list from an iterable, allowing interruption and monitoring.

    This function act as list() constructor, and build a list from an iterable,
    except:
      - When a SIGINT (CTRL-C, KeyboardInterrupt) is received, the construction
        is stopped, and the current list is returned.
      - When a SIGUSR1 is received, the last item is pickled in a file, and the
        construction of the list continues.
      - When a SIGUSR2 is received, the current list is pickled in an file, and
        the construction of the list continues.

    Parameters
    ----------
    iterable : iterable
        The iterable for requesting values to build the list.
    gzip : boolean, optional
        Enable the gzip compression for pickled files. Default: True.
    directory : str, optional
        Directory to save the pickled file (not used if filenames are provided.
    filename_last : str, optional
        Filename of file to pickle the last item on SIGUSR1. If None, the
        filename is build from the directory, the pid, and the gzip compression
        option. Default: None.
    filename_all : str, optional
        Filename of file to pickle the current list on SIGUSR2. If None, the
        filename is build from the directory, the pid, and the gzip compression
        option. Default: None.
    quiet : boolean, optional
        Quiet mode. Default: False.
    """
    wrapper = Wrap(
        iterable,
        gzip=gzip,
        directory=directory,
        filename_last=filename_last,
        filename_all=filename_all,
        quiet=quiet,
    )
    if not quiet:
        print(
            textwrap.dedent(
                f"""
                breakable_list running, you can use:
                  - `kill -USR1 {os.getpid()}` to pickle the last fetched item.
                  - `kill -USR2 {os.getpid()}` to pickle the current list.
                  - CTRL-C (or `kill -INT {os.getpid()}`) to stop and return the current list."""
            )[1:],
            file=sys.stderr,
        )

    old_usr1 = signal.signal(signal.SIGUSR1, wrapper.handler_sig)
    old_usr2 = signal.signal(signal.SIGUSR2, wrapper.handler_sig)

    try:
        ret = wrapper.build()
    except Exception as e:
        signal.signal(signal.SIGUSR1, old_usr1)
        signal.signal(signal.SIGUSR2, old_usr2)
        raise e

    signal.signal(signal.SIGUSR1, old_usr1)
    signal.signal(signal.SIGUSR2, old_usr2)
    if not quiet:
        print("breakable_list ended", file=sys.stderr)

    return ret
