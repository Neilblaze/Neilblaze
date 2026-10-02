#!/usr/bin/env bash

set -euo pipefail

KEEP_DAYS="${KEEP_DAYS:-30}"
DRY_RUN="${DRY_RUN:-false}"
MIN_COMMITS_KEPT=2

branch="$(git rev-parse --abbrev-ref HEAD)"
before_tree="$(git rev-parse 'HEAD^{tree}')"
before_head="$(git rev-parse HEAD)"
before_count="$(git rev-list --count HEAD)"

echo "branch=$branch commits=$before_count keep_days=$KEEP_DAYS"

cutoff="$(git rev-list -1 --before="$KEEP_DAYS days ago" HEAD || true)"

if [ -z "$cutoff" ]; then
  echo "No commit older than $KEEP_DAYS days. Nothing to prune."
  exit 0
fi

if [ "$cutoff" = "$before_head" ]; then
  echo "Cutoff resolved to HEAD -- that would discard every commit. Refusing."
  exit 1
fi

if [ "$(git rev-list --parents -n1 "$cutoff" | wc -w | tr -d ' ')" = "1" ]; then
  echo "Cutoff $cutoff is already a root commit. Nothing to prune."
  exit 0
fi

kept="$(git rev-list --count "$cutoff..HEAD")"
kept=$((kept + 1))  # new root
if [ "$kept" -lt "$MIN_COMMITS_KEPT" ]; then
  echo "Would keep only $kept commit(s); below floor of $MIN_COMMITS_KEPT. Refusing."
  exit 1
fi

echo "new root: $cutoff ($(git log -1 --format=%ci "$cutoff"))"
echo "dropping $((before_count - kept)) commit(s), keeping $kept"

if [ "$DRY_RUN" = "true" ]; then
  echo "DRY_RUN=true -- stopping before rewrite."
  exit 0
fi

git replace --graft "$cutoff"
git filter-repo --force

after_tree="$(git rev-parse 'HEAD^{tree}')"
after_count="$(git rev-list --count HEAD)"

if [ "$after_tree" != "$before_tree" ]; then
  echo "ABORT: HEAD tree changed ($before_tree -> $after_tree). Not pushing."
  exit 1
fi

if [ "$after_count" != "$kept" ]; then
  echo "ABORT: expected $kept commits after rewrite, got $after_count. Not pushing."
  exit 1
fi

git reflog expire --expire=now --all
git gc --prune=now --quiet

echo "OK: $before_count -> $after_count commits, tree $after_tree unchanged"
