#!/usr/bin/env bash
# Extracts the first frame of every video into img/<name>-poster.jpg
# Run again after replacing any mp4.
set -e
cd "$(dirname "$0")"
for f in videos/*.mp4; do
  name=$(basename "$f" .mp4)
  ffmpeg -y -loglevel error -i "$f" -vf "select=eq(n\,0),scale=720:-2" -frames:v 1 -q:v 3 "img/${name}-poster.jpg"
  echo "img/${name}-poster.jpg"
done
