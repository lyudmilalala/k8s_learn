# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD app.py /app

# Install any needed packages specified in requirements.txt
RUN pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --no-cache-dir Flask==2.0.2 requests==2.26.0 Werkzeug==2.0.2

# add default environment variables
ENV APP_NAME="default-app" POD_NAME="dummy_pod"

# Make port 5000 available to the world outside this container
EXPOSE 8080

# Run server.py when the container launches
CMD ["python", "app.py"]