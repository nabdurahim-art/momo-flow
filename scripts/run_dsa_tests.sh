#!/usr/bin/env bash
# Run the DSA search unit tests and store the output as submission evidence.
set -uo pipefail

cd "$(dirname "$0")/.."

OUT="docs/dsa_test_evidence.txt"

{
    echo "DSA Integration & Testing - unit test evidence"
    echo "=============================================="
    echo "Command : python3 -m unittest discover -s tests -v"
    echo "Date    : $(date '+%Y-%m-%d %H:%M:%S')"
    echo "Python  : $(python3 --version 2>&1)"
    echo
} > "$OUT"

status=0
python3 -m unittest discover -s tests -v >> "$OUT" 2>&1 || status=$?
echo >> "$OUT"

cat "$OUT"
exit $status
