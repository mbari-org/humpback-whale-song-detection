import os

import numpy as np
import tensorflow as tf
import tensorflow_hub as hub

MODEL_URL = "https://tfhub.dev/google/humpback_whale/1"

# Model saved locally here
LOCAL_MODEL = "google/humpback_whale/1"

# We apply the model to get a 1-sec score resolution
# (Note that the model expects input signals sampled at 10 kHz.)
CONTEXT_STEP_SAMPLES = tf.cast(10_000, tf.int64)


class ModelHelper:
    """
    Helps loading and applying the Google model.
    """

    def __init__(self):
        self.model = None
        self.score_fn = None

    def load_model(self) -> None:
        """
        Loads the model, initially by downloading it from its original place,
        then from a local copy in subsequent calls.
        The model and score function are maintained internally.
        """

        if os.path.isdir(LOCAL_MODEL):
            print(f"\n==> Loading model from {LOCAL_MODEL}")
            model = hub.load(LOCAL_MODEL)
        else:
            print(f"\n==> Loading model from {MODEL_URL}")
            model = hub.load(MODEL_URL)
            print(f"    Saving model to {LOCAL_MODEL} ...")
            tf.saved_model.save(
                model,
                LOCAL_MODEL,
                signatures={"score": model.score, "metadata": model.metadata},
            )
            print(f"    Model saved to {LOCAL_MODEL}")

        self.model = model

        self.score_fn = model.signatures["score"]

        metadata_fn = model.signatures["metadata"]
        metadata = metadata_fn()
        print("metadata:")
        for k, v in metadata.items():
            print(f"  {k}: {v}")

    def apply_model(self, psound: np.ndarray) -> np.ndarray:
        """
        Applies the model on given audio segment.

        :param psound:  The input signal, assumed sampled at 10 kHz.
        :return:        Array of corresponding scores at 1-sec resolution.
        """
        waveform1 = np.expand_dims(psound, axis=1)
        waveform_exp = tf.expand_dims(waveform1, 0)  # makes a batch of size 1

        psound_scores = self.score_fn(
            waveform=waveform_exp, context_step_samples=CONTEXT_STEP_SAMPLES
        )
        return psound_scores["scores"].numpy()[0]
