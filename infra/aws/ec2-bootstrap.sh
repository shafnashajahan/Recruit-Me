#!/usr/bin/env bash
# Run ONCE on a fresh Ubuntu EC2 instance (as the ubuntu user) to install Docker.
# Usage: bash ec2-bootstrap.sh
set -euo pipefail
sudo apt-get update -y
sudo apt-get install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"

# Small instances (1-2 GB RAM) need swap or the app can be killed for lack of memory
if [ ! -f /swapfile ]; then
  sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
  sudo mkswap /swapfile && sudo swapon /swapfile
  echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
fi
echo "Done. Log out and back in so the docker group applies."
