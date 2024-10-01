import os
from io import BytesIO
from PIL import Image
import base64
import json
import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter, maximum_filter

# Set environment variables
os.environ['WORKSPACE'] = '/tmp'
os.environ['WINDOW_BACKEND'] = 'headless'

site_packages_dir = r'C:\Users\chris\IdeaProjects\DepthFlow-Lambda-Docker\site-packages'
os.environ['PATH'] = f"{site_packages_dir}:{os.environ.get('PATH', '')}"

os.environ['PYTHONPATH'] = f"{site_packages_dir}:{os.environ.get('PYTHONPATH', '')}"
sys.path.append(site_packages_dir)

import symlink_patch
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


def process_scene(image_array, depth_array):
    """
    Modified process_scene to accept uint8 arrays for image and depth.
    """
    scene = CustomLambdaScene(backend='headless')

    # Image and depth are now uint8 arrays
    scene.input(image=image_array, depth=depth_array)

    output_path = "/tmp/output.mp4"
    scene.main(output=output_path, fps=30, time=6, ssaa=2, quality=100, height=1152, width=648)
    return output_path


def display_images(image_np, depth_np):
    # Use matplotlib to display the images
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].imshow(image_np)
    axes[0].set_title('Image (uint8)')
    axes[0].axis('off')

    axes[1].imshow(depth_np, cmap='gray')
    axes[1].set_title('Depth Image (uint8)')
    axes[1].axis('off')

    plt.show()


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

        # Convert byte arrays to images
        image = Image.open(BytesIO(image_bytes))
        depth = Image.open(BytesIO(depth_bytes))

        # Convert PIL images to NumPy arrays
        image_np = np.array(image)
        depth_np = np.array(depth)

        depth_np = gaussian_filter(input=depth_np, sigma=0.6)

        depth_np = maximum_filter(input=depth_np, size=5)

        # Print the original data type of both image and depth image
        print(f"Original Image dtype: {image_np.dtype}")
        print(f"Original Depth dtype: {depth_np.dtype}")

        # Convert the image from uint8 to uint16 by scaling up
        if image_np.dtype == np.uint8:
            image_np = (image_np.astype(np.uint16) * 256)  # Scale up to uint16 range
            print(f"Converted Image dtype: {image_np.dtype}")

        # Ensure depth image remains uint16
        if depth_np.dtype == np.uint16:
            print(f"Depth image is already in uint16 format.")

        # Display images on the screen
        #display_images(image_np, depth_np)

        # Process scene with uint8 arrays
        output_path = process_scene(image_np, depth_np)

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
