<#
.SYNOPSIS
    Automate Jenkins container deployment and initial admin password extraction on Windows.
.DESCRIPTION
    Runs Jenkins LTS in Docker, monitors boot readiness, and displays the initial admin credentials.
#>

$ContainerName = "jenkins"
$ImageName = "jenkins/jenkins:lts"
$Port = 8080
$AgentPort = 50000

Write-Host "[1/4] Checking for existing Jenkins container..." -ForegroundColor Cyan
$existing = docker ps -aq -f "name=^/${ContainerName}$"
if ($existing) {
    Write-Host "Removing existing container '$ContainerName'..." -ForegroundColor Yellow
    docker rm -f $ContainerName | Out-Null
}

Write-Host "[2/4] Starting Jenkins container ($ImageName)..." -ForegroundColor Cyan
docker run -d `
  --name $ContainerName `
  -p "${Port}:8080" `
  -p "${AgentPort}:50000" `
  -v jenkins_home:/var/jenkins_home `
  $ImageName

Write-Host "[3/4] Waiting for Jenkins service to initialize (may take 20-30s)..." -ForegroundColor Cyan
$ready = $false
for ($i = 0; $i -lt 15; $i++) {
    Start-Sleep -Seconds 4
    $logs = docker logs $ContainerName 2>&1
    if ($logs -match "Jenkins is fully up and running") {
        $ready = $true
        break
    }
    Write-Host "Still initializing..." -ForegroundColor Gray
}

Write-Host "[4/4] Retrieving Initial Admin Password..." -ForegroundColor Cyan
$pwd = docker exec $ContainerName cat /var/jenkins_home/secrets/initialAdminPassword 2>$null

Write-Host "==========================================================" -ForegroundColor Green
Write-Host " Jenkins is ready!" -ForegroundColor Green
Write-Host " Access URL: http://localhost:$Port" -ForegroundColor Green
Write-Host " Initial Admin Password: $pwd" -ForegroundColor Yellow
Write-Host "==========================================================" -ForegroundColor Green
