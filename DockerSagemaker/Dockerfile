# Commands:
# docker build --no-cache -t lome/depthflowsagemakerimagecontainer .
# aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 181172696166.dkr.ecr.us-east-2.amazonaws.com
# docker tag lome/depthflowsagemakerimagecontainer:latest 181172696166.dkr.ecr.us-east-2.amazonaws.com/lome/depthflowsagemakerimagecontainer:latest
# docker push 181172696166.dkr.ecr.us-east-2.amazonaws.com/lome/depthflowsagemakerimagecontainer:latest

# Create Lambda: Use the webui, its easier
# aws lambda create-function --function-name depth-flow-docker-lambda --package-type Image --code ImageUri=181172696166.dkr.ecr.us-east-2.amazonaws.com/lome/depthflowimagecontainer:latest --role arn:aws:iam::181172696166:role/lomeawsLambdaRole18e25170-master

# Update Lambda:
# aws lambda update-function-code --function-name depth-flow-docker-lambda --image-uri 181172696166.dkr.ecr.us-east-2.amazonaws.com/lome/depthflowimagecontainer:latest

# Used to create the ECR docker image for sagemaker

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
    mkdir -p /opt/python/site-packages && \
    cp inference.py symlink_patch.py requirements.txt /opt/python/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install \
    --no-cache-dir \
    --target=/opt/python/site-packages \
    --upgrade \
    -r /opt/python/requirements.txt

# Download and install FFmpeg
RUN wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz && \
    tar xJf ffmpeg-release-amd64-static.tar.xz && \
    mv ffmpeg-*-amd64-static/ffmpeg /opt/python/ && \
    rm -rf ffmpeg-release-amd64-static*

# Copy contents of /usr/lib64 to /opt/python/usr/lib64
RUN mkdir -p /opt/python/usr/lib64 && \
    cp -r /usr/* /opt/python/usr/

# Remove unnecessary files
RUN find /opt/python -type d -name '__pycache__' -exec rm -rf {} + && \
    find /opt/python -type f -name '*.pyc' -delete && \
    find /opt/python -type f -name '*.pyo' -delete && \
    find /opt/python -type d -name 'tests' -exec rm -rf {} +

ENV PATH="/opt/python:/opt/python/site-packages:${PATH}"

# Set the CMD to the Lambda handler
CMD ["python", "/opt/python/inference.py"]
