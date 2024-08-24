import os

# Set environment variables
os.environ['WORKSPACE'] = '/tmp'
os.environ['SKIP_TORCH'] = '1'
os.environ['WINDOW_BACKEND'] = 'headless'

import json
from DepthFlow import DepthScene
from ShaderFlow.Message import ShaderMessage

# Apply symlink patch
import symlink_patch

class CustomLambdaScene(DepthScene):
    def update(self):
        self.state.offset_x = 0.1  # Example: small constant offset

    def pipeline(self):
        yield from DepthScene.pipeline(self)

    def handle(self, message: ShaderMessage):
        DepthScene.handle(self, message)

def process_scene(image_url):
    scene = CustomLambdaScene(backend='headless')
    scene.input(image=image_url)
    output_path = "/tmp/output.mp4"
    scene.main(output=output_path, fps=30, time=5)
    return output_path

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        image_url = body.get('image_url')

        if not image_url:
            raise ValueError("No image_url provided in the request body")

        output_path = process_scene(image_url)

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