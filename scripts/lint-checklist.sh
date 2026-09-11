# Lint checklist structure
set -euo pipefail
f=CHECKLIST.md
test -f "$f"
grep -q "HARD" "$f"
grep -q "Sign-off" "$f"
echo "OK: $f structure looks intact"
