# Use slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy script and .env
COPY . .

# Set environment variables if needed (or rely on .env)
ENV PYTHONUNBUFFERED=1

# Run your script
CMD ["python", "main.py"]
