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

class CustomLambdaScene(DepthScene):
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

def process_scene(image_bytes, depth_bytes):
    scene = CustomLambdaScene(backend='headless')
    scene.input(image=image_bytes, depth=depth_bytes)
    output_path = "/tmp/output.mp4"
    scene.main(output=output_path, fps=12, time=5, ssaa=1, quality=0, height=640, width=360)
    return output_path

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

def lambda_handler(event, context):
    try:
        body = event.get('body', {})

        image_base64 = body.get('image')
        depth_base64 = body.get('depth')

        if not image_base64 or not depth_base64:
            raise ValueError("Both 'image' and 'depth' must be provided in the request body")

        # Decode base64 strings to bytes
        image_bytes = base64.b64decode(image_base64)
        depth_bytes = base64.b64decode(depth_base64)

        output_path = process_scene(image_bytes, depth_bytes)

        # Upload to S3
        bucket_name = 'bucketab3e5-master'
        s3_object_key = upload_to_s3(output_path, bucket_name)

        if not s3_object_key:
            raise Exception("Failed to upload file to S3")

        # Generate presigned URL
        presigned_url = generate_presigned_url(bucket_name, s3_object_key)

        if not presigned_url:
            raise Exception("Failed to generate presigned URL")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Processing complete',
                'video_url': presigned_url
            })
        }
    except Exception as e:
        print(str(e))  # Lambda will capture this in CloudWatch logs
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }