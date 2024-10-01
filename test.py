import json
import base64

import numpy as np
from PIL import Image

from customlocaltesting import lambda_handler

class TestLambdaHandler:
    def __init__(self):
        self.test_image_path = "piggies.png"
        self.test_depth_path = "piggiesdepthmap.png"

        image = Image.open('depth_map_resized_normalized.png')  # Replace 'your_image.png' with the path to your image

        # Convert the image to a NumPy array
        image_np = np.array(image)

        # Print the type of the image (NumPy array)
        print(f"Image dtype: {image_np.dtype}")

    def encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def create_test_event(self):
        return {
            "body": {
                "image": self.encode_image(self.test_image_path),
                "depth": self.encode_image(self.test_depth_path)
            }
        }

    def run_test(self):
        print("Starting test...")

        # Create a test event
        test_event = self.create_test_event()

        # Call the lambda_handler
        response = lambda_handler(test_event, None)

        # Check the response
        if response['statusCode'] == 200:
            print("Test passed!")
            print("Response:", json.loads(response['body']))
        else:
            print("Test failed!")
            print("Error:", json.loads(response['body'])['error'])

if __name__ == "__main__":
    tester = TestLambdaHandler()
    tester.run_test()
