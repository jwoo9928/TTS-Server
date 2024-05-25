# Use an official NVIDIA base image with CUDA support, assuming we are to use an Ubuntu base here for simplicity
FROM python:3.10.14

# Set label for the docker image description
LABEL description="Docker image for TTS"

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app/

# Install dependencies
# Combining RUN commands and cleanup to reduce layer size
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    git ffmpeg

RUN pip install --upgrade pip 

RUN pip install flask gunicorn tts

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Define the default command to run the server
# Adjust the number of workers and threads as per your project's need and environment capability.
CMD ["gunicorn", "-w", "2", "--worker-class", "gthread", "--threads", "2", "-b", "0.0.0.0:8010", "app.wsgi:app"]
