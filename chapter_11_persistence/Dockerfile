# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD app.py /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir Flask==2.0.2 Werkzeug==2.0.2

# add default environment variables
ENV POD_NAME="dummy_pod" STORAGE_PREFIX="/opt"

# Make port 5000 available to the world outside this container
EXPOSE 8080

# Run server.py when the container launches
CMD ["python", "app.py"]