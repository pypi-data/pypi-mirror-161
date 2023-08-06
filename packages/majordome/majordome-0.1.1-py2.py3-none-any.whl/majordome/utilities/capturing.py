# -*- coding: utf-8 -*-
from io import StringIO
import sys


class Capturing(list):
    """ Helper to capture excessive solver output.

    In some cases, specially when running from a notebook, it might
    be desirable to capture solver (here Ipopt specifically) output
    to later check, thus avoiding a overly long notebook.  For this
    end this context manager is to be used and redirect to a list.
    """
    def __enter__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = self._tmpout = StringIO()
        sys.stderr = self._tmperr = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._tmpout.getvalue().splitlines())
        self.extend(self._tmperr.getvalue().splitlines())
        del self._tmpout
        del self._tmperr
        sys.stdout = self._stdout
        sys.stderr = self._stderr
