#!/bin/bash

# Release script for seahi-skills
# Usage: ./scripts/release.sh [patch|minor|major]

set -e

VERSION_TYPE=${1:-patch}

echo "🚀 Releasing seahi-skills..."

# Check if we're on main branch
BRANCH=$(git branch --show-current)
if [ "$BRANCH" != "main" ]; then
  echo "❌ Error: Must be on main branch to release (currently on $BRANCH)"
  exit 1
fi

# Check if working directory is clean
if [ -n "$(git status --porcelain)" ]; then
  echo "❌ Error: Working directory is not clean"
  exit 1
fi

# Get current version
CURRENT_VERSION=$(node -p "require('./package.json').version")
echo "📦 Current version: $CURRENT_VERSION"

# Bump version
case $VERSION_TYPE in
  patch)
    npm version patch --no-git-tag-version
    ;;
  minor)
    npm version minor --no-git-tag-version
    ;;
  major)
    npm version major --no-git-tag-version
    ;;
  *)
    echo "❌ Invalid version type: $VERSION_TYPE"
    echo "Usage: ./scripts/release.sh [patch|minor|major]"
    exit 1
    ;;
esac

NEW_VERSION=$(node -p "require('./package.json').version")
echo "📦 New version: $NEW_VERSION"

# Run validation
echo "🔍 Running validation..."
npm run validate

# Commit changes
git add package.json
git commit -m "chore: release v${NEW_VERSION}"

# Create tag
git tag -a "v${NEW_VERSION}" -m "Release v${NEW_VERSION}"

echo ""
echo "✅ Release v${NEW_VERSION} prepared!"
echo ""
echo "Next steps:"
echo "  1. Push commit: git push origin main"
echo "  2. Push tag: git push origin v${NEW_VERSION}"
echo ""
echo "Or push both at once:"
echo "  git push origin main --tags"
