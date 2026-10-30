#!/bin/bash
# Usage: bash snellius/status.sh [model filter, default 14B]
F=${1:-14B}
cd ~/Think_QE_IR2 2>/dev/null
short() { sed -e 's/DeepSeek-R1-Distill-Qwen-//g' -e 's/tqe_//g' -e 's/  */ /g'; }
echo "=== Results $(date +%H:%M) ==="
python3 snellius/collect_results.py "$F" 2>&1 | tail -n +3 | short
echo
DONE=$(sacct -u $USER --starttime today -X --noheader --format=JobName%70,State | grep "$F" | grep -c COMPLETED)
FAIL=$(sacct -u $USER --starttime today -X --noheader --format=JobName%70,State | grep "$F" | grep -c -E "FAILED|TIMEOUT|CANCELLED|OUT_OF_ME")
echo "=== Jobs: $DONE completed, $FAIL failed; running/queued: ==="
squeue -u $USER --noheader --format="%10i %70j %3t %9M" | grep "$F" | short
