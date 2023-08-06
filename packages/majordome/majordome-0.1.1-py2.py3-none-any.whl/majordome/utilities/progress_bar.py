# -*- coding: utf-8 -*-
from time import perf_counter
import sys


class ProgressBar:
    """ Simple progress bar with duration estimation for simulation tracking.
    
    This basic progress bar display process status advance on the screen and
    also total run-time and e.t.a (estimated time of arrival). It is extremely
    minimalist and cannot handle overflow, thus it is up to the user to ensure
    terminal will be at least 79 characters wide.

    Parameters
    ----------
    ncols: int = 40
        Number of columns used for bar tracing.
    marker: str = "█"
        Single character used for filling up the bar.
    """
    def __init__(self, ncols: int = 40, marker: str = "█") -> None:
        self._nc = ncols + 1.0e-06
        self._mk = marker[:1]
        self._t0 = perf_counter()

        base = ("\r|{{0:{ncols}s}}| {{1:3.0f}}% "
                "[run {{2:.2e}}s | eta {{3:.2e}}s]")
        self._txt = base.format(ncols=ncols)

    def update(self, frac: float) -> None:
        """ Update fraction of bar filling.
        
        Parameters
        ----------
        frac: float
            Current status of filling to apply to the bar.
        """
        stat = int(self._nc * frac)

        mark = self._mk * stat
        fill = 100 * stat / self._nc

        run = perf_counter() - self._t0
        eta = float("nan") if fill <= 0.0 else 100 * run / fill - run

        sys.stdout.write(self._txt.format(mark, fill, run, eta))
        sys.stdout.flush()
