FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependency file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Expose port
EXPOSE 8080

# Run Flask with gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app