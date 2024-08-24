import os

# Set environment variables
os.environ['WORKSPACE'] = '/tmp'
os.environ['SKIP_TORCH'] = '1'
os.environ['WINDOW_BACKEND'] = 'headless'

ffmpeg_dir = '/opt/python'  # Adjust this path if ffmpeg is located elsewhere
os.environ['PATH'] = f"{ffmpeg_dir}:{os.environ.get('PATH', '')}"
site_packages_dir = '/opt/python/site-packages'
os.environ['PATH'] = f"{site_packages_dir}:{os.environ.get('PATH', '')}"

import sys

os.environ['PYTHONPATH'] = f"{site_packages_dir}:{os.environ.get('PYTHONPATH', '')}"
sys.path.append(site_packages_dir)
os.environ['SAGEMAKER_BIND_TO_PORT'] = '9002'

# Apply symlink patch
import symlink_patch

import json
import base64
import boto3
import uuid
from botocore.exceptions import ClientError
from DepthFlow import DepthScene
from ShaderFlow.Message import ShaderMessage
from DepthFlow.Motion import Components, Presets, Target
import numpy as np
from PIL import Image
import io

class CustomSageMakerScene(DepthScene):
    def setup(self):
        super().setup()

        # Add animations
        self.add_animation(Presets.Orbital(depth=0.5, intensity=0.5))
        self.add_animation(Presets.Dolly())
        self.add_animation(Components.Sine(target=Target.OffsetY, amplitude=0.1, cycles=2))
        self.add_animation(Components.Linear(
            target=Target.Zoom,
            start=0, end=1,
            low=1, hight=1.15
        ))

    def update(self):
        self.animate()  # This will apply all the animations we added

    def handle(self, message: ShaderMessage):
        super().handle(message)

def model_fn(model_dir):
    return CustomSageMakerScene(backend='headless')

def input_fn(request_body, request_content_type):
    if request_content_type == 'application/json':
        input_data = json.loads(request_body)
        image_base64 = input_data.get('image')
        depth_base64 = input_data.get('depth')

        if not image_base64 or not depth_base64:
            raise ValueError("Both 'image' and 'depth' must be provided in the request body")

        image_bytes = base64.b64decode(image_base64)
        depth_bytes = base64.b64decode(depth_base64)

        return {'image': image_bytes, 'depth': depth_bytes}
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    if isinstance(input_data, dict):
        image_bytes = input_data['image']
        depth_bytes = input_data['depth']
    else:
        # If it's just an image array, we'll need to estimate the depth
        image_bytes = Image.fromarray(input_data).tobytes()
        depth_bytes = None  # You might want to add depth estimation here if needed

    model.input(image=image_bytes, depth=depth_bytes)
    output_path = "/tmp/output.mp4"
    model.main(output=output_path, fps=40, time=8, ssaa=1, quality=100)

    # Upload to S3
    bucket_name = 'bucketab3e5-master'
    s3_object_key = upload_to_s3(output_path, bucket_name)

    if not s3_object_key:
        raise Exception("Failed to upload file to S3")

    # Generate presigned URL
    presigned_url = generate_presigned_url(bucket_name, s3_object_key)

    if not presigned_url:
        raise Exception("Failed to generate presigned URL")

    return presigned_url

def output_fn(prediction, accept):
    if accept == 'application/json':
        return json.dumps({
            'message': 'Processing complete',
            'video_url': prediction
        })
    raise ValueError(f"Unsupported accept type: {accept}")

def upload_to_s3(file_path, bucket_name, object_name=None):
    if object_name is None:
        object_name = f"public/{uuid.uuid4()}.mp4"

    s3_client = boto3.client('s3')
    try:
        s3_client.upload_file(file_path, bucket_name, object_name)
    except ClientError as e:
        print(f"Error uploading file to S3: {str(e)}")
        return None
    return object_name

def generate_presigned_url(bucket_name, object_name, expiration=3600):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket_name,
                                                            'Key': object_name},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        print(f"Error generating presigned URL: {str(e)}")
        return None
    return response

