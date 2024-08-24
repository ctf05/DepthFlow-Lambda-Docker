# Commands:
# docker build --no-cache --target tester -t lambda-layer-tester .
# docker build -t lambda-layer-builder .
# docker run --rm -v %cd%:/opt lambda-layer-builder

# Use the latest AWS Lambda Python runtime as the base image
FROM public.ecr.aws/lambda/python:3.12-x86_64 AS builder

# Set the working directory in the container
WORKDIR /var/task

# Install system dependencies and build dependencies
RUN dnf update -y && \
    dnf install -y \
        git unzip wget tar gzip xz zip \
        mesa-libGL mesa-libEGL libXrandr libXi libXcursor libXinerama \
        mesa-libGLU mesa-libGL-devel mesa-libEGL-devel \
        libXrandr-devel libXi-devel libXcursor-devel libXinerama-devel \
        gcc gcc-c++ && \
    dnf clean all && \
    rm -rf /var/cache/dnf

# Clone your Git repository and copy only custom.py
RUN git clone https://github.com/ctf05/DepthFlow-Lambda-Docker.git . && \
    mkdir -p /opt/python && \
    cp custom.py symlink_patch.py requirements.txt /opt/python/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install \
    --no-cache-dir \
    --platform manylinux2014_x86_64 \
    --target=/opt/python \
    --implementation cp \
    --python-version 3.10 \
    --only-binary=:all: \
    --upgrade \
    -r requirements.txt

# Download and install FFmpeg
RUN wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    tar xJf ffmpeg-release-amd64-static.tar.xz && \
    mv ffmpeg-*-amd64-static/ffmpeg /opt/python/ && \
    rm -rf ffmpeg-release-amd64-static*

# Remove unnecessary files
RUN find /opt/python -type d -name '__pycache__' -exec rm -rf {} + && \
    find /opt/python -type f -name '*.pyc' -delete && \
    find /opt/python -type f -name '*.pyo' -delete && \
    find /opt/python -type d -name 'tests' -exec rm -rf {} +

# Run the dev import
RUN python -c "import sys; sys.path.append('/opt/python'); from DepthFlow import DepthScene; from custom import CustomLambdaScene; print('Import successful on dev branch!'); scene = CustomLambdaScene(backend='headless'); print('CustomLambdaScene initialized successfully!')"

# Create the ZIP file with maximum compression
RUN cd /opt && zip -r9 /tmp/lambda-layer.zip python

# Create a new stage for testing. This is a more accurate enviroment of AWS Lambda
FROM public.ecr.aws/lambda/python:3.12-x86_64 AS tester

# Install system dependencies
RUN dnf install -y \
        unzip && \
    dnf clean all && \
    rm -rf /var/cache/dnf

# Copy zip from the builder stage
COPY --from=builder /tmp/lambda-layer.zip /tmp/lambda-layer.zip

# Unzip the Lambda layer to /opt
RUN unzip /tmp/lambda-layer.zip -d /opt && rm /tmp/lambda-layer.zip

# Run the test import
RUN python -c "import sys; sys.path.append('/opt/python'); from DepthFlow import DepthScene; from custom import CustomLambdaScene; print('Import successful on test branch!'); scene = CustomLambdaScene(backend='headless'); print('CustomLambdaScene initialized successfully!')"

# Use a minimal base image for the final stage
FROM alpine:latest

# Copy the ZIP file from the builder stage
COPY --from=builder /tmp/lambda-layer.zip /DepthFlow.zip

# Set the entrypoint to copy the ZIP file to the mounted volume
ENTRYPOINT ["/bin/sh", "-c", "cp /DepthFlow.zip /opt/ && echo 'Lambda layer ZIP file created successfully.' && echo 'ZIP file size:' && du -h /opt/DepthFlow.zip"]