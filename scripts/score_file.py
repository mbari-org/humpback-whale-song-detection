#!/usr/bin/env python3
"""
Applies the Google Humpback Whale model on a given WAV file and saves the scores.
The input file is assumed to be sampled at 10 kHz.

Example:
  uv run scripts/score_file.py path/to/MARS_20161221_000046_SongSession_10kHz_HPF5Hz.wav
generates:
  path/to/MARS_20161221_000046_SongSession_10kHz_HPF5Hz.npy
"""

import time
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path

import numpy as np
import soundfile as sf

from hwsd.misc import elapsed_end
from hwsd.model_helper import ModelHelper


def score_file(wav_path: str) -> None:
    wav_path = Path(wav_path)
    print(f"==> Loading {wav_path}")
    audio, sample_rate = sf.read(wav_path, dtype="float32")
    if sample_rate != 10_000:
        print(f"ERROR: Expected 10 kHz sample rate, got {sample_rate} Hz")
        return
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

    out_path = wav_path.with_name(wav_path.stem + "_scores.npy")
    np.save(out_path, scores)
    print(f"==> Scores saved to {out_path}")


def parse_arguments():
    description = "Applies Google Humpback Whale Model on a WAV file (assumed 10 kHz)."
    parser = ArgumentParser(description=description, formatter_class=RawTextHelpFormatter)
    parser.add_argument("wav_file", type=str, help="Path to the input WAV file.")
    return parser.parse_args()


if __name__ == "__main__":
    opts = parse_arguments()
    score_file(opts.wav_file)
