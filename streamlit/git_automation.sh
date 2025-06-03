#!/bin/bash

# Check if a commit message is provided
if [ -z "$1" ]; then
  echo "Error: No commit message provided."
  echo "Usage: ./git_automation.sh \"<commit_message>\""
  exit 1
fi

# Assign the first argument to a variable for clarity
COMMIT_MESSAGE="$1"

# Get the current branch name
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Git commands
echo "Adding all changes..."
git add .

echo -e "\nShowing git status..."
git status

echo -e "\nCommitting changes with message: '$COMMIT_MESSAGE'..."
git commit -m "$COMMIT_MESSAGE"

echo -e "\nPushing to remote 'origin' and branch '$CURRENT_BRANCH'..."
git push origin "$CURRENT_BRANCH"

echo -e "\nScript finished." 