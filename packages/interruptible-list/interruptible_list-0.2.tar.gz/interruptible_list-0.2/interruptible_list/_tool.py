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

from ._wrapper import Wrap


def interruptible_list(
    iterable,
    *,
    gzip=True,
    save_last=False,
    save_whole=False,
    directory="/tmp",
    filename_last=None,
    filename_whole=None,
    callback_last=None,
    callback_whole=None,
    quiet=False,
):
    """
    Build a list from an iterable, allowing interruption and monitoring.

    This function act as list() constructor, and build a list from an iterable,
    except:
      - When a SIGINT (CTRL-C, KeyboardInterrupt) is received, the construction
        is stopped, and the current list is returned.
      - When a SIGUSR1 is received, the last item is pickled in a file or a callback
        is called on the last item, and the construction of the list continues.
      - When a SIGUSR2 is received, the whole current list is pickled in an file or
        a callback is called on the whole current list, and the construction of the
        list continues.

    Parameters
    ----------
    iterable : iterable
        The iterable for requesting values to build the list.
    save_last : bool, optional
        If True, the last item is pickled on USR1. If `callback_last` is set,
        the callback is called on the last item, and the result is save in place
        of the last item. Default False.
    save_whole : bool, optional
        If True, the whole current list is pickled on USR2. If `callback_whole`
        is set, the callback is called on the whole current list, and the result
        is saved in place of the whole current list. Default False.
    gzip : boolean, optional
        Enable the gzip compression for pickled files. Default: True.
    directory : str, optional
        Directory to save the pickled file (not used if filenames are provided).
    filename_last : str, optional
        Filename of file to pickle the last item on SIGUSR1 if `save_last` is
        True. If None, the filename is build from the directory, the pid, and
        the gzip compression option. Default: None.
    filename_whole : str, optional
        Filename of file to pickle the whole current list on SIGUSR2 if
        `save_whole` is True. If None, the filename is build from the directory,
        the pid, and the gzip compression option. Default: None.
    callback_last : callable, optional
        This callback is call on the last item when SIGUSR1 is received. If
        `save_last`, the result of this callback is pickled.
    callback_whole : callable, optional
        This callback is call on the whole current list when SIGUSR2 is
        received. If `save_whole`, the result of this callback is pickled.
    quiet : boolean, optional
        Quiet mode. Default: False.
    """
    wrapper = Wrap(
        iterable,
        gzip=gzip,
        directory=directory,
        filename_last=filename_last,
        filename_whole=filename_whole,
        save_last=save_last,
        save_whole=save_whole,
        callback_last=callback_last,
        callback_whole=callback_whole,
        quiet=quiet,
    )
    if not quiet:
        print("\033[0K;\r", end="", file=sys.stderr)
        print("interruptible_list running, you can use:", file=sys.stderr)
        if save_last:
            if callback_last is not None:
                print(f" - `kill -USR1 {os.getpid()}` to pickle the result of the callback on the last fetched item.", file=sys.stderr)
            else:
                print(f" - `kill -USR1 {os.getpid()}` to pickle the last fetched item.", file=sys.stderr)
        else:
            if callback_last is not None:
                print(f" - `kill -USR1 {os.getpid()}` to call the callback on the last fetched item.", file=sys.stderr)
        if save_whole:
            if callback_whole is not None:
                print(f" - `kill -USR2 {os.getpid()}` to pickle the result on the callback on the whole current list.", file=sys.stderr)
            else:
                print(f" - `kill -USR2 {os.getpid()}` to pickle the whole current list.", file=sys.stderr)
        else:
            if callback_whole is not None:
                print(f" - `kill -USR2 {os.getpid()}` to call the callback on the whole current list.", file=sys.stderr)
        print(f"  - CTRL-C (or `kill -INT {os.getpid()}`) to stop and return the current list.", file=sys.stderr)

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
        if ret:
            print("interruptible_list ended", file=sys.stderr)
        else:
            print("interruptible_list interrupted", file=sys.stderr)

    return wrapper.retlist
