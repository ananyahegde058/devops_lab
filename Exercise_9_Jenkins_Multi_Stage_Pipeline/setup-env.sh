#!/usr/bin/env bash
# ==============================================================================
# Script: setup-env.sh
# Purpose: Resolves missing Python 3, pip, and Flask dependencies inside the
#          Jenkins container or build agent environment (Step 8 in Lab Manual).
# ==============================================================================

set -e

CONTAINER_NAME="${1:-jenkins}"

echo "=================================================================="
echo "Configuring Python 3 environment in container: ${CONTAINER_NAME}"
echo "=================================================================="

# Check if container is running
if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "ERROR: Container '${CONTAINER_NAME}' is not running."
    echo "Please start Jenkins first via Exercise 7 (e.g. docker run or docker-compose)."
    exit 1
fi

echo "[1/3] Updating apt package indices inside container..."
docker exec -u root "${CONTAINER_NAME}" apt-get update -y

echo "[2/3] Installing Python3, Pip, and build utilities..."
docker exec -u root "${CONTAINER_NAME}" apt-get install -y \
  python3 \
  python3-pip \
  python3-venv \
  python3-flask \
  curl

echo "[3/3] Verifying installations inside Jenkins container..."
docker exec "${CONTAINER_NAME}" python3 --version
docker exec "${CONTAINER_NAME}" python3 -c "import flask; print('Flask successfully installed:', flask.__version__)"

echo "=================================================================="
echo " SUCCESS: Jenkins container environment is now fully configured!"
echo " You may now trigger the multi-stage pipeline build without errors."
echo "=================================================================="
