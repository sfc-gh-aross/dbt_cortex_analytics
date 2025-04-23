#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# 1. Stage all changes
echo "Staging changes..."
git add .

# 2. Get status and check if there are changes
status_output=$(git status --porcelain)

if [ -z "$status_output" ]; then
  echo "No changes to commit."
  exit 0
fi

echo "Changes detected:"
echo "$status_output"
echo

# 3. Generate commit message
commit_message="Automated commit: Update project files

Changed files:
$status_output"

echo "Committing changes..."
git commit -m "$commit_message"

# 4. Push to remote (origin) and current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "Pushing to origin/$current_branch..."
git push origin "$current_branch"

echo "Git update complete." 