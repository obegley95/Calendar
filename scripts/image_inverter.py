# file: batch_invert_f1_tracks.py

import requests
from PIL import Image, ImageOps
from io import BytesIO
import os

# Base URL format
BASE_URL = "https://media.formula1.com/image/upload/f_auto,c_limit,w_1440,q_auto/f_auto/q_auto/content/dam/fom-website/2018-redesign-assets/Track%20icons%204x3/{}%20carbon"

# List of track names
tracks = [
    "Australia", "China", "Japan", "Bahrain", "Saudi Arabia", "Miami",
    "Emilia-Romagna", "Monaco", "Spain", "Canada", "Austria", "Great Britain",
    "Belgium", "Hungary", "Netherlands", "Italy", "Azerbaijan", "Singapore",
    "United States", "Mexico", "Brazil", "Las Vegas", "Qatar", "Abu Dhabi"
]

# Output folder
output_folder = os.path.join(os.path.expanduser("~"), "Documents", "F1_Tracks_Inverted")
os.makedirs(output_folder, exist_ok=True)

for track in tracks:
    try:
        url = BASE_URL.format(track.replace(" ", "%20"))
        response = requests.get(url)
        response.raise_for_status()

        image = Image.open(BytesIO(response.content))

        if image.mode != 'RGBA':
            image = image.convert('RGBA')

        r, g, b, a = image.split()
        inverted_rgb = ImageOps.invert(Image.merge("RGB", (r, g, b)))
        r2, g2, b2 = inverted_rgb.split()
        inverted_image = Image.merge("RGBA", (r2, g2, b2, a))

        output_path = os.path.join(output_folder, f"{track.lower().replace(' ', '_')}_inverted.png")
        inverted_image.save(output_path)
        print(f"✅ Saved: {output_path}")

    except Exception as e:
        print(f"❌ Failed: {track} — {e}")
