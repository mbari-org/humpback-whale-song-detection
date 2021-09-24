## Some notes taken during initial exercising of the model

- In general, the actual plotted spectrogram selection in each case depends on the
  length of the obtained score array.
- The 300-sec PacificSound example in the notebook results in a score array of
  300 values, that is, one score per second of input signal.
- However, the duration associated to the score array length may not correspond
  exactly to the length of the input signal. By visual inspection, in these cases,
  it seems the given score array corresponds to the trailing section of the input signal,
  so we extract that particular section for the corresponding spectrogram.
- The specific model application behavior needs to be verified.


## Excerpts from paper

Allen Ann N., Harvey Matt, et al.
A Convolutional Neural Network for Automated Detection of Humpback Whale Song
in a Diverse, Long-Term Passive Acoustic Dataset.
Frontiers in Marine Science. 2021.

<https://www.frontiersin.org/articles/10.3389/fmars.2021.607321/full>


> Recording files consisted of a sequence of 75 s blocks of audio, hereafter referred to as segments.

> The raw data were typically sampled at 200 kHz but were low-pass filtered and decimated to 10 kHz,
> resulting in an effective bandwidth of 10 Hz to 5 kHz.

> Two aspects in particular were responsible for most of the quality improvement: 
> primarily, active learning, and secondarily, per-channel energy normalization 
> applied to the spectrograms (PCEN).

> Our front end first applies to the input waveform a standard short-time Fourier transform (STFT)
> with a Hann window of length 1,024 samples (∼100 ms for our 10 kHz audio). 
> With the output size fixed at 128×96 (time, frequency) bins, 
> we experimented with stride lengths of 10, 30, and 50 ms –
> equivalent to context window lengths of 1.28, 3.84, and 6.4 s. 
> (The term context window refers to the duration of audio the model required for a single instance of input).
> 
> The input pipeline read entire segments at once and sliced them into context windows.

> All metrics were computed at the segment level by averaging (mean pooling) the scores of
> non-overlapping context windows covering the segment and considering any segment with
> at least one humpback annotation to be positive.

> This study is unique in the scale of application of a CNN to a large marine acoustic dataset
> and demonstrates the ability of a CNN trained on a relatively small dataset to generalize well
> to a highly variable call type across a varied range of recording and noise conditions.

> Our current method is limited by its ability to only classify a time segment
> as either positive or negative for humpback song. 
