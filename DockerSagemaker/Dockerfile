# Commands:
# docker build --no-cache -t lome/depthflowsagemakerimagecontainer .
# aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 181172696166.dkr.ecr.us-east-2.amazonaws.com
# docker tag lome/depthflowsagemakerimagecontainer:latest 181172696166.dkr.ecr.us-east-2.amazonaws.com/lome/depthflowsagemakerimagecontainer:latest
# docker push 181172696166.dkr.ecr.us-east-2.amazonaws.com/lome/depthflowsagemakerimagecontainer:latest

# Used to create the ECR docker image for sagemaker

# Use the latest AWS SageMaker runtime as the base image
FROM python:3.12-slim AS builder

# Switch to root user for installations
USER root

# Set the working directory in the container
WORKDIR /opt/ml/code

# Install system dependencies and build dependencies
RUN apt-get update && apt-get install -y \
    git unzip wget tar gzip xz-utils zip \
    libgl1-mesa-glx libglib2.0-0 \
    libsm6 libxext6 libxrender-dev \
    gcc g++ && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Clone your Git repository and copy necessary files to /opt/ml/code
RUN git clone https://github.com/ctf05/DepthFlow-Lambda-Docker.git /tmp/repo && \
    mkdir -p /opt/ml/code && \
    cp /tmp/repo/inference.py /opt/ml/code/ && \
    cp /tmp/repo/symlink_patch.py /opt/ml/code/ && \
    cp /tmp/repo/requirements.txt /opt/ml/code/ && \
    rm -rf /tmp/repo

# Create site-packages directory
RUN mkdir -p /opt/ml/model/site-packages

# Install Python dependencies in /opt/ml/code
RUN python -m pip install --upgrade pip && \
    python -m pip install \
    --no-cache-dir \
    --target=/opt/ml/code/site-packages \
    --upgrade \
    -r /opt/ml/code/requirements.txt

# Download and install FFmpeg in /opt/ml/code
RUN wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz --no-check-certificate && \
    tar xJf ffmpeg-release-amd64-static.tar.xz && \
    mv ffmpeg-*-amd64-static/ffmpeg /opt/ml/code/ && \
    rm -rf ffmpeg-release-amd64-static*

# Copy contents of /usr to /opt/ml/code/usr
RUN mkdir -p /opt/ml/code/usr && \
    cp -r /usr/* /opt/ml/code/usr/

# Remove unnecessary files
RUN find /opt/ml/code -type d -name '__pycache__' -exec rm -rf {} + && \
    find /opt/ml/code -type f -name '*.pyc' -delete && \
    find /opt/ml/code -type f -name '*.pyo' -delete && \
    find /opt/ml/code -type d -name 'tests' -exec rm -rf {} +

# Switch back to the default SageMaker user
USER 1000

ENTRYPOINT ["python", "/opt/ml/code/inference.py"]