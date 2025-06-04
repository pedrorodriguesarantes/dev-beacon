#!/bin/bash
#SBATCH --job-name=devBeaconJabref
#SBATCH --output=/scratch/pro32/devBeacon/logs/jabrefOutput.txt   # stdout / stderr
#SBATCH --chdir=/scratch/pro32/devBeacon/                         # repo root
#SBATCH --time=48:00:00                                           # wall‑clock limit
#SBATCH --mem=16000                                               # RAM (MB)
#SBATCH --mail-type=FAIL                                          # e‑mail on failure

# ─── 1. HPC‑specific environment (adjust if your cluster uses modules) ─────────
module load python/3.9            # or comment out if not needed

# ─── 2. Optional: keep code up‑to‑date ─────────────────────────────────────────
git pull --ff-only origin main || echo "⚠️  Git pull skipped"

# ─── 3. Make sure the driver script is executable and run it ──────────────────
chmod +x ../bash/rdatatable_datatable.sh
../bash/rdatatable_datatable.sh             # all logic lives in this file
