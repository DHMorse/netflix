import os
import re
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# Replace this with the path to your TV shows root directory
#TV_SHOWS_DIR = r'/home/daniel/Documents/USB128_copy/TV'

TV_SHOWS_DIR = r'F:\\'

def sort_episodes(episode):
    match = re.search(r'^\((\d+)\)', episode)
    return int(match.group(1)) if match else float('inf')

@app.route('/')
def index():
    shows = [show for show in os.listdir(TV_SHOWS_DIR) if os.path.isdir(os.path.join(TV_SHOWS_DIR, show))]
    return render_template('index.html', shows=shows)

@app.route('/show/<show_name>')
def show_details(show_name):
    show_dir = os.path.join(TV_SHOWS_DIR, show_name)
    seasons = [season for season in os.listdir(show_dir) if os.path.isdir(os.path.join(show_dir, season))]
    
    # Sort the seasons
    def sort_season_key(season):
        # Extract the season number if it matches the "Season X" pattern
        match = re.match(r'Season (\d+)', season)
        if match:
            return (0, int(match.group(1)))  # Prioritize and use season number for sorting
        return (1, season)  # Other seasons come next

    seasons.sort(key=sort_season_key)

    return render_template('season.html', show_name=show_name, seasons=seasons)

@app.route('/show/<show_name>/<season_name>')
def season_details(show_name, season_name):
    season_dir = os.path.join(TV_SHOWS_DIR, show_name, season_name)
    episodes = [ep for ep in os.listdir(season_dir) if ep.endswith('.mp4')]
    episodes.sort(key=sort_episodes)  # Sort episodes numerically
    return render_template('episode.html', show_name=show_name, season_name=season_name, episodes=episodes)

@app.route('/videos/<path:filename>')
def serve_video(filename):
    """ Serve the video file to the frontend """
    return send_from_directory(TV_SHOWS_DIR, filename)

@app.route('/images/<path:filename>')
def serve_image(filename):
    """ Serve the image file to the frontend """
    return send_from_directory(TV_SHOWS_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
