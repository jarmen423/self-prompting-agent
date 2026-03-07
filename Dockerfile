FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Create output directory
RUN mkdir -p output

# Default command (API Server)
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
