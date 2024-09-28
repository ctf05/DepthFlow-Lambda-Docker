import os

# Set environment variables
os.environ['WORKSPACE'] = '/tmp'
os.environ['WINDOW_BACKEND'] = 'headless'

ffmpeg_dir = '/app:/usr/local/bin'  # Adjusted for Inferless
os.environ['PATH'] = f"{ffmpeg_dir}:{os.environ.get('PATH', '')}"
site_packages_dir = '/app/site-packages'
os.environ['PATH'] = f"{site_packages_dir}:{os.environ.get('PATH', '')}"

import sys

os.environ['PYTHONPATH'] = f"{site_packages_dir}:{os.environ.get('PYTHONPATH', '')}"
sys.path.append(site_packages_dir)

# Apply symlink patch
import symlink_patch

import json
import base64
from DepthFlow import DepthScene
from ShaderFlow.Message import ShaderMessage
from DepthFlow.Motion import Components, Presets, Target

# Additional imports for Inferless
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

class CustomScene(DepthScene):
    def setup(self):
        super().setup()

        # Add animations
        self.add_animation(Presets.Orbital(depth=0.5, intensity=0.5))
        self.add_animation(Presets.Dolly())
        self.add_animation(Components.Sine(target=Target.OffsetY, amplitude=0.1, cycles=2))
        self.add_animation(Components.Linear(
            target=Target.Zoom,
            start=0, end=1,
            low=1, high=1.15
        ))

    def update(self):
        self.animate()  # This will apply all the animations we added

    def handle(self, message: ShaderMessage):
        super().handle(message)

class InferRequest(BaseModel):
    image: str
    depth: str

app = FastAPI()
model = CustomScene(backend='headless')

def process_scene(image_bytes, depth_bytes):
    model.input(image=image_bytes, depth=depth_bytes)
    output_path = "/tmp/output.mp4"
    model.main(output=output_path, fps=12, time=5, ssaa=1, quality=0, height=640, width=360)
    return output_path

@app.get("/v2")
@app.get("/v2/models/depth-flow-model")
def version():
    return {"name": "depth-flow-model"}

@app.get("/v2/health/live")
@app.get("/v2/health/ready")
@app.get("/v2/models/depth-flow-model/ready")
def health():
    return {"status": "running"}

@app.post("/v2/models/depth-flow-model/infer")
def infer(request: InferRequest):
    try:
        image_bytes = base64.b64decode(request.image)
        depth_bytes = base64.b64decode(request.depth)

        output_path = process_scene(image_bytes, depth_bytes)

        # Read the output video file
        with open(output_path, "rb") as video_file:
            video_bytes = video_file.read()

        # Encode video to base64
        video_base64 = base64.b64encode(video_bytes).decode('utf-8')

        # Clean up the temporary file
        os.remove(output_path)

        return {
            "message": "Processing complete",
            "video": video_base64,
            "fps": 12,
            "duration": 5,
            "width": 360,
            "height": 640
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)