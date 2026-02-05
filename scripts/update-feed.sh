#!/bin/bash
# Update the news.json feed from blogwatcher data
# Run this periodically to refresh the widget content

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_FILE="$PROJECT_DIR/public/news.json"

# Get recent articles from blogwatcher
# This requires blogwatcher to be installed and configured

echo "Fetching articles from blogwatcher..."

# Create temporary file for processing
TEMP_FILE=$(mktemp)

# Get all articles and format as JSON
blogwatcher articles --all 2>/dev/null | head -200 > "$TEMP_FILE"

# For now, this is a placeholder - the actual parsing would need to 
# extract article data and convert to the JSON format
# In practice, Otto 2 will manually update news.json or use a more
# sophisticated parsing script

echo "Feed update placeholder - manual update recommended"
echo "Output would go to: $OUTPUT_FILE"

rm -f "$TEMP_FILE"
