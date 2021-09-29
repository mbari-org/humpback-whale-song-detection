#!/usr/bin/env python3

import time
from argparse import ArgumentParser, RawTextHelpFormatter
from typing import Union

import numpy as np

from hwsd.file_helper import FileHelper, DEFAULT_AUDIO_BASE_DIR, DEFAULT_SCORE_BASE_DIR
from hwsd.misc import elapsed_end
from hwsd.model_helper import ModelHelper


def get_chunk_label(tot_minutes: int) -> str:
    hours, minutes = divmod(tot_minutes, 60)
    return f"{hours:02}h:{minutes:02}m"


def apply_model_day(
    fh: FileHelper,
    year: int,
    month: int,
    day: int,
    at_hour: int = 0,
    hours: int = 24,
    model_minutes: int = 10,
    mh: Union[None, ModelHelper] = None,
) -> None:
    """
    Applies the model on a specified audio segment.
    Updates the score file corresponding to the complete year-month-day,
    of course while retaining any already stored scores outside on the segment.
    """

    if fh.sample_rate != 10_000:
        # A previous version handled this case by doing the resampling (using librosa).
        # but later on we opted to generate the 10kHz files beforehand (using sox).
        print("ERROR: Input signal expected at 10kHz")
        return

    program_started = time.time()
    line = f"{year:04}-{month:02}-{day:02} @ {at_hour:02}h dur={hours:02}h model_minutes={model_minutes}"
    print(f"### starting apply_model_day: {line}")

    if mh is None:
        mh = ModelHelper()
        model_load_started = time.time()
        mh.load_model()
        print(f"    >> model loaded in {elapsed_end(model_load_started)}")

    print("\n==> Selecting day")
    if not fh.select_day(year, month, day):
        return

    hours = min(hours, 24 - at_hour)
    print(f"\n==> Loading segment (hours={hours})")
    segment_load_started = time.time()
    psound_segment, psound_segment_seconds = fh.load_audio_segment(
        at_hour=at_hour,
        hours=hours,
    )
    print(f"    >> {hours}-hour segment loaded in {elapsed_end(segment_load_started)}")

    # At 10 kHz, this is the nominal size in samples of our desired
    # segment when resampled:
    psound_segment_samples_at_10k = 10_000 * psound_segment_seconds
    print(f"    psound_segment_samples_at_10k = {psound_segment_samples_at_10k:,}")

    # Get score array for the whole day:
    day_scores = fh.load_day_scores()

    # initial offset to update day_scores below:
    day_scores_offset_seconds = at_hour * 60 * 60

    print("\n==> Starting model application ...")
    model_application_started = time.time()
    to_model_in_seconds = 60 * model_minutes
    to_model_in_samples = 10_000 * to_model_in_seconds
    chunk_minutes = 60 * at_hour
    for start in range(0, len(psound_segment), to_model_in_samples):
        chunk_label = get_chunk_label(chunk_minutes)
        print(
            f"\n==> Applying model on {model_minutes}-min chunk starting @ {chunk_label} ..."
        )
        model_chunk_started = time.time()
        psound_chunk = psound_segment[start : start + to_model_in_samples]
        chunk_score_values = mh.apply_model(psound_chunk)
        print(f"    >> model applied on chunk in {elapsed_end(model_chunk_started)}")
        print(f"     chunk_score_values: {len(chunk_score_values):,}")
        if len(chunk_score_values) > to_model_in_seconds:
            chunk_score_values = chunk_score_values[:to_model_in_seconds]

        # update day_scores with to_model_in_seconds values:
        np.put(
            day_scores,
            range(
                day_scores_offset_seconds,
                day_scores_offset_seconds + to_model_in_seconds,
            ),
            chunk_score_values,
        )

        # advance scores offset for next cycle:
        day_scores_offset_seconds += model_minutes * 60

        # advance chunk_minutes for next cycle:
        chunk_minutes += model_minutes

    print(
        f"\n>> model applied on complete {hours}-hour segment in {elapsed_end(model_application_started)}\n"
    )

    fh.save_day_scores(day_scores)

    print(f"\n>> complete apply_model_day: {line} in {elapsed_end(program_started)}\n")


def parse_arguments():
    description = "Applies Google Humpback Whale Model on a Pacific Sound day file."
    example = """
Examples:
    hwsd/apply_model_day.py --year=2016 --month=12 --day=21
       will process a complete day.
                         
    hwsd/apply_model_day.py --year=2016 --month=12 --day=21 --at_hour=10 --hours=4
       will only process the indicated segment within a day.    
    """

    parser = ArgumentParser(
        description=description, epilog=example, formatter_class=RawTextHelpFormatter
    )

    parser.add_argument(
        "--audio-base-dir",
        type=str,
        metavar="dir",
        default=DEFAULT_AUDIO_BASE_DIR,
        help=f"Audio base directory. By default, {DEFAULT_AUDIO_BASE_DIR}.",
    )
    parser.add_argument(
        "--score-base-dir",
        type=str,
        metavar="dir",
        default=DEFAULT_SCORE_BASE_DIR,
        help=f"Score base directory. By default, {DEFAULT_SCORE_BASE_DIR}.",
    )

    parser.add_argument("--year", type=int, metavar="YYYY", required=True, help="Year")
    parser.add_argument("--month", type=int, metavar="M", required=True, help="Month")
    parser.add_argument("--day", type=int, metavar="D", required=True, help="Day")
    parser.add_argument(
        "--at-hour",
        type=int,
        metavar="H",
        default=0,
        help="Hour at which to start applying the model. By default, 0.",
    )
    parser.add_argument(
        "--hours",
        type=int,
        metavar="h",
        default=24,
        help="Number of hours to process. "
        "By default, the remaining hours for the day per `at-hour`.",
    )
    parser.add_argument(
        "--model-minutes",
        type=int,
        metavar="m",
        default=10,
        help="Length in minutes of signal to give the model at a time. By default, 10.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    opts = parse_arguments()
    fh = FileHelper(opts.audio_base_dir, opts.score_base_dir)
    apply_model_day(
        fh,
        opts.year,
        opts.month,
        opts.day,
        opts.at_hour,
        opts.hours,
        opts.model_minutes,
    )
