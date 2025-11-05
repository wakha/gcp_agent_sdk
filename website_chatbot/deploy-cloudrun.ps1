# GCP Cloud Run Deployment Script
# Automatically reads .env file and deploys to Cloud Run

param(
    [string]$Memory = "2Gi",
    [string]$Cpu = "2",
    [string]$MaxInstances = "10",
    [string]$MinInstances = "0",
    [switch]$SkipBuild = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cloud Run Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (!(Test-Path ".env")) {
    Write-Host "ERROR: .env file not found!" -ForegroundColor Red
    Write-Host "Please create a .env file with your configuration." -ForegroundColor Yellow
    exit 1
}

# Read .env file and parse environment variables
Write-Host "Reading .env file..." -ForegroundColor Yellow
$envVars = @{}
Get-Content .env | Where-Object { $_ -match '^\s*[^#]' -and $_ -match '=' } | ForEach-Object {
    $line = $_.Trim()
    if ($line -match '^([^=]+)=(.+)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        $envVars[$key] = $value
    }
}

Write-Host "Found $($envVars.Count) environment variables" -ForegroundColor Green
Write-Host ""

# Extract deployment configuration from .env with defaults
$ProjectId = if ($envVars.ContainsKey('GOOGLE_CLOUD_PROJECT')) { $envVars['GOOGLE_CLOUD_PROJECT'] } else { "gcp-chatbot-477114" }
$Region = if ($envVars.ContainsKey('GOOGLE_CLOUD_LOCATION')) { $envVars['GOOGLE_CLOUD_LOCATION'] } else { "us-central1" }
$ServiceName = if ($envVars.ContainsKey('CLOUD_RUN_SERVICE_NAME')) { $envVars['CLOUD_RUN_SERVICE_NAME'] } else { "website-chatbot-api" }

# Generate version tag using timestamp
$Timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$ImageTag = "v$Timestamp"

# Debug output
Write-Host "DEBUG: ProjectId = '$ProjectId'" -ForegroundColor Magenta
Write-Host "DEBUG: Region = '$Region'" -ForegroundColor Magenta
Write-Host "DEBUG: ServiceName = '$ServiceName'" -ForegroundColor Magenta
Write-Host "DEBUG: ImageTag = '$ImageTag'" -ForegroundColor Magenta

# Remove deployment-only variables from env vars that will be passed to Cloud Run
$deploymentOnlyVars = @('CLOUD_RUN_SERVICE_NAME')
$deploymentOnlyVars | ForEach-Object { $envVars.Remove($_) | Out-Null }

# Build environment variables string for gcloud
$envVarString = ($envVars.GetEnumerator() | ForEach-Object { 
    "$($_.Key)=$($_.Value)" 
}) -join ','

# Display deployment configuration
Write-Host "Deployment Configuration:" -ForegroundColor Cyan
Write-Host "  Project ID:     $ProjectId" -ForegroundColor White
Write-Host "  Service Name:   $ServiceName" -ForegroundColor White
Write-Host "  Region:         $Region" -ForegroundColor White
Write-Host "  Memory:         $Memory" -ForegroundColor White
Write-Host "  CPU:            $Cpu" -ForegroundColor White
Write-Host "  Min Instances:  $MinInstances" -ForegroundColor White
Write-Host "  Max Instances:  $MaxInstances" -ForegroundColor White
Write-Host "  Image Tag:      $ImageTag" -ForegroundColor White
Write-Host "  Image:          gcr.io/$ProjectId/${ServiceName}:${ImageTag}" -ForegroundColor White
Write-Host ""

# Confirm deployment
$confirm = Read-Host "Continue with deployment? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Deployment cancelled." -ForegroundColor Yellow
    exit 0
}

# Confirm deployment
$confirm = Read-Host "Continue with deployment? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Deployment cancelled." -ForegroundColor Yellow
    exit 0
}

if (-not $SkipBuild) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Step 1: Building Docker Image" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    docker build -t "${ServiceName}:latest" .
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Docker build failed!" -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Step 2: Tagging for GCR" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    # Tag with versioned tag
    docker tag "${ServiceName}:latest" "gcr.io/$ProjectId/${ServiceName}:${ImageTag}"
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Docker tag failed!" -ForegroundColor Red
        exit 1
    }

    # Also tag as latest
    docker tag "${ServiceName}:latest" "gcr.io/$ProjectId/${ServiceName}:latest"
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Docker tag (latest) failed!" -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Step 3: Pushing to GCR" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    # Push versioned tag
    docker push "gcr.io/$ProjectId/${ServiceName}:${ImageTag}"
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "ERROR: Docker push failed!" -ForegroundColor Red
        Write-Host "Make sure you're authenticated with: gcloud auth configure-docker" -ForegroundColor Yellow
        exit 1
    }

    # Push latest tag
    docker push "gcr.io/$ProjectId/${ServiceName}:latest"
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "WARNING: Docker push (latest) failed!" -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "Skipping Docker build (using existing image)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Step 4: Deploying to Cloud Run" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Debug: Show the exact command
Write-Host "DEBUG: Full image path = 'gcr.io/$ProjectId/${ServiceName}:${ImageTag}'" -ForegroundColor Magenta

# Deploy to Cloud Run
gcloud run deploy "$ServiceName" `
    --image "gcr.io/$ProjectId/${ServiceName}:${ImageTag}" `
    --platform managed `
    --region "$Region" `
    --allow-unauthenticated `
    --memory "$Memory" `
    --cpu "$Cpu" `
    --timeout 300 `
    --max-instances "$MaxInstances" `
    --min-instances "$MinInstances" `
    --service-account "cloud-run-sa@$ProjectId.iam.gserviceaccount.com" `
    --set-env-vars "$envVarString"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "Deployment Successful!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    
    # Get service URL
    $serviceUrl = gcloud run services describe $ServiceName --region $Region --format 'value(status.url)'
    
    Write-Host "Service URL: $serviceUrl" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Test endpoints:" -ForegroundColor Yellow
    Write-Host "  Health: $serviceUrl/health" -ForegroundColor White
    Write-Host "  Chat:   $serviceUrl/api/chat" -ForegroundColor White
    Write-Host ""
    
    # Test health endpoint
    Write-Host "Testing health endpoint..." -ForegroundColor Yellow
    try {
        $health = Invoke-RestMethod -Uri "$serviceUrl/health"
        Write-Host "[OK] Health check passed!" -ForegroundColor Green
        Write-Host "  Status:  $($health.status)" -ForegroundColor White
        Write-Host "  Version: $($health.version)" -ForegroundColor White
        Write-Host "  Indexed: $($health.indexed)" -ForegroundColor White
    }
    catch {
        Write-Host "[FAILED] Health check failed: $_" -ForegroundColor Red
    }
    
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Deployment Failed!" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Check the error messages above." -ForegroundColor Yellow
    exit 1
}
