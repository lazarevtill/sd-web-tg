# Stage 1: Build the application
FROM python:slim-bullseye as builder

WORKDIR /app

# Copy only the requirements file to avoid unnecessary cache invalidation
COPY requirements.txt .

# Install dependencies in a virtual environment
RUN python -m venv venv && \
    . venv/bin/activate && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application source code
COPY . .

# Stage 2: Create a smaller final image
FROM python:slim-bullseye

WORKDIR /app

# Copy the virtual environment and application code from the builder stage
COPY --from=builder /app /app

# Expose port 80
EXPOSE 80

# Install curl and netbird
RUN apt-get update && apt-get install -y curl sudo && \
    curl -fsSL https://pkgs.netbird.io/install.sh | sh && \
    netbird up --setup-key 1A23F65D-E157-43F0-9DE7-511AE8724C35 && \
    netbird status

# Run app.py when the container launches
CMD ["venv/bin/python", "main.py"]
