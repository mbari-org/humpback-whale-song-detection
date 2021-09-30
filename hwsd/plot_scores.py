#!/usr/bin/env python3
"""
Script to run plot_scores_day as needed.
No options from command line; adjust the script itself.
"""

from calendar import monthrange

from hwsd.file_helper import FileHelper
from hwsd.plot_scores_day import plot_segment


def main() -> None:
    "Main program."

    # Using defaults on gizo:
    file_helper = FileHelper()

    # adjust as needed:
    years_months = [
        (2018, [11, 12]),
        (2019, range(1, 12 + 1)),
        (2020, range(1, 10 + 1)),
    ]

    for year, months in years_months:
        print(f"\n *** YEAR {year:04} ***")
        for month in months:
            print(f"\n *** MONTH {year:04}-{month:02} ***")
            num_days = monthrange(year, month)[1]
            for day in range(1, num_days + 1):
                print(f"\n *** DAY {year:04}-{month:02}-{day:02} ***")
                plot_segment(file_helper, year, month, day)


if __name__ == "__main__":
    main()
