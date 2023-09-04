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
EXPOSE 8080

# Run app.py when the container launches
CMD ["venv/bin/python", "main.py"]
