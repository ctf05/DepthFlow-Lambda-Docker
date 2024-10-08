# Commands:
# docker build --no-cache -t depth-flow-docker-lambda .
# aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 181172696166.dkr.ecr.us-east-2.amazonaws.com
# docker tag depth-flow-docker-lambda:latest 181172696166.dkr.ecr.us-east-2.amazonaws.com/lome/depthflowimagecontainer:latest
# docker push 181172696166.dkr.ecr.us-east-2.amazonaws.com/lome/depthflowimagecontainer:latest

# Create Lambda: Use the webui, its easier
# aws lambda create-function --function-name depth-flow-docker-lambda --package-type Image --code ImageUri=181172696166.dkr.ecr.us-east-2.amazonaws.com/lome/depthflowimagecontainer:latest --role arn:aws:iam::181172696166:role/lomeawsLambdaRole18e25170-master

# Update Lambda:
# aws lambda update-function-code --function-name depth-flow-docker-lambda --image-uri 181172696166.dkr.ecr.us-east-2.amazonaws.com/lome/depthflowimagecontainer:latest

# Used to create the ECR docker image for lambda

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
RUN git clone https://github.com/ctf05/DepthFlow-Lambda-Docker.git /tmp/repo && \
    mkdir -p /opt/python/site-packages && \
    cp /tmp/repo/custom.py /tmp/repo/symlink_patch.py /tmp/repo/requirements.txt /opt/python/ && \
    rm -rf /tmp/repo

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install \
    --no-cache-dir \
    --target=/opt/python/site-packages \
    --upgrade \
    -r /opt/python/requirements.txt

# Download and install FFmpeg from BtbN's builds
RUN wget https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz && \
    tar xJf ffmpeg-master-latest-linux64-gpl.tar.xz && \
    mv ffmpeg-master-latest-linux64-gpl/bin/ffmpeg /opt/python/ffmpeg && \
    mv ffmpeg-master-latest-linux64-gpl/bin/ffprobe /opt/python/ffprobe && \
    rm -rf ffmpeg-master-latest-linux64-gpl*

# Ensure FFmpeg is in the PATH
ENV PATH="/opt/python:/usr/local/bin:${PATH}"

# Copy contents of /usr/lib64 to /opt/python/usr/lib64
RUN mkdir -p /opt/python/usr/lib64 && \
    cp -r /usr/lib64/* /opt/python/usr/lib64/

# Remove unnecessary files
RUN find /opt/python -type d -name '__pycache__' -exec rm -rf {} + && \
    find /opt/python -type f -name '*.pyc' -delete && \
    find /opt/python -type f -name '*.pyo' -delete && \
    find /opt/python -type d -name 'tests' -exec rm -rf {} +

# Set the CMD to the Lambda handler
CMD ["custom.lambda_handler"]
