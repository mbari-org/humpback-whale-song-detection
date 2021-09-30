# Detecting Humpback Whale Song

Applying the NOAA/Google Humpback Whale Song Detector on Pacific Ocean Sound data.

References:

- <https://tfhub.dev/google/humpback_whale/1>
- <https://doi.org/10.1109/OCEANS.2016.7761363>

Some notebooks where code developed here has been used:

- <https://colab.research.google.com/drive/13HinPes8vi39yjb7nD3ZULpB3eXZFxvc>
- <https://colab.research.google.com/drive/11gxYzDKPgyqncu1ooiTrH-iWtemkFIJJ>

## Setup

    python3 -m venv virtenv
    source virtenv/bin/activate
    pip install -r requirements.txt

> Note: The `pip` install command above has failed a couple of times on gizo, with
> problems related with tensorflow. I've quickly solved this with a combination of
> explicit installation of tensorflow, one time with `pip install --upgrade 'tensorflow>=2.0.0'`,
> and other time with just `pip install tensorflow` under one other fresh virtualenv.

In subsequent sessions, just run `source virtenv/bin/activate`
to set up the python environment.

## Gizo

On gizo, a copy of the code in this repo is located under
`/opt/humpback/humpback-whale-song-detection/`. 

Base directories:

- `/PAM_Analysis/decimated_16kHz/` - Input audio files sampled at 16kHz

- `/PAM_Analysis/GoogleHumpbackModel/decimated_10kHz/` - Input audio files resampled to 10kHz

- `/PAM_Analysis/GoogleHumpbackModel/Scores/` - Generated score files

With 2016-11-01 as an example:

`/PAM_Analysis/GoogleHumpbackModel/Scores/2016/11/Scores-20161101.npy`

will be the model score file corresponding to the audio file:

`/PAM_Analysis/decimated_16kHz/2016/11/MARS-20161101T000000Z-16kHz.wav`

via the intermediate, decimated 10kHz version at:

`/PAM_Analysis/GoogleHumpbackModel/decimated_10kHz/2016/11/MARS-20161101T000000Z-10kHz.wav`

## Resampling to 10kHz

Note that the NOAA/Google model requires the input signal to be sampled at 10kHz.

We do the necessary resampling beforehand using [`sox`](http://sox.sourceforge.net/). 
The `resample_sox.sh` script launches a `sox`
process for each day in a given month. Example:

    ./resample_sox.sh 2018 11


## Applying the model

Edit `apply_model.py` as needed to indicate the years, months, and days to process.
Basically, you just need to run `hwsd/apply_model.py`, but, depending on how you launch
the script or the amount of work to be dispatched here's a convenient way:

    nohup python -u hwsd/apply_model.py &

Note that `hwsd/apply_model.py` is a convenience to run the actual core function
`apply_model_day` on multiple days.
For a particular day you can also run `hwsd/apply_model_day.py` directly.

    hwsd/apply_model_day.py --help

## Generating the plots

Edit `hwsd/plot_scores.py` as needed to indicate the years, months, and days to process.
Then, run it:

    hwsd/plot_scores.py

Each generated plot file will be located next to the corresponding score file.

Note that `hwsd/plot_scores.py` is a convenience to run the actual core function
`plot_scores_day` on multiple days. 
For a particular day you can also run `hwsd/plot_scores_day.py` directly.

    hwsd/plot_scores_day.py --help

---

## Development

With the setup in place, run the following on a regular basis
as you work with the code:

    make

The default task in the makefile does type checking, testing and code formatting.

**NOTE**: Before committing/pushing any changes, be sure to also run:

    make pylint

and address any issues, or check with the team about any known pylint complaints.

See [`makefile`](makefile) for all available tasks.

> You can also run [`just`](https://github.com/casey/just) if available on the system.
> For example, run `just list` for a nice summary of the available "recipes."
