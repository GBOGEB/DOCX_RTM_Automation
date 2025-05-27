#!/bin/bash

echo "Starting cleanup of yellow marker comments..."

PATTERN1="YELLOW: Check for unmatched or missing brackets"
PATTERN2="YELLOW: End of YAML file, check for unmatched or missing brackets above"

find . \( -name "*.md" -o -name "*.yml" -o -name "*.yaml" -o -name "*.json" \) -type f -print0 | while IFS= read -r -d $'\0' file; do
  echo "Processing file: $file"
  tmp_file=$(mktemp)
  
  if grep -q -e "$PATTERN1" -e "$PATTERN2" "$file"; then
    sed -e "/$PATTERN1/d" -e "/$PATTERN2/d" "$file" > "$tmp_file"
    mv "$tmp_file" "$file"
    echo "Cleaned: $file"
  else
    echo "No yellow markers found in: $file. Skipping."
    rm "$tmp_file"
  fi
done

echo "Cleanup complete."
