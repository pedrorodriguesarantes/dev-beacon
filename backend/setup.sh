set -euo pipefail

# ─────────── CONFIG (edit if you use a different Python) ────────────
PYTHON=python3.12         # interpreter to build the venv
VENV_DIR=".venv"          # where the env lives
REQS="requirements.txt"   # dependency list

# ─────────────────────────────────────────────────────────────────────
echo "📦  Bootstrapping project …"

# 1. sanity‑check Python
command -v "$PYTHON" >/dev/null || {
  echo "❌  $PYTHON not found. Install it (brew install python@3.12 or pyenv)." >&2
  exit 1
}

# 2. create venv (idempotent)
if [[ ! -d $VENV_DIR ]]; then
  "$PYTHON" -m venv "$VENV_DIR"
  echo "  • virtual‑env created in $VENV_DIR/"
fi

# 3. install / update dependencies
source "$VENV_DIR/bin/activate"
pip install --quiet --upgrade pip
pip install --quiet -r "$REQS"

echo "✅  Setup complete. Activate with:  source $VENV_DIR/bin/activate"
