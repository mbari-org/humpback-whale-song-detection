#!/usr/bin/env python3
"""
Applies the Google Humpback Whale model on a given WAV file and saves the scores.

If the input file is not at 10 kHz, it is first resampled to 10 kHz using `sox`
(invoked as a subprocess). The resampled file is written alongside the input as
`<stem>_10kHz.wav` and reused on subsequent runs.

Scores are saved with 1-second resolution as `<stem>_scores.npy` next to the
10 kHz WAV file actually used for scoring.

Example:
  uv run scripts/score_file.py path/to/MARS_20161221_000046_SongSession.wav
generates (resampling first if needed):
  path/to/MARS_20161221_000046_SongSession_10kHz.wav      (only if input != 10 kHz)
  path/to/MARS_20161221_000046_SongSession[_10kHz]_scores.npy
"""

import shutil
import subprocess
import time
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

import numpy as np
import soundfile as sf

from hwsd.misc import elapsed_end
from hwsd.model_helper import ModelHelper

TARGET_SAMPLE_RATE = 10_000


def ensure_10khz(wav_path: Path, output_dir: Path | None = None) -> Path:
    """
    Returns a path to a 10 kHz version of `wav_path`, resampling via `sox`
    if needed. The resampled file is written as `<stem>_10kHz.wav` in
    `output_dir` (if given) or alongside the input, and reused if already
    present.
    """
    info = sf.info(str(wav_path))
    if info.samplerate == TARGET_SAMPLE_RATE:
        return wav_path

    if shutil.which("sox") is None:
        raise RuntimeError("`sox` not found on PATH; required to resample to 10 kHz.")

    resampled_name = wav_path.stem + "_10kHz.wav"
    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        out_path = output_dir / resampled_name
    else:
        out_path = wav_path.with_name(resampled_name)
    if out_path.exists() and sf.info(str(out_path)).samplerate == TARGET_SAMPLE_RATE:
        print(f"==> Reusing existing 10 kHz file {out_path}")
        return out_path

    print(f"==> Resampling {wav_path} ({info.samplerate} Hz) -> {out_path} (10 kHz) via sox ...")
    started = time.time()
    subprocess.run(
        ["sox", str(wav_path), "-r", str(TARGET_SAMPLE_RATE), str(out_path)],
        check=True,
    )
    print(f"    >> resampled in {elapsed_end(started)}")
    return out_path


def score_file(
    wav_path: str,
    output_dir: str | None = None,
    remove_resampled: bool = False,
) -> None:
    original_path = Path(wav_path)
    out_dir = Path(output_dir) if output_dir is not None else None
    wav_path = ensure_10khz(original_path, out_dir)
    resampled = wav_path != original_path

    print(f"==> Loading {wav_path}")
    audio, sample_rate = sf.read(wav_path, dtype="float32")
    assert sample_rate == TARGET_SAMPLE_RATE, sample_rate
    if audio.ndim > 1:
        audio = audio[:, 0]

    print(f"    {len(audio):,} samples ({len(audio) / sample_rate:.1f} s)")

    model_helper = ModelHelper()
    model_load_started = time.time()
    model_helper.load_model()
    print(f"    >> model loaded in {elapsed_end(model_load_started)}")

    print("==> Applying model ...")
    apply_started = time.time()
    scores = model_helper.apply_model(audio)
    print(f"    >> model applied in {elapsed_end(apply_started)}")
    print(f"    scores: {len(scores):,}")

    score_name = wav_path.stem + "_scores.npy"
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / score_name
    else:
        out_path = wav_path.with_name(score_name)
    np.save(out_path, scores)
    print(f"==> Scores saved to {out_path}")

    if resampled and remove_resampled:
        print(f"==> Removing resampled file {wav_path}")
        wav_path.unlink()


def parse_arguments():
    description = "Applies Google Humpback Whale Model on a WAV file (resampling to 10 kHz via sox if needed)."
    parser = ArgumentParser(description=description, formatter_class=RawTextHelpFormatter)
    parser.add_argument("wav_file", type=str, help="Path to the input WAV file.")
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        metavar="dir",
        help="Directory in which to save the score file. Defaults to alongside the WAV.",
    )
    parser.add_argument(
        "--remove-resampled",
        action="store_true",
        default=False,
        help="If the input was resampled to 10 kHz, delete the resampled WAV after scoring.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    opts = parse_arguments()
    score_file(opts.wav_file, opts.output_dir, opts.remove_resampled)
