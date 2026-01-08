"""
Some misc utilities.
"""

import math
import time
from calendar import monthrange


def elapsed_end(started: float) -> str:
    """See test_elapsed_end"""

    secs = time.time() - started
    seconds = math.floor(secs)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours:02}h:{minutes:02}m:{seconds:02}s"
    if minutes > 0:
        return f"{minutes:02}m:{seconds:02}s"
    return f"{secs:.1f}s"


def parse_days(*args: str) -> list[tuple[int, int, int]]:
    """See test_parse_days"""

    # pylint: disable=too-many-locals,too-many-nested-blocks

    def interval_values(spec: str, limit: int) -> list[int]:
        limits = range(1, limit + 1)
        frags = [int(x) for x in spec.split("-")]
        if not 1 <= len(frags) <= 2:
            print(f"ERROR: invalid syntax for interval: `{spec}`")
            return []
        if len(frags) == 2:
            start, end = frags
            nominal = list(range(start, end + 1))
            return [x for x in nominal if x in limits]
        return frags

    res: list[tuple[int, int, int]] = []

    # for simplicity, we assume the delimited pieces are numbers.

    for arg in args:
        parts = arg.split("/")
        if len(parts) == 3:
            yyy, mmm, ddd = parts
        elif len(parts) == 2:
            yyy, mmm = parts
            ddd = "1-31"
        else:
            print(f"ERROR: invalid syntax for parse_days: arg=`{arg}`")
            return res

        # pylint: disable=invalid-name

        for yy in yyy.split(","):
            years = interval_values(yy, 9999)
            for mm in mmm.split(","):
                months = interval_values(mm, 12)
                for dd in ddd.split(","):
                    days = interval_values(dd, 31)
                    for y in years:
                        for m in months:
                            num_days = monthrange(y, m)[1]
                            for d in days:
                                if d in range(1, num_days + 1):
                                    res.append((y, m, d))

    return res
