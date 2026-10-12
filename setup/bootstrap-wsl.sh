#!/usr/bin/env bash
# Step 1b: run INSIDE Ubuntu (WSL) after WSL is installed and you've created your Linux user.
#   bash /mnt/c/Users/you/OneDrive/Documents/Projects/OpenRig/setup/bootstrap-wsl.sh
set -euo pipefail

echo "== Installing base packages (will ask for your Linux password) =="
sudo apt-get update
sudo apt-get install -y tmux git curl build-essential unzip

echo "== Installing Node 22 via nvm =="
export NVM_DIR="$HOME/.nvm"
if [ ! -d "$NVM_DIR" ]; then
  curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
fi
# shellcheck disable=SC1091
. "$NVM_DIR/nvm.sh"
nvm install 22
nvm alias default 22

echo "== Creating the rig home at ~/openrig =="
mkdir -p "$HOME/openrig"

echo
echo "== Versions =="
echo "node: $(node -v)"
echo "npm:  $(npm -v)"
tmux -V
git --version

echo
echo "== GPU visible inside WSL? =="
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv
else
  echo "nvidia-smi not found. Update your NVIDIA Windows driver, then run 'wsl --shutdown' and try again."
fi

echo
echo "== Can WSL reach Windows localhost? (needs mirrored networking) =="
if curl -s --max-time 2 http://localhost:11434 >/dev/null 2>&1; then
  echo "Ollama on Windows is reachable."
else
  echo "Not reachable yet. That's expected until Ollama is installed (step 3)."
fi

echo
echo "Done. Paste everything from '== Versions ==' down back to Claude."
