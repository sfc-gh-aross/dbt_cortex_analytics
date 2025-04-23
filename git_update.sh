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
echo "Generating commit message..."
commit_subject="Automated commit: Update project files"
commit_body=""

# Parse git status output
modified_files=""
added_files=""
deleted_files=""
untracked_files=""
other_changes=""

while IFS= read -r line; do
  # Extract status and file path
  # Handle potentially complex file paths (spaces, etc.) correctly
  status=${line:0:2}
  file=${line:3}

  case "$status" in
    " M") modified_files+="  - $file
";;
    " A") added_files+="  - $file
";; # Staged Added
    " D") deleted_files+="  - $file
";; # Staged Deleted
    "AM") added_files+="  - $file (staged as added, modified in worktree)
";;
    "MM") modified_files+="  - $file (staged as modified, modified in worktree)
";;
    "MD") deleted_files+="  - $file (staged as modified, deleted in worktree)
";;
    "AD") deleted_files+="  - $file (staged as added, deleted in worktree)
";;
    " R") other_changes+="  - Renamed: $file
";; # Staged Renamed
    " C") other_changes+="  - Copied: $file
";; # Staged Copied
    "??") untracked_files+="  - $file
";;
     *) other_changes+="  - [$status] $file
";; # Catch-all for other statuses (like M ,  D, etc.)
  esac
done <<< "$status_output"

if [ -n "$modified_files" ]; then
  commit_body+="
Modified files:
$modified_files"
fi
if [ -n "$added_files" ]; then
  commit_body+="
Added files:
$added_files"
fi
if [ -n "$deleted_files" ]; then
  commit_body+="
Deleted files:
$deleted_files"
fi
if [ -n "$untracked_files" ]; then
  # Note: 'git add .' stages untracked files, so they appear as Added (' A')
  # If script logic changes to not add everything, this section might be relevant.
  commit_body+="
Untracked files (now added):
$untracked_files"
fi
if [ -n "$other_changes" ]; then
  commit_body+="
Other changes:
$other_changes"
fi

# Combine subject and body, removing leading/trailing whitespace from body
commit_body=$(echo -e "$commit_body" | sed '/^[[:space:]]*$/d' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
commit_message="$commit_subject"
if [ -n "$commit_body" ]; then
  commit_message+="

$commit_body"
fi


echo "Committing changes with message:"
echo "--------------------"
echo -e "$commit_message" # Use -e to interpret backslashes like 

echo "--------------------"
git commit -m "$commit_message"

# Ask for confirmation before pushing
read -p "Are you sure you want to push these changes to origin/$current_branch? (y/n): " confirm

# Convert input to lowercase
confirm_lower=$(echo "$confirm" | tr '[:upper:]' '[:lower:]')

# Check confirmation
if [[ "$confirm_lower" != "y" && "$confirm_lower" != "yes" ]]; then
  echo "Push aborted by user."
  exit 1
fi

# 4. Push to remote (origin) and current branch
current_branch=$(git rev-parse --abbrev-ref HEAD)
echo "Pushing to origin/$current_branch..."
git push origin "$current_branch"

echo "Git update complete." 