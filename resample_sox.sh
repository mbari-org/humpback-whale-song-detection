#!/usr/bin/env bash

# This script runs `sox` for resampling all days in a given year/month,
# which are required arguments. Example:
#    ./resample_sox.sh 2018 11
# Each resample is launched in its own process.

set -ue

year=$1
month=$2
days=$(seq 1 31)  # for convenience 1–31 regardless of month

audio_base_dir="/PAM_Analysis/decimated_16kHz"
decimated_base_dir="/PAM_Analysis/GoogleHumpbackModel/decimated_10kHz"

days_line="$(echo "${days}" | tr '\n' ' ')"

in_dir=$(printf "%s/%04d/%02d" ${audio_base_dir} "${year}" "${month}")
out_dir=$(printf "%s/%04d/%02d" ${decimated_base_dir} "${year}" "${month}")
mkdir -p "${out_dir}"

printf "Starting resample_sox.sh: %04d-%02d days: %s\n" "${year}" "${month}" "${days_line}"

for day in ${days}; do
  infile=$(printf "%s/MARS-%04d%02d%02dT000000Z-16kHz.wav" "${in_dir}" "${year}" "${month}" "${day}")
  outfile=$(printf "%s/MARS-%04d%02d%02dT000000Z-10kHz.wav" "${out_dir}" "${year}" "${month}" "${day}")
  sox "${infile}" -r 10000 "${outfile}" &
done
wait

printf "\nCompleted resample_sox.sh for %04d-%02d days:%s" "${year}" "${month}" "${days_line}"
