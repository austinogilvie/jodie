#!/usr/bin/env bash
#
# release.sh — prep and publish a new jodie release to PyPI.
#
# Keeps the two version strings in sync (pyproject.toml + jodie/cli/__doc__.py),
# runs the test suite, builds the sdist/wheel, uploads to PyPI, then commits
# and tags the release.
#
# Usage:
#   ./scripts/release.sh 0.1.3          # set an explicit version
#   ./scripts/release.sh patch          # bump 0.1.2 -> 0.1.3
#   ./scripts/release.sh minor          # bump 0.1.2 -> 0.2.0
#   ./scripts/release.sh major          # bump 0.1.2 -> 1.0.0
#   ./scripts/release.sh patch --dry-run    # show what would happen, change nothing
#   ./scripts/release.sh patch --no-upload  # build + tag, but skip PyPI upload
#
set -euo pipefail

# --- locate repo root (script lives in scripts/) -----------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

PYPROJECT="pyproject.toml"
DOC_FILE="jodie/cli/__doc__.py"

# --- args --------------------------------------------------------------------
DRY_RUN=false
UPLOAD=true
BUMP_ARG=""

for arg in "$@"; do
  case "$arg" in
    --dry-run)   DRY_RUN=true ;;
    --no-upload) UPLOAD=false ;;
    -h|--help)
      grep '^#' "$0" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *) BUMP_ARG="$arg" ;;
  esac
done

if [[ -z "$BUMP_ARG" ]]; then
  echo "error: give a version (e.g. 0.1.3) or a bump type (patch|minor|major)" >&2
  echo "run '$0 --help' for usage" >&2
  exit 1
fi

say() { printf '\033[1;34m==>\033[0m %s\n' "$*"; }

# --- read current version ----------------------------------------------------
CURRENT="$(grep -E '^version = ' "$PYPROJECT" | head -1 | sed -E 's/version = "([^"]+)".*/\1/')"
if [[ -z "$CURRENT" ]]; then
  echo "error: could not read current version from $PYPROJECT" >&2
  exit 1
fi

# --- compute new version -----------------------------------------------------
if [[ "$BUMP_ARG" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  NEW="$BUMP_ARG"
else
  IFS='.' read -r MAJ MIN PAT <<< "$CURRENT"
  case "$BUMP_ARG" in
    major) NEW="$((MAJ + 1)).0.0" ;;
    minor) NEW="${MAJ}.$((MIN + 1)).0" ;;
    patch) NEW="${MAJ}.${MIN}.$((PAT + 1))" ;;
    *)
      echo "error: '$BUMP_ARG' is not a version or one of patch|minor|major" >&2
      exit 1
      ;;
  esac
fi

say "Current version: $CURRENT"
say "New version:     $NEW"

# --- sanity checks -----------------------------------------------------------
# Version in the doc file must currently match pyproject, or they're already
# out of sync and a human should look.
DOC_CURRENT="$(grep -E "^__version__" "$DOC_FILE" | sed -E "s/.*'([^']+)'.*/\1/")"
if [[ "$DOC_CURRENT" != "$CURRENT" ]]; then
  echo "error: version mismatch — $PYPROJECT is $CURRENT but $DOC_FILE is $DOC_CURRENT" >&2
  echo "resolve that by hand before releasing." >&2
  exit 1
fi

if git rev-parse "v$NEW" >/dev/null 2>&1; then
  echo "error: git tag v$NEW already exists" >&2
  exit 1
fi

if [[ -n "$(git status --porcelain)" ]]; then
  echo "error: working tree is dirty — commit or stash first" >&2
  git status --short >&2
  exit 1
fi

if $DRY_RUN; then
  say "DRY RUN — no files changed, nothing built or published."
  say "Would: bump to $NEW, run tests, build, $([[ $UPLOAD == true ]] && echo 'upload to PyPI, ' )commit + tag v$NEW."
  exit 0
fi

# --- 1. bump both version strings -------------------------------------------
say "Bumping version strings..."
# BSD/macOS sed: -i needs an (empty) backup suffix argument.
sed -i '' -E "s/^version = \"$CURRENT\"/version = \"$NEW\"/" "$PYPROJECT"
sed -i '' -E "s/^__version__([[:space:]]*)= '$CURRENT'/__version__\\1= '$NEW'/" "$DOC_FILE"

# --- 2. run tests ------------------------------------------------------------
say "Running test suite..."
python -m pytest -q

# --- 3. build ----------------------------------------------------------------
say "Building sdist + wheel..."
rm -rf dist/
python -m build

# --- 4. upload ---------------------------------------------------------------
if $UPLOAD; then
  say "Uploading to PyPI via twine..."
  python -m twine upload dist/*
else
  say "Skipping PyPI upload (--no-upload)."
fi

# --- 5. commit + tag ---------------------------------------------------------
say "Committing and tagging..."
git add "$PYPROJECT" "$DOC_FILE"
git commit -m "Release $NEW"
git tag "v$NEW"

say "Done. Push with:  git push && git push --tags"
