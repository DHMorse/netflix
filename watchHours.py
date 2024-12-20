import os
from pathlib import Path
import cv2
import logging

# Suppress OpenCV and FFMPEG warning messages
logging.getLogger("opencv-python").setLevel(logging.ERROR)
os.environ["OPENCV_LOG_LEVEL"] = "OFF"
os.environ["OPENCV_FFMPEG_DEBUG"] = "0"
os.environ["OPENCV_FFMPEG_LOGLEVEL"] = "0"  # Suppress FFMPEG specific warnings

# Redirect stderr to devnull to catch remaining FFMPEG messages
class SuppressFFMPEG:
    def __enter__(self):
        self.stderr = os.dup(2)
        self.devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(self.devnull, 2)
        
    def __exit__(self, *args):
        os.dup2(self.stderr, 2)
        os.close(self.stderr)
        os.close(self.devnull)

def get_video_duration(file_path):
    """Get duration of video file in hours"""
    try:
        with SuppressFFMPEG():
            video = cv2.VideoCapture(str(file_path))
            frames = video.get(cv2.CAP_PROP_FRAME_COUNT)
            fps = video.get(cv2.CAP_PROP_FPS)
            duration_hours = (frames / fps) / 3600  # Convert seconds to hours
            video.release()
        return duration_hours
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def calculate_watch_hours(root_dir):
    """Calculate total watch hours for each show and overall total"""
    root = Path(root_dir)
    shows_duration = {}
    total_duration = 0
    
    # Iterate through all shows
    for show_dir in root.iterdir():
        if not show_dir.is_dir():
            continue
            
        show_duration = 0
        # Iterate through seasons
        for season_dir in show_dir.iterdir():
            if not season_dir.is_dir():
                continue
                
            # Process each episode
            for episode_file in season_dir.glob('*.mp4'):
                duration = get_video_duration(episode_file)
                show_duration += duration
                
        shows_duration[show_dir.name] = show_duration
        total_duration += show_duration
    
    # Sort shows by duration in descending order
    sorted_shows = dict(sorted(shows_duration.items(), 
                             key=lambda x: x[1], 
                             reverse=True))
    
    # Print results
    print("\nWatch Hours Per Show:")
    print("-" * 30)
    for show, duration in sorted_shows.items():
        print(f"{show}: {duration:.2f} hours")
    
    print("\nTotal Watch Hours Across All Shows:")
    print("-" * 30)
    print(f"{total_duration:.2f} hours")
    
    return sorted_shows, total_duration

if __name__ == "__main__":
    # Replace with your root directory path
    root_directory = "/home/daniel/Documents/USB128_copy/TV"
    calculate_watch_hours(root_directory)