FROM mcr.microsoft.com/playwright/python:v1.45.0-jammy

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8050 \
    HOST=0.0.0.0

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Ensure playwright chromium browser binaries are installed
RUN playwright install chromium

# Copy application source
COPY . .

# Expose application port
EXPOSE 8050

# Start server dynamically respecting $PORT from host (Render / Railway / Fly.io / Heroku)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8050}"]
