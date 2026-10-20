#!/bin/bash
# ==============================================================================
# Script: git-setup-commands.sh
# Purpose: Reference Git commands for publishing the Jenkins Hello World project to GitHub
# ==============================================================================

set -e

# Replace with your actual GitHub username and repository name
GITHUB_USERNAME="<your-github-username>"
REPO_NAME="devops-sample-code"

echo "1. Initialize local Git repository (if not already done)"
git init

echo "2. Configure local Git identity"
# git config user.name "Your Name"
# git config user.email "your.email@example.com"

echo "3. Add and make the script executable"
chmod +x hello-world.sh
git add hello-world.sh

echo "4. Commit the script"
git commit -m "Add hello-world.sh for Jenkins Freestyle job"

echo "5. Rename branch to main"
git branch -M main

echo "6. Add GitHub remote origin"
git remote add origin "https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

echo "7. Push to GitHub"
echo "Run: git push -u origin main"
echo "(When prompted, provide your GitHub username and Personal Access Token)"
