FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY monitor.py .
COPY create_sheet_template.py .
COPY config.yaml.example .

# Create directory for credentials
RUN mkdir -p /app/credentials

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Command to run the monitor script
CMD ["python", "monitor.py"]
