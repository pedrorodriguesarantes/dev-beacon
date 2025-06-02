#!/bin/bash
#SBATCH --job-name=devBeaconKubernetes
#SBATCH --output=/scratch/pro32/devBeacon/logs/kubernetesOutput.txt     # Adjust path as needed
#SBATCH --time=48:00:00                                                 # Job time limit
#SBATCH --chdir=/scratch/pro32/devBeacon/                               # Project working directory
#SBATCH --mem=16000                                                     # Memory allocation (in MB)
#SBATCH --mail-type=FAIL                                                # Notifications on job failure

# Optional: specify modules (adjust to your system)
module load python/3.9

# Securely load your API key from a secrets file outside the project
source /scratch/pro32/devBeacon/secrets/github.env

# Activate the Python virtual environment
source .venv/bin/activate

# Pull latest changes (optional, ensures you're working with the latest code)
git pull origin main   # Adjust branch if needed

# Run your extraction scripts with the secret API key
python backend/functions/issueExtractor.py kubernetes kubernetes $API_KEY
python backend/functions/pullRequestExtractor.py kubernetes kubernetes $API_KEY
python backend/functions/milestoneExtractor.py kubernetes kubernetes $API_KEY

python productivityISProcessing.py kubernetes kubernetes
python productivityPRProcessing.py kubernetes kubernetes

# Configure Git user
git config --global user.name "pedrorodriguesarantes"
git config --global user.email "pedrorodriguesarantes@gmail.com"

# Add and commit changes (replace 'backend/files' and 'backend/metrics' with your target folders)
git add backend/files backend/metrics
git commit -m "Update metrics and issues from SLURM run [skip ci]" || echo "No changes to commit"
git push origin main   # Adjust branch if needed
