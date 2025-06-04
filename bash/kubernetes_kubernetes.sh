#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

###############################################################################
# 0️⃣  Locate repository root and switch to it
###############################################################################
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &>/dev/null && pwd )"
REPO_ROOT="$( dirname "$SCRIPT_DIR" )"
cd "$REPO_ROOT"                       # e.g. …/your‑project‑root

###############################################################################
# 1️⃣  Run backend/setup.sh **inside** the backend folder
###############################################################################
echo "📦  Bootstrapping backend …"
pushd backend >/dev/null              # enter backend/
chmod +x setup.sh
./setup.sh                            # creates backend/.venv & installs deps
popd >/dev/null                       # back to repo root

###############################################################################
# 2️⃣  Activate the venv that setup.sh just made
###############################################################################
# shellcheck disable=SC1091
source backend/.venv/bin/activate

###############################################################################
# 3️⃣  Load secrets (API_KEY) – path is relative to repo root
###############################################################################
if [[ -f secrets/github.env ]]; then
  # shellcheck disable=SC1091
  source secrets/github.env
else
  echo "❌  secrets/github.env not found – export API_KEY before running." >&2
  exit 1
fi

###############################################################################
# 4️⃣  (Optional) pull latest code
###############################################################################
git pull --ff-only origin main || echo "⚠️  Git pull skipped"

###############################################################################
# 5️⃣  Run extraction & processing
###############################################################################
python backend/functions/issueExtractor.py JabRef jabref "$API_KEY"
python backend/functions/pullRequestExtractor.py JabRef jabref "$API_KEY"
python backend/functions/milestoneExtractor.py JabRef jabref "$API_KEY"

python backend/functions/productivityISProcessing.py JabRef jabref
python backend/functions/productivityPRProcessing.py JabRef jabref

###############################################################################
# 6️⃣  Commit any generated metrics
###############################################################################
git config user.name  "pedrorodriguesarantes"
git config user.email "pedrorodriguesarantes@gmail.com"

git add metrics/
git commit -m "Update metrics and issues (local run) [skip ci]"
git push origin main
