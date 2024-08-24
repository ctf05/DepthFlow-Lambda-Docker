import os

ffmpeg_dir = '/opt/python'  # Adjust this path if ffmpeg is located elsewhere
os.environ['PATH'] = f"{ffmpeg_dir}:{os.environ.get('PATH', '')}"
site_packages_dir = '/opt/python/site-packages'
os.environ['PATH'] = f"{site_packages_dir}:{os.environ.get('PATH', '')}"

print(os.environ['PATH'])