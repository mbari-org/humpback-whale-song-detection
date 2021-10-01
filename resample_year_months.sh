#!/usr/bin/env bash

# This script runs `resample_sox.sh` in sequence for all given months in a given year.
# Example:
#    nohup ./resample_year_months.sh 2018 $(seq 1 10) > nohup_resample_2018.out &

set -eu

year=$1
shift
months=$*

for m in $months; do
   echo "Running ./resample_sox.sh $year $m"
   ./resample_sox.sh $year $m
done
