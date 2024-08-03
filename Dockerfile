# Use the official Python image from the Docker Hub
FROM python:3.8-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Create a directory for the app
WORKDIR /app

# Copy the current directory contents into the container
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE 8080

# Run the application with increased timeout
CMD ["gunicorn", "--timeout", "120", "-b", "0.0.0.0:8080", "app:app"]
