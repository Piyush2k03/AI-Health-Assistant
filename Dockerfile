# -----------------------------
# 1️⃣ Base Python Image
# -----------------------------
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# -----------------------------
# 2️⃣ Set working directory
# -----------------------------
WORKDIR /app

# -----------------------------
# 3️⃣ Install system dependencies
# -----------------------------
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    build-essential \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# -----------------------------
# 4️⃣ Copy project files (excluding .env - will be handled by docker-compose)
# -----------------------------
COPY requirements.txt /app/
COPY app.py /app/
COPY firebase_key.json /app/
COPY assets /app/assets/

# -----------------------------
# 5️⃣ Environment Variables
# -----------------------------
# Note: .env file should be passed via docker-compose env_file or environment variables
# The app will read from environment variables set by docker-compose

# -----------------------------
# 6️⃣ Install Python dependencies
# -----------------------------
RUN pip install --no-cache-dir -r requirements.txt

# -----------------------------
# 7️⃣ Expose Streamlit port
# -----------------------------
EXPOSE 8501

# -----------------------------
# 8️⃣ Run Streamlit App
# -----------------------------
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
