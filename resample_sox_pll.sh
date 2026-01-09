#!/usr/bin/env bash

# This script is essentially as resample_sox.sh, but uses
# GNU Parallel (https://www.gnu.org/software/parallel)
# to launch the individual process instances.

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

printf "Starting resample_sox_pll.sh: %04d-%02d days: %s\n" "${year}" "${month}" "${days_line}"

infile=$(printf  "%s/MARS-%04d%02d{}T000000Z-16kHz.wav" "${in_dir}" "${year}" "${month}")
outfile=$(printf "%s/MARS-%04d%02d{}T000000Z-10kHz.wav" "${out_dir}" "${year}" "${month}")
for day in ${days}; do
  printf "%02d\n" "$day"
done | parallel "sox ${infile} -r 10000 ${outfile}"

printf "\nCompleted resample_sox_pll.sh for %04d-%02d days:%s" "${year}" "${month}" "${days_line}"
