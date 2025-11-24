#!/bin/bash
# Bash script to help set up environment variables for Docker
# Run this script before docker-compose up

echo "=== AI Health Assistant - Environment Setup ==="
echo ""

# Check if .env file exists
if [ -f .env ]; then
    echo "✓ .env file found"
else
    echo "⚠ .env file not found. Creating template..."
    read -p "Enter your GEMINI_API_KEY (or press Enter to skip): " gemini_key
    if [ ! -z "$gemini_key" ]; then
        echo "GEMINI_API_KEY=$gemini_key" > .env
        echo "✓ .env file created"
    else
        echo "⚠ No API key provided. You'll need to set GEMINI_API_KEY environment variable or create .env file manually."
    fi
fi

echo ""
echo "Next steps:"
echo "1. Make sure firebase_key.json exists in the project root"
echo "2. Run: docker-compose up --build"
echo ""

