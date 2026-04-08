#!/usr/bin/env bash
# Remove committed .env from git history (local). Run and then commit.
git rm --cached .env || true
rm -f .env
echo "Removed .env from index and working tree. Commit the change and push."
