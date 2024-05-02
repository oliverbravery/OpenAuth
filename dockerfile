# Use the official Python image as the base image
FROM python:3.12.3-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port the app will run on
EXPOSE $AUTH_PORT

# Define the command to run the application
CMD uvicorn main:app --host $AUTH_HOST --port $AUTH_PORT