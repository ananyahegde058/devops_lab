#!/usr/bin/env bash
# ==============================================================================
# Script: setup-jenkins.sh
# Purpose: Automate Jenkins container startup, status validation, and password extraction.
# ==============================================================================

set -e

CONTAINER_NAME="jenkins"
IMAGE_NAME="jenkins/jenkins:lts"
PORT="8080"
AGENT_PORT="50000"

echo "[1/4] Checking if an existing Jenkins container is present..."
if [ "$(docker ps -aq -f name=^/${CONTAINER_NAME}$)" ]; then
    echo "Found existing container '${CONTAINER_NAME}'. Removing it to ensure fresh start..."
    docker rm -f "${CONTAINER_NAME}"
fi

echo "[2/4] Starting Jenkins container (${IMAGE_NAME})..."
docker run -d \
  --name "${CONTAINER_NAME}" \
  -p "${PORT}:8080" \
  -p "${AGENT_PORT}:50000" \
  -v jenkins_home:/var/jenkins_home \
  "${IMAGE_NAME}"

echo "[3/4] Waiting for Jenkins initialization (approx. 20-30 seconds)..."
until docker logs "${CONTAINER_NAME}" 2>&1 | grep -q "Jenkins is fully up and running"; do
    echo "Waiting for Jenkins to finish boot..."
    sleep 5
done

echo "[4/4] Retrieving Initial Admin Password..."
PASSWORD=$(docker exec "${CONTAINER_NAME}" cat /var/jenkins_home/secrets/initialAdminPassword 2>/dev/null || true)

echo "=========================================================="
echo " Jenkins is ready!"
echo " URL: http://localhost:${PORT}"
echo " Initial Admin Password: ${PASSWORD}"
echo "=========================================================="
