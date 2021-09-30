#!/usr/bin/env python3
"""
Main script to run apply_model_day as needed.
No options from command line; adjust the script itself.
     $ nohup python3 -u hwsd/apply_model.py &
     $ tail -f nohup.out
"""

import time

from hwsd import file_helper
from hwsd.apply_model_day import apply_model_day
from hwsd.misc import elapsed_end, parse_days
from hwsd.model_helper import ModelHelper


def main() -> None:
    "Main program."

    # Adjust as needed (the intervals are adjusted by parse_days):
    intervals = ["2018/11-12/1-31", "2019/1-12/1-31", "2020/1-10/1-31"]
    # intervals = ["2018/12/1-15"]
    # intervals = ["2018/12/16-31"]
    years_months_days = parse_days(*intervals)

    print(f"\nSTARTING apply_model with intervals={intervals}")
    program_started = time.time()

    # Adjust the following depending on cpu/ram resources available
    # to apply the model:
    hours_per_call = 3  # how many hours of audio to keep in memory
    model_minutes = 60  # Size of audio to pass to the model.
    # The longer this is the more resources used by the model.

    # With 10kHz already pre-generated:
    audio_base_dir = "/PAM_Analysis/GoogleHumpbackModel/decimated_10kHz"
    # (The default in file_helper is to read from the 16kHz data.)

    score_base_dir = file_helper.DEFAULT_SCORE_BASE_DIR

    model_helper = ModelHelper()
    model_helper.load_model()

    for year, month, day in years_months_days:
        print(f"\n*** DAY {year:04}-{month:02}-{day:02} ***")
        for at_hour in range(0, 24, hours_per_call):
            apply_model_day(
                file_helper.FileHelper(audio_base_dir, score_base_dir),
                model_helper,
                year,
                month,
                day,
                at_hour=at_hour,
                hours=hours_per_call,
                model_minutes=model_minutes,
            )

    print(f"\n>> complete apply_model in {elapsed_end(program_started)}\n")


if __name__ == "__main__":
    main()
