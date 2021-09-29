from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

# Per `help(scipy)` one actually needs to do an explicit import
# of certain subpackages. Interesting that this doesn't seem to
# be required on notebooks, at least in Colab.
import scipy.signal as sp_signal


def plot_spectrogram_scipy(
    signal: np.ndarray,
    sample_rate: int,
    hydrophone_sensitivity: float,
    title: Optional[str] = None,
    with_colorbar: bool = True,
) -> None:
    # Compute spectrogram:
    w = sp_signal.get_window("hann", sample_rate)
    _, _, psd = sp_signal.spectrogram(
        signal,
        sample_rate,
        nperseg=sample_rate,
        noverlap=0,
        window=w,
        nfft=sample_rate,
    )
    psd = 10 * np.log10(psd) - hydrophone_sensitivity

    # Plot spectrogram:
    plt.imshow(
        psd,
        aspect="auto",
        origin="lower",
        vmin=30,
        vmax=90,
        cmap="Blues",
    )
    plt.yscale("log")
    y_max = sample_rate / 2
    plt.ylim(10, y_max)

    if with_colorbar:
        plt.colorbar()

    plt.xlabel("Seconds")
    plt.ylabel("Frequency (Hz)")
    plt.title(
        title or f"Calibrated spectrum levels, 16 {sample_rate / 1000.0} kHz data"
    )


def plot_scores(
    scores: np.ndarray,
    with_steps: bool = False,
    with_dots: bool = True,
    med_filt_size: Optional[int] = None,
) -> None:
    if with_steps:
        # repeat last value to also see a step at the end:
        scores = np.concatenate((scores, scores[-1:]))
        x = range(len(scores))
        plt.step(x, scores, where="post")
    else:
        x = range(len(scores))

    if with_dots:
        plt.plot(x, scores, "o", color="lightgrey", markersize=9)

    plt.grid(axis="x", color="0.95")
    plt.xlim(xmin=0, xmax=len(scores) - 1)
    plt.ylabel("Model Score")
    plt.xlabel("Seconds")

    if med_filt_size is not None:
        scores_int = [int(s * 1000) for s in scores]
        meds_int = sp_signal.medfilt(scores_int, kernel_size=med_filt_size)
        meds = [m / 1000.0 for m in meds_int]
        plt.plot(x, meds, "p", color="black", markersize=9)
