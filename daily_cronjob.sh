#!/usr/bin/env bash

# Script intended to be run on `gizo` via crontab:
#  0 3 * * * /opt/humpback/humpback-whale-song-detection/daily_cronjob.sh

# This script is used to:
# - Resample previous day's 16kHz audio file to 10kHz
# - Apply Google/NOAA humpback whale song detection model
# - Clean up the resampled 10kHz file

set -ue

# Change to the directory where this script is located (that is, under the repo clone)
cd "$(dirname "${BASH_SOURCE[0]}")"

# Capture start time
start_time=$SECONDS

AUDIO_BASE_DIR_10kHz="/mnt/PAM_Analysis/GoogleHumpbackModel/decimated_10kHz"

LOG_FILE="/mnt/PAM_Analysis/GoogleHumpbackModel/daily_cronjob.log"

# Get $year $month $day from previous day's date
prev_date=$(date -d 'yesterday' '+%Y %m %d')
read -r year month day <<< "$prev_date"

# Redirect stdout to log file, keep stderr for cron email on errors
mkdir -p logs
exec 1>> "$LOG_FILE"

# Remove leading zeros for proper formatting
year=$(printf "%d" "$year")
month=$(printf "%d" "$month")
day=$(printf "%d" "$day")

printf "=== [%s]: Processing: %04d-%02d-%02d\n" \
       "$(date '+%Y-%m-%d %H:%M:%S')" \
       "$year" "$month" "$day"

# Resample the 16kHz audio file to 10kHz
echo "Resampling audio file..."
./resample_sox.sh "$year" "$month" "$day" 2>&1

# Apply the humpback whale song detection model
echo "Applying humpback whale song detection model..."
uv run python3 -u hwsd/apply_model.py "$year/$month/$day" > "logs/nohup-$year-$month-$day.out" 2>&1

# Remove the resampled 10kHz file
echo "Cleaning up resampled file..."
decimated_file=$(printf "%s/%04d/%02d/MARS-%04d%02d%02dT000000Z-10kHz.wav" \
     "$AUDIO_BASE_DIR_10kHz" "$year" "$month" "$year" "$month" "$day")
if [[ -f "$decimated_file" ]]; then
  rm "$decimated_file"
  echo "Removed: $decimated_file"
else
  echo "Warning: File not found for removal: $decimated_file" >&2
fi

# Calculate and display elapsed time
elapsed=$((SECONDS - start_time))
e_hours=$((elapsed / 3600))
e_minutes=$(((elapsed % 3600) / 60))
e_seconds=$((elapsed % 60))

printf "=== [%s]: Completed: %04d-%02d-%02d (elapsed: %02d:%02d:%02d)\n\n" \
       "$(date '+%Y-%m-%d %H:%M:%S')" \
       "$year" "$month" "$day" "$e_hours" "$e_minutes" "$e_seconds"
