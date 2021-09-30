#!/usr/bin/env python3
"""
A main script to run apply_model_day on given time intervals.
See USAGE.
"""

import sys
import time
from typing import List

from hwsd.apply_model_day import apply_model_day
from hwsd.file_helper import FileHelper, DEFAULT_SCORE_BASE_DIR
from hwsd.misc import elapsed_end, parse_days
from hwsd.model_helper import ModelHelper

# Adjust the following depending on cpu/ram resources available to apply the model:
HOURS_PER_CALL = 3  # how many hours of audio to keep in memory
MODEL_MINUTES = 60  # Size of audio to pass to the model.
# The longer this is the more resources used by the model.


USAGE = """
hwsd/apply_model.py: A main script to apply the model on given time intervals.

Usage:
    $ hwsd/apply_model.py time-interval ...
  where each time interval must be of the form
  'yearRange/monthRange/dayRange' or 'yearRange/monthRange'
  with each __Range either a single number or a hyphen-separated range with inclusive limits.
  If omitted, the day range will be "1-31".

Examples:
    $ hwsd/apply_model.py "2020/10-12" "2021/1-3"
    $ hwsd/apply_model.py "2021/9/1-21"

Some of our runs on gizo were like this (two concurrent jobs to process Jan–Aug'2021):
    $ source virtenv/bin/activate
    $ nohup python3 -u hwsd/apply_model.py "2021/1-4" > nohup-2021--1-4.out &
    $ nohup python3 -u hwsd/apply_model.py "2021/5-8" > nohup-2021--5-8.out &
"""


def main(intervals: List[str]) -> None:
    """
    Applies the model on the given intervals.
    """

    years_months_days = parse_days(*intervals)

    print(f"\nSTARTING apply_model with intervals={intervals}")
    program_started = time.time()

    # With 10kHz already pre-generated:
    audio_base_dir = "/PAM_Analysis/GoogleHumpbackModel/decimated_10kHz"
    # (The default in file_helper is to read from the 16kHz data.)

    model_helper = ModelHelper()
    model_helper.load_model()

    for year, month, day in years_months_days:
        print(f"\n*** DAY {year:04}-{month:02}-{day:02} ***")
        for at_hour in range(0, 24, HOURS_PER_CALL):
            apply_model_day(
                FileHelper(audio_base_dir, DEFAULT_SCORE_BASE_DIR),
                model_helper,
                year,
                month,
                day,
                at_hour=at_hour,
                hours=HOURS_PER_CALL,
                model_minutes=MODEL_MINUTES,
            )

    print(f"\n>> complete apply_model in {elapsed_end(program_started)}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1:])
    else:
        print(USAGE)
