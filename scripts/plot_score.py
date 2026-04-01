#!/usr/bin/env python3
"""
Creates a spectrogram + score plot for a given WAV file and its corresponding score file.
The WAV file is assumed to be sampled at 10 kHz.

Example:
  uv run scripts/plot_score.py path/to/MARS_20161221_000046_SongSession_10kHz_HPF5Hz.wav

  By default, looks for the score file alongside the WAV with the '_scores.npy' suffix.
  You can also specify the score file explicitly:

  uv run scripts/plot_score.py path/to/file.wav --score-file path/to/file_scores.npy

  Plot a segment starting at minute 25 with a duration of 30 minutes:
  uv run scripts/plot_score.py path/to/file.wav --start 25 --duration 30

  To save the plot to a file:
  uv run scripts/plot_score.py path/to/file.wav --output path/to/plot.png
"""

from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as sp_signal
import soundfile as sf
from matplotlib import gridspec

from hwsd.plotting import plot_scores


def _plot_spectrogram(
    signal: np.ndarray,
    sample_rate: int,
    title: str | None,
) -> None:
    window = sp_signal.get_window("hann", sample_rate)
    _, _, psd = sp_signal.spectrogram(
        signal,
        sample_rate,
        nperseg=sample_rate,
        noverlap=0,
        window=window,
        nfft=sample_rate,
    )
    psd_db = 10 * np.log10(psd + 1e-12)

    vmin = float(np.percentile(psd_db, 5))
    vmax = float(np.percentile(psd_db, 99))

    plt.imshow(psd_db, aspect="auto", origin="lower", vmin=vmin, vmax=vmax, cmap="Blues")
    plt.yscale("log")
    plt.ylim(10, sample_rate / 2)
    plt.xlabel("Seconds")
    plt.ylabel("Frequency (Hz)")
    plt.title(title or f"Spectrum levels, {sample_rate / 1000.0} kHz data")


def plot_score(
    wav_path: Path,
    score_path: Path,
    start_min: float,
    duration_min: float | None,
    output: str | None,
    show: bool,
) -> None:
    print(f"==> Loading {wav_path}")
    audio, sample_rate = sf.read(wav_path, dtype="float32")
    if sample_rate != 10_000:
        print(f"ERROR: Expected 10 kHz sample rate, got {sample_rate} Hz")
        return
    if audio.ndim > 1:
        audio = audio[:, 0]
    print(f"    {len(audio):,} samples ({len(audio) / sample_rate:.1f} s)")

    print(f"==> Loading scores from {score_path}")
    scores = np.load(score_path).flatten()
    print(f"    {len(scores):,} score values")

    start_sec = int(start_min * 60)
    end_sec = int((start_min + duration_min) * 60) if duration_min is not None else len(scores)
    end_sec = min(end_sec, len(scores))

    if start_sec > 0 or end_sec < len(scores):
        print(f"    slicing to [{start_sec}s, {end_sec}s)")
        scores = scores[start_sec:end_sec]
        audio = audio[start_sec * sample_rate : end_sec * sample_rate]

    title = f"Scores for {wav_path.name}"
    if start_sec > 0 or duration_min is not None:
        title += f" @ {start_min:.1f}min, duration {(end_sec - start_sec) / 60:.1f}min"

    print("==> Plotting ...")
    fig = plt.figure(figsize=(24, 8))
    grid = gridspec.GridSpec(2, 1, height_ratios=[1, 1])

    print("    plotting spectrogram")
    plt.subplot(grid[0])
    _plot_spectrogram(audio, sample_rate, title)

    print("    plotting scores")
    fig.add_subplot(grid[1])
    plot_scores(scores, with_dots=True, med_filt_size=25)

    plt.tight_layout()

    if output:
        print(f"Saving {output}")
        fig.savefig(output, dpi=120)

    if show:
        plt.show()


def parse_arguments():
    description = "Creates spectrogram + score plot for a WAV file and its score file."
    parser = ArgumentParser(description=description, formatter_class=RawTextHelpFormatter)
    parser.add_argument("wav_file", type=str, help="Path to the input WAV file (10 kHz).")
    parser.add_argument(
        "--score-file",
        type=str,
        default=None,
        help="Path to the score .npy file. Defaults to <wav_stem>_scores.npy alongside the WAV.",
    )
    parser.add_argument(
        "--start",
        type=float,
        default=0.0,
        metavar="minutes",
        help="Start of the segment to plot, in minutes. Default: 0.",
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        metavar="minutes",
        help="Duration of the segment to plot, in minutes. Default: until end of file.",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Save the plot to this image file (e.g. plot.png). If omitted, derived from the WAV filename.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        default=False,
        help="Display the plot interactively.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    opts = parse_arguments()

    wav_path = Path(opts.wav_file)

    score_path = Path(opts.score_file) if opts.score_file \
        else wav_path.with_name(wav_path.stem + "_scores.npy")

    if not wav_path.exists():
        print(f"ERROR: WAV file not found: {wav_path}")
        raise SystemExit(1)
    if not score_path.exists():
        print(f"ERROR: Score file not found: {score_path}")
        raise SystemExit(1)

    output = opts.output
    if output is None and not opts.show:
        output = str(wav_path.with_name(wav_path.stem + "_scores_plot.png"))

    plot_score(
        wav_path=wav_path,
        score_path=score_path,
        start_min=opts.start,
        duration_min=opts.duration,
        output=output,
        show=opts.show,
    )
