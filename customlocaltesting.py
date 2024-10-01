import os

# Set environment variables
os.environ['WORKSPACE'] = '/tmp'
os.environ['SKIP_TORCH'] = '1'
os.environ['WINDOW_BACKEND'] = 'headless'

site_packages_dir = r'C:\Users\chris\IdeaProjects\DepthFlow-Lambda-Docker\site-packages'
os.environ['PATH'] = f"{site_packages_dir}:{os.environ.get('PATH', '')}"

import sys

os.environ['PYTHONPATH'] = f"{site_packages_dir}:{os.environ.get('PYTHONPATH', '')}"
sys.path.append(site_packages_dir)

# Apply symlink patch
import symlink_patch

import json
from DepthFlow import DepthScene
from ShaderFlow.Message import ShaderMessage
import base64
from DepthFlow.Motion import Components, Presets, Target

class CustomLambdaScene(DepthScene):
    def setup(self):
        super().setup()

        # Add animations
        self.add_animation(Presets.Dolly(
            intensity=5,
            smooth=True,
            loop=False,
            depth=.3
        ))
        self.add_animation(Components.Arc(
            target=Target.OffsetY,
            points=(-5, 0, 5)
        ))
        self.add_animation(Components.Set(
            target=Target.Zoom,
            value=1.12
        ))
        self.add_animation(Components.Cosine(
            target=Target.OffsetX,
            amplitude=0.6,
            cycles=2.0,
            phase=0.0
        ))


    def update(self):
        self.animate()  # This will apply all the animations we added

    def handle(self, message: ShaderMessage):
        super().handle(message)

def process_scene(image_bytes, depth_bytes):
    scene = CustomLambdaScene(backend='headless')
    scene.input(image=image_bytes, depth=depth_bytes)
    output_path = "/tmp/output.mp4"
    scene.main(output=output_path, fps=30, time=6, ssaa=2, quality=100, height=360, width=540)
    return output_path

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

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Processing complete',
                'output': output_path
            })
        }
    except Exception as e:
        print(str(e))  # Lambda will capture this in CloudWatch logs
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }