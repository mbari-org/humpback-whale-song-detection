#!/usr/bin/env bash

# This script runs `sox` for resampling all given days in a given year and month.
# Each resample is launched in its own process.

set -ue

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <year> <month> [ <days>... ]"
  echo "Examples:"
  echo "  $0 2018 11              # all days by default"
  echo "  $0 2025 8 \$(seq 21 31)  # days 21-31"
  exit 1
fi

year=$1
month=$2
shift 2
days=$*
if [[ -z "$days" ]]; then
  days=$(seq 1 31)  # for convenience 1–31 regardless of month
fi

days_line="$(echo "${days}" | tr '\n' ' ')"
printf "Starting resample_sox.sh: %04d-%02d days: %s\n" "${year}" "${month}" "${days_line}"

audio_base_dir="/mnt/PAM_Analysis/decimated_16kHz"
decimated_base_dir="/mnt/PAM_Analysis/GoogleHumpbackModel/decimated_10kHz"

in_dir=$(printf "%s/%04d/%02d" ${audio_base_dir} "${year}" "${month}")
out_dir=$(printf "%s/%04d/%02d" ${decimated_base_dir} "${year}" "${month}")
mkdir -p "${out_dir}"

for day in ${days}; do
  infile=$(printf "%s/MARS-%04d%02d%02dT000000Z-16kHz.wav" "${in_dir}" "${year}" "${month}" "${day}")
  outfile=$(printf "%s/MARS-%04d%02d%02dT000000Z-10kHz.wav" "${out_dir}" "${year}" "${month}" "${day}")
  sox "${infile}" -r 10000 "${outfile}" &
done
wait

printf "\nCompleted resample_sox.sh for %04d-%02d days:%s\n" "${year}" "${month}" "${days_line}"
month_dir=$(printf "%s/%04d/%02d" "${decimated_base_dir}" "${year}" "${month}")
echo "Month directory: ${month_dir}"
