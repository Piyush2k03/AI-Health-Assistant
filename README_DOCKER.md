# Docker Setup Instructions

## API Keys Configuration

This application requires API keys to run. You have two options to provide them:

### Option 1: Using .env file (Recommended)

1. Create a `.env` file in the project root directory:
   ```bash
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   ```

2. The `docker-compose.yaml` will automatically load this file.

### Option 2: Using Environment Variables Directly

You can set the environment variable before running docker-compose:

**On Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_actual_gemini_api_key_here"
docker-compose up
```

**On Windows (CMD):**
```cmd
set GEMINI_API_KEY=your_actual_gemini_api_key_here
docker-compose up
```

**On Linux/Mac:**
```bash
export GEMINI_API_KEY=your_actual_gemini_api_key_here
docker-compose up
```

### Option 3: Edit docker-compose.yaml directly

You can also edit the `docker-compose.yaml` file and add the API key directly in the `environment` section:

```yaml
environment:
  - GEMINI_API_KEY=your_actual_gemini_api_key_here
  - GOOGLE_APPLICATION_CREDENTIALS=/app/firebase_key.json
```

## Running the Application

1. Make sure you have:
   - `firebase_key.json` in the project root
   - `GEMINI_API_KEY` set (via .env file or environment variable)

2. Build and run:
   ```bash
   docker-compose up --build
   ```

3. Access the application at: http://localhost:8501

## Troubleshooting

### API Key Issues

If you see "🚨 Gemini API key missing!" error:

1. Check that your `.env` file exists and contains `GEMINI_API_KEY=...`
2. Or verify the environment variable is set: `echo $GEMINI_API_KEY` (Linux/Mac) or `echo %GEMINI_API_KEY%` (Windows)
3. Restart the container after setting the environment variable

### Firebase Issues

If you see Firebase errors:
- Ensure `firebase_key.json` exists in the project root
- The file should be a valid Firebase service account JSON

