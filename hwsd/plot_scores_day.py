#!/usr/bin/env python3

from argparse import ArgumentParser, RawTextHelpFormatter
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec

from hwsd.file_helper import FileHelper, DEFAULT_AUDIO_BASE_DIR, DEFAULT_SCORE_BASE_DIR
from hwsd.plotting import plot_spectrogram_scipy, plot_scores


def plot_results(
    scores: np.ndarray,
    signal: np.ndarray,
    sample_rate: int,
    hydrophone_sensitivity: float,
    title: Optional[str] = None,
    scores_with_dots: bool = True,
    scores_with_steps: bool = False,
    scores_med_filt_size: Optional[int] = None,
    show_plot: bool = True,
    out_image_filename: Optional[str] = None,
):
    """
    Creates a combined figure with spectrogram and score plots.
    """

    # As numpy array:
    signal = np.array(signal)

    fig = plt.figure(figsize=(24, 8))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1])

    # Plot spectrogram:
    print("    plotting spectrogram")
    plt.subplot(gs[0])
    plot_spectrogram_scipy(
        signal,
        sample_rate,
        hydrophone_sensitivity,
        title,
        with_colorbar=False,
    )

    # Plot scores:
    print("    plotting scores")
    fig.add_subplot(gs[1])
    plot_scores(
        scores,
        with_dots=scores_with_dots,
        with_steps=scores_with_steps,
        med_filt_size=scores_med_filt_size,
    )

    plt.tight_layout()

    if out_image_filename:
        print(f"Saving {out_image_filename}")
        fig.savefig(out_image_filename, dpi=120)

    if show_plot:
        plt.show()


def plot_segment(
    fh: FileHelper,
    year: int,
    month: int,
    day: int,
    at_hour: int = 0,
    at_minute: int = 0,
    hours: int = 24,
    minutes: int = 0,
    show_plot: bool = False,
):
    print("\n==> Selecting day")
    if not fh.select_day(year, month, day):
        return

    print("\n==> Loading audio segment")
    psound_segment, psound_segment_seconds = fh.load_audio_segment(
        at_hour=at_hour, at_minute=at_minute, hours=hours, minutes=minutes
    )

    scores_dest_dir = f"{fh.score_base_dir}/{year:04}/{month:02}"
    score_filename = f"{scores_dest_dir}/Scores-{year:04}{month:02}{day:02}.npy"
    print(f"\n==> Loading score segment {score_filename}")
    day_scores = np.load(score_filename)
    day_scores_offset_seconds = (at_hour * 60 + at_minute) * 60
    segment_scores = day_scores[
        day_scores_offset_seconds : day_scores_offset_seconds + psound_segment_seconds
    ]
    print(f"     segment_scores ({len(segment_scores)}) = {segment_scores}")

    if at_hour == 0 and at_minute == 0 and hours == 24 and minutes == 0:
        out_image_filename = f"{scores_dest_dir}/Scores-{year:04}{month:02}{day:02}.png"
    else:
        out_image_filename = (
            f"{scores_dest_dir}/Scores-{year:04}{month:02}{day:02}"
            + f"-at-{at_hour:02}h{at_minute:02}m-dur-{hours:02}h{minutes:02}m.png"
        )

    print(f"\n==> Plotting results -> {out_image_filename}")
    title = f"Scores for segment {year:04}-{month:02}-{day:02}"
    title += f" starting at {at_hour:02}h:{at_minute:02}m"
    title += f" with duration {hours:02}h:{minutes:02}m"

    plot_results(
        segment_scores,
        signal=psound_segment,
        sample_rate=fh.sample_rate,
        hydrophone_sensitivity=-168.8,
        title=title,
        scores_with_dots=True,
        scores_med_filt_size=25,
        show_plot=show_plot,
        out_image_filename=out_image_filename,
    )


def parse_arguments():
    description = "Plots Google Humpback Whale Model Scores."
    example = """
The base directory to read in audio files is by default {DEFAULT_AUDIO_BASE_DIR}.
The base directory for the generated score files is by default {DEFAULT_SCORE_BASE_DIR}.

Examples:
    hwsd/plot_scores_day.py --year=2016 --month=11 --day=1 --at-hour=0 --at-minute=25 --hours=0 --minutes=30
    """

    parser = ArgumentParser(
        description=description, epilog=example, formatter_class=RawTextHelpFormatter
    )

    parser.add_argument(
        "--audio-base-dir",
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
        help="Start hour for the plot. By default, 0.",
    )
    parser.add_argument(
        "--at-minute",
        type=int,
        metavar="m",
        default=0,
        help="Start minute for the plot. By default, 0.",
    )
    parser.add_argument(
        "--hours",
        type=int,
        metavar="h",
        default=24,
        help="Number of hours to plot. By default, 24",
    )
    parser.add_argument(
        "--minutes",
        type=int,
        metavar="h",
        default=0,
        help="Additional number of minutes to plot. By default, 0",
    )
    parser.add_argument(
        "--show-plot", action="store_true", default=False, help="Also show the plot."
    )

    return parser.parse_args()


if __name__ == "__main__":
    opts = parse_arguments()
    fh = FileHelper(opts.audio_base_dir, opts.score_base_dir)
    plot_segment(
        fh,
        opts.year,
        opts.month,
        opts.day,
        opts.at_hour,
        opts.at_minute,
        opts.hours,
        opts.minutes,
        show_plot=opts.show_plot,
    )
