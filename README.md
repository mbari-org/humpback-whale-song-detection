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

- `resample_sox.sh`:
  For a given year and month, this script starts multiple `sox`
  processes concurrently, one for each day of the month. Example:

        ./resample_sox.sh 2018 11

- `resample_year_months.sh`:
  Runs `resample_sox.sh` in sequence for all given months in a given year.
  Example:

        ./resample_year_months.sh 2018 $(seq 1 10)


## Applying the model

Run `hwsd/apply_model.py` indicating the years, months, and days to process.

Usage:

    hwsd/apply_model.py time-interval ...

where each time interval must be of the form
`yearRange/monthRange/dayRange` or `yearRange/monthRange`,
with each `xxRange` either a single number or a hyphen-separated range with inclusive limits.
If omitted, the day range will be "1-31".

Example: To apply the model on the six full months Oct–Dec'2020 and Jan–Mar'2021:

    hwsd/apply_model.py "2020/10-12" "2021/1-3"

Some of our runs on gizo were like the following:

    source virtenv/bin/activate
    export PYTHONPATH=.

Two concurrent jobs to process Jan–Aug'2021:

    nohup python3 -u hwsd/apply_model.py "2021/1-4" > nohup-2021--1-4.out &
    nohup python3 -u hwsd/apply_model.py "2021/5-8" > nohup-2021--5-8.out &

Five concurrent jobs to process Jan–Oct'2018:

    nohup python3 -u hwsd/apply_model.py "2018/1-2" > nohup-2018--1-2.out &
    nohup python3 -u hwsd/apply_model.py "2018/3-4" > nohup-2018--3-4.out &
    nohup python3 -u hwsd/apply_model.py "2018/5-6" > nohup-2018--5-6.out &
    nohup python3 -u hwsd/apply_model.py "2018/7-8" > nohup-2018--7-8.out &
    nohup python3 -u hwsd/apply_model.py "2018/9-10" > nohup-2018--9-10.out &

Note that `hwsd/apply_model.py` is a convenience to run the actual core function
`apply_model_day` on multiple days.
For a particular day you can also run `hwsd/apply_model_day.py` directly.
Run the following for usage:

    hwsd/apply_model_day.py --help

## Generating plots

This repo also includes code to generte plots with spectrograms and scores,
which mainly helped with initial validations.

In this case, no command line arguments are expected.
Edit `hwsd/plot_scores.py` as needed to indicate the
years, months, and days to process. Then, run it:

    hwsd/plot_scores.py

Each generated plot file will be located next to the corresponding score file.

Note that `hwsd/plot_scores.py` is a convenience to run the actual core function
`plot_scores_day` on multiple days. 
For a particular day you can also run `hwsd/plot_scores_day.py` directly.
Run the following for usage:

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
