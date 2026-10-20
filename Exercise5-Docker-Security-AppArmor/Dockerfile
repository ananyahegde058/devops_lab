# Use official supported Python slim image
FROM python:3.11-slim

# Set working directory inside container
WORKDIR /app

# Ensure standard output/error are unbuffered and no pyc files written
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Copy dependency definition and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only the application source code
COPY app.py .

# Expose container port 5000
EXPOSE 5000

# Start Flask application
CMD ["python", "app.py"]
