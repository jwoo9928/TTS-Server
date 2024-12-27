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
    git ffmpeg \
    curl

# Install pm2
RUN npm install pm2@latest -g

# Install git lfs
RUN curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash && \
    apt-get install git-lfs && \
    git lfs install

# Clone the required repository
RUN git clone https://huggingface.co/coqui/XTTS-v2 /app/XTTS-v2

# Upgrade pip and install Python dependencies
RUN pip install --upgrade pip 

RUN pip install flask gunicorn tts

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# apt install cuda-11-8
export PATH=/usr/local/cuda-11.8/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda-11.8/lib64:$LD_LIBRARY_PATH
source ~/.bashrc
pip install deepspeed
apt install git
https://github.com/jwoo9928/TTS-Server.git

git ainstall git-lfs
pip uninstall torch torchvision torchaudio
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
# Run the application
CMD ["pm2-runtime", "app.py"]
