#!/usr/bin/env python3
"""calc.py - the small pure-arithmetic helpers stats.py, dcf.py and holdings.py share: statistics over lists,
percentiles, growth, drawdown, beta, and the number formats the --md tables print. No I/O, no database."""
import math


def clamp(x, lo, hi):
    return max(lo, min(hi, x))


def mean(xs):
    xs = list(xs)
    return sum(xs) / len(xs) if xs else None


def stdev(xs):
    """Sample standard deviation; None below two points."""
    xs = list(xs)
    n = len(xs)
    if n < 2:
        return None
    m = sum(xs) / n
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (n - 1))


def percentile(xs, p):
    """Linear-interpolated percentile (p in 0..100) of a list; None when empty."""
    xs = sorted(xs)
    if not xs:
        return None
    k = (len(xs) - 1) * p / 100.0
    lo, hi = int(math.floor(k)), int(math.ceil(k))
    if lo == hi:
        return xs[lo]
    return xs[lo] + (xs[hi] - xs[lo]) * (k - lo)


def log_returns(levels):
    return [math.log(b / a) for a, b in zip(levels, levels[1:]) if a and b and a > 0 and b > 0]


def cagr(start, end, years):
    """Annualised growth from start to end over `years`; None when it cannot be taken."""
    if not start or start <= 0 or end is None or end <= 0 or years <= 0:
        return None
    return (end / start) ** (1.0 / years) - 1


def max_drawdown(levels):
    """Deepest peak-to-trough fall as a negative fraction (0 when the series never falls)."""
    peak, worst = None, 0.0
    for x in levels:
        if peak is None or x > peak:
            peak = x
        if peak:
            worst = min(worst, x / peak - 1)
    return worst


def beta_corr(r, m):
    """Slope and correlation of r on m (paired return lists); (None, None) below three pairs or flat m."""
    n = min(len(r), len(m))
    if n < 3:
        return None, None
    r, m = r[:n], m[:n]
    mr, mm = sum(r) / n, sum(m) / n
    cov = sum((a - mr) * (b - mm) for a, b in zip(r, m))
    var_m = sum((b - mm) ** 2 for b in m)
    var_r = sum((a - mr) ** 2 for a in r)
    if var_m <= 0:
        return None, None
    corr = cov / math.sqrt(var_m * var_r) if var_r > 0 else None
    return cov / var_m, corr


# --- formats for --md ---------------------------------------------------------------------------
def pct(x, places=1):
    return "" if x is None else "%+.*f%%" % (places, x * 100)


def pct_plain(x, places=1):
    return "" if x is None else "%.*f%%" % (places, x * 100)


def money(x, places=2):
    return "" if x is None else "{:,.{p}f}".format(x, p=places)


def num(x, places=2):
    return "" if x is None else "%.*f" % (places, x)
