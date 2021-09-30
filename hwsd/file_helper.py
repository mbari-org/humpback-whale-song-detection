"""
File handling utilities.
"""
import os
import sys
from math import ceil, floor
from typing import Tuple, Optional

import numpy as np
import soundfile as sf

DEFAULT_AUDIO_BASE_DIR = "/PAM_Analysis/GoogleHumpbackModel/decimated_10kHz/"

DEFAULT_SCORE_BASE_DIR = "/PAM_Analysis/GoogleHumpbackModel/Scores"


class FileHelper:
    """
    Helps loading audio segments, as well as initializing
    and updating score files.
    """

    def __init__(
        self,
        audio_base_dir: str = DEFAULT_AUDIO_BASE_DIR,
        score_base_dir: str = DEFAULT_SCORE_BASE_DIR,
    ):
        if not audio_base_dir.endswith("10kHz"):
            print(
                f"ERROR: Expecting audio_base_dir to end with `10kHz`: {audio_base_dir}"
            )
            sys.exit(1)

        self.audio_base_dir: str = audio_base_dir
        self.score_base_dir: str = score_base_dir
        self.audio_filename: Optional[str] = None
        self.score_filename: Optional[str] = None
        self.year: int = 0
        self.month: int = 0
        self.day: int = 0

    @property
    def sample_rate(self) -> int:
        """The handled sample rate, 10kHz."""
        return 10_000

    def select_day(self, year: int, month: int, day: int) -> bool:
        """
        Selects a particular day, from which segments can then be loaded.

        :return:  True only if corresponding audio file exists.
        """
        simple_name = f"MARS-{year:04}{month:02}{day:02}T000000Z-10kHz.wav"
        self.audio_filename = (
            f"{self.audio_base_dir}/{year:04}/{month:02}/{simple_name}"
        )
        print(f"select_day {year:04}-{month:02}-{day:02}: {self.audio_filename}")

        if not os.path.isfile(self.audio_filename):
            print(f"ERROR: {self.audio_filename}: file not found\n")
            return False

        scores_dest_dir = f"{self.score_base_dir}/{year:04}/{month:02}"
        os.makedirs(scores_dest_dir, exist_ok=True)
        self.score_filename = (
            f"{scores_dest_dir}/Scores-{year:04}{month:02}{day:02}.npy"
        )

        self.year = year
        self.month = month
        self.day = day
        return True

    def load_audio_segment(
        self, at_hour: int = 0, at_minute: int = 0, hours: int = 0, minutes: int = 0
    ) -> Tuple[np.ndarray, int]:
        """
        Loads a segment from the selected day starting at the given
        `at_hour` and `at_minute`, and with duration given by
         `hours` and `minutes`

        :return: (signal, duration_in_seconds)
        """
        assert self.audio_filename is not None

        print(
            f"load_audio_segment @ {at_hour:02}h:{at_minute:02} dur={hours:02}h:{minutes:02}m"
        )
        start_time_secs = (at_hour * 60 + at_minute) * 60
        psound_segment_seconds = (hours * 60 + minutes) * 60
        start_sample = floor(start_time_secs * self.sample_rate)
        num_samples = ceil(psound_segment_seconds * self.sample_rate)

        print(f"Loading {num_samples:,} samples starting at {start_sample:,}")
        psound_segment, sample_rate = sf.read(
            self.audio_filename,
            start=start_sample,
            frames=num_samples,
            dtype="float32",
        )

        assert self.sample_rate == sample_rate  # sanity check

        print(f"    num_samples         = {num_samples:,}")
        print(f"    len(psound_segment) = {len(psound_segment):,}")

        # convert scaled voltage to volts:
        psound_segment *= 3

        return psound_segment, psound_segment_seconds

    def load_day_scores(self) -> np.ndarray:
        """
        Loads the score array for the selected day, initializing the
        array and file if not already created.
        :return: Day score array
        """
        assert self.score_filename is not None

        if os.path.isfile(self.score_filename):
            print(f"\n==> Loading score array {self.score_filename}")
            day_scores = np.load(self.score_filename)
        else:
            print(f"\n==> Initializing score array {self.score_filename}")
            day_scores = np.full(24 * 60 * 60, np.nan)
            np.save(self.score_filename, day_scores)

        return day_scores

    def save_day_scores(self, day_scores: np.ndarray) -> None:
        """
        Updates the score file for the selected day.
        """
        print(f"Saving scores in {self.score_filename}")
        np.save(self.score_filename, day_scores)
