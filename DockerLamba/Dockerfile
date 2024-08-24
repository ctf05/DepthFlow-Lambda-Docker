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
    --target=/opt/python \
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

# Set the CMD to the Lambda handler
CMD ["custom.lambda_handler"]
