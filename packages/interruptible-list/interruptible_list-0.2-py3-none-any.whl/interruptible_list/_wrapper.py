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


import gzip
import os
import pickle
import signal
import sys


class Wrap:
    def __init__(
        self,
        iterable,
        quiet=False,
        gzip=True,
        directory="/tmp",
        filename_whole=None,
        filename_last=None,
        save_whole=False,
        save_last=False,
        callback_whole=None,
        callback_last=None,
    ):
        self._iterable = iterable
        self._retlist = []
        self._quiet = quiet
        self._gzip = gzip
        self._save_whole = save_whole
        self._callback_whole = callback_whole
        if save_whole:
            if filename_whole is not None:
                self._filename_whole = filename_whole
            else:
                self._filename_whole = (
                    directory
                    + f"/breakable-list-{os.getpid()}-whole.pkl"
                    + (".gz" if gzip else "")
                )
        self._save_last = save_last
        self._callback_last = callback_last
        if save_last:
            if filename_last is not None:
                self._filename_last = filename_last
            else:
                self._filename_last = (
                    directory
                    + f"/breakable-list-{os.getpid()}-last.pkl"
                    + (".gz" if gzip else "")
                )

    def handler_sig(self, sig, _):
        if not self._retlist:
            if not self._quiet:
                print("\033[0K;\r"+
                    f"Signal {'SIGUSR1' if sig==signal.SIGUSR1 else 'SIGUSR2'} ignored: the list is still empty",
                    file=sys.stderr,
                )
            return None

        if sig == signal.SIGUSR1:
            if self._save_last:
                filename = self._filename_last
            else:
                filename = None
            if self._callback_last:
                toconsider = self._callback_last(self._retlist[-1])
                savemsg = f"Result from callback on last item (item {len(self._retlist)}) saved in {filename}"
            else:
                toconsider = self._retlist[-1]
                savemsg = f"Last item (item {len(self._retlist)}) saved in {filename}"
        elif sig == signal.SIGUSR2:
            if self._save_whole:
                filename = self._filename_whole
            else:
                filename = None
            if self._callback_whole:
                toconsider = self._callback_whole(self._retlist)
                savemsg = f"Result from callback on the whole current list (length {len(self._retlist)}) saved in {filename}"
            else:
                toconsider = self._retlist
                savemsg = f"Whole current list (length {len(self._retlist)}) saved in {filename}"
        else:
            raise Exception

        if filename is not None:
            if self._gzip:
                fileobj = gzip.open(filename, "wb")
            else:
                fileobj = open(filename, "wb")
            pickle.dump(toconsider, fileobj)
            fileobj.close()
            if not self._quiet:
                print("\033[0K;\r"+savemsg, file=sys.stderr)
                print(f"To load, use `pickle.load({'gzip.' if self._gzip else ''}open({filename!r}, {'rb'!r}))`", file=sys.stderr)
        return None

    def build(self):
        try:
            for value in self._iterable:
                self._retlist.append(value)
        except KeyboardInterrupt:
            return False
        return True

    @property
    def retlist(self):
        return self._retlist
