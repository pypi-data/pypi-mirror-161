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
        filename_all=None,
        filename_last=None,
    ):
        self._iterable = iterable
        self._retlist = []
        self._quiet = quiet
        self._gzip = gzip
        if filename_all is not None:
            self._filename_all = filename_all
        else:
            self._filename_all = (
                directory
                + f"/breakable-list-{os.getpid()}-all.pkl"
                + (".gz" if gzip else "")
            )
        if filename_last is not None:
            self._filename_last = filename_last
        else:
            self._filename_last = (
                directory
                + f"/breakable-list-{os.getpid()}-last.pkl"
                + (".gz" if gzip else "")
            )

    def handler_sig(self, sig, frame):
        if not self._retlist:
            if not self._quiet:
                print(
                    f"Signal {'SIGUSR1' if sig==signal.SIGUSR1 else 'SIGUSR2'} ignored: the list is still empty",
                    file=sys.stderr,
                )
            return None
        if sig == signal.SIGUSR1:
            tosave = self._retlist[-1]
            filename = self._filename_last
            saveall = False
        elif sig == signal.SIGUSR2:
            tosave = self._retlist
            filename = self._filename_all
            saveall = True
        else:
            raise Exception
        if self._gzip:
            fileobj = gzip.open(filename, "wb")
        else:
            fileobj = open(filename, "wb")
        pickle.dump(tosave, fileobj)
        fileobj.close()
        if not self._quiet:
            if saveall:
                print(
                    f"Current list (length={len(self._retlist)}) saved in {filename}",
                    file=sys.stderr,
                )
            else:
                print(
                    f"Last item (item {len(self._retlist)}) saved in {filename}",
                    file=sys.stderr,
                )
            print(
                f"\tTo load this, use `pickle.load({'gzip.' if self._gzip else ''}open({filename!r}))`.",
                file=sys.stderr,
            )
        return None

    def build(self):
        try:
            for value in self._iterable:
                self._retlist.append(value)
        except KeyboardInterrupt:
            pass
        return self._retlist
