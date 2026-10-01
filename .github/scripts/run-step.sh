#!/usr/bin/env bash
set -uo pipefail

log="$(mktemp)"
"$@" >"$log" 2>&1
status=$?

if [ "$status" -ne 0 ]; then
    tail_lines="$(tail -n 40 "$log")"
    echo "::error title=Command failed (exit $status)::$*"
    echo "Last 40 lines of output:"
    echo "$tail_lines"
    {
        echo "### Failed: \`$*\` (exit $status)"
        echo '```'
        echo "$tail_lines"
        echo '```'
    } >>"${GITHUB_STEP_SUMMARY:-/dev/null}"
    exit "$status"
fi

tail -n 15 "$log"
