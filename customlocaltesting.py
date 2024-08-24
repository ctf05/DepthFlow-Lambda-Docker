import os

# Set environment variables
os.environ['WORKSPACE'] = '/tmp'
os.environ['SKIP_TORCH'] = '1'
os.environ['WINDOW_BACKEND'] = 'headless'

ffmpeg_dir = '/opt/python'  # Adjust this path if ffmpeg is located elsewhere
os.environ['PATH'] = f"{ffmpeg_dir}:{os.environ.get('PATH', '')}"

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
    scene.main(output=output_path, fps=40, time=8, ssaa=1, quality=100)
    return output_path

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
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