# PowerShell script to help set up environment variables for Docker
# Run this script before docker-compose up

Write-Host "=== AI Health Assistant - Environment Setup ===" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (Test-Path .env) {
    Write-Host "✓ .env file found" -ForegroundColor Green
} else {
    Write-Host "⚠ .env file not found. Creating template..." -ForegroundColor Yellow
    $geminiKey = Read-Host "Enter your GEMINI_API_KEY (or press Enter to skip)"
    if ($geminiKey) {
        "GEMINI_API_KEY=$geminiKey" | Out-File -FilePath .env -Encoding utf8
        Write-Host "✓ .env file created" -ForegroundColor Green
    } else {
        Write-Host "⚠ No API key provided. You'll need to set GEMINI_API_KEY environment variable or create .env file manually." -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Make sure firebase_key.json exists in the project root"
Write-Host "2. Run: docker-compose up --build"
Write-Host ""

