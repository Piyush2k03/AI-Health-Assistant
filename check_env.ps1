# Quick script to verify environment setup
Write-Host "=== Environment Check ===" -ForegroundColor Cyan
Write-Host ""

# Check .env file
if (Test-Path .env) {
    Write-Host "✓ .env file found" -ForegroundColor Green
    $envContent = Get-Content .env
    $hasKey = $false
    foreach ($line in $envContent) {
        if ($line -match "^GEMINI_API_KEY=") {
            $hasKey = $true
            $keyValue = $line -replace "^GEMINI_API_KEY=", ""
            $keyValue = $keyValue.Trim()
            if ($keyValue.Length -gt 20) {
                Write-Host "✓ GEMINI_API_KEY found (length: $($keyValue.Length))" -ForegroundColor Green
                $previewLen = if ($keyValue.Length -gt 10) { 10 } else { $keyValue.Length }
                Write-Host "  Key starts with: $($keyValue.Substring(0, $previewLen))..." -ForegroundColor Gray
            } else {
                Write-Host "⚠ GEMINI_API_KEY seems too short" -ForegroundColor Yellow
            }
        }
    }
    if (-not $hasKey) {
        Write-Host "✗ GEMINI_API_KEY not found in .env file" -ForegroundColor Red
    }
} else {
    Write-Host "✗ .env file NOT found" -ForegroundColor Red
    Write-Host "  Create it with: GEMINI_API_KEY=your_key_here" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Docker Check ===" -ForegroundColor Cyan

# Check if Docker container is running
$containerRunning = docker ps --filter "name=medai-healthcare" --format "{{.Names}}" 2>$null
if ($containerRunning) {
    Write-Host "✓ Docker container is running" -ForegroundColor Green
    
    # Check environment variable in container
    Write-Host "Checking environment variable in container..." -ForegroundColor Gray
    $envInContainer = docker exec medai-healthcare printenv GEMINI_API_KEY 2>$null
    if ($envInContainer) {
        Write-Host "✓ GEMINI_API_KEY found in container" -ForegroundColor Green
        $previewLen2 = if ($envInContainer.Length -gt 10) { 10 } else { $envInContainer.Length }
        Write-Host "  Value starts with: $($envInContainer.Substring(0, $previewLen2))..." -ForegroundColor Gray
    } else {
        Write-Host "✗ GEMINI_API_KEY NOT found in container" -ForegroundColor Red
        Write-Host "  Try: docker-compose down && docker-compose up --build" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ Docker container not running" -ForegroundColor Yellow
    Write-Host "  Start it with: docker-compose up" -ForegroundColor Yellow
}

Write-Host ""

