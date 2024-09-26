# Commands:
# docker build --no-cache -t lome/depthflowsagemakerimagecontainer .
# aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 181172696166.dkr.ecr.us-east-2.amazonaws.com
# docker tag lome/depthflowsagemakerimagecontainer:latest 181172696166.dkr.ecr.us-east-2.amazonaws.com/lome/depthflowsagemakerimagecontainer:latest
# docker push 181172696166.dkr.ecr.us-east-2.amazonaws.com/lome/depthflowsagemakerimagecontainer:latest

# Used to create the ECR docker image for sagemaker

# Use the latest AWS Sagemaker runtime as the base image
FROM public.ecr.aws/sagemaker/sagemaker-distribution:1.11-cpu AS builder

# Switch to root user for installations
USER root

# Set the working directory in the container
WORKDIR /opt/program

# Install system dependencies and build dependencies
RUN apt-get update && apt-get install -y \
    git unzip wget tar gzip xz-utils zip \
    libgl1-mesa-glx libglib2.0-0 \
    libsm6 libxext6 libxrender-dev \
    gcc g++ && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Clone your Git repository and copy necessary files
RUN git clone https://github.com/ctf05/DepthFlow-Lambda-Docker.git . && \
    mkdir -p /opt/python/site-packages && \
    cp inference.py symlink_patch.py requirements.txt /opt/python/

# Install Python dependencies
RUN python -m pip install --upgrade pip && \
    python -m pip install \
    --no-cache-dir \
    --target=/opt/python/site-packages \
    --upgrade \
    -r /opt/python/requirements.txt

# Download and install FFmpeg
RUN wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    tar xJf ffmpeg-release-amd64-static.tar.xz && \
    mv ffmpeg-*-amd64-static/ffmpeg /opt/python/ && \
    rm -rf ffmpeg-release-amd64-static*

# Copy contents of /usr to /opt/python/usr
RUN mkdir -p /opt/python/usr && \
    cp -r /usr/* /opt/python/usr/

# Remove unnecessary files
RUN find /opt/python -type d -name '__pycache__' -exec rm -rf {} + && \
    find /opt/python -type f -name '*.pyc' -delete && \
    find /opt/python -type f -name '*.pyo' -delete && \
    find /opt/python -type d -name 'tests' -exec rm -rf {} +

# Switch back to the default SageMaker user
USER 1000

# Set the ENTRYPOINT to the inference script
ENTRYPOINT ["python", "/opt/python/inference.py"]