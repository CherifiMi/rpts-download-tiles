import os
import requests
import zipfile
from tqdm import tqdm
import math

MAPBOX_ACCESS_TOKEN = 'sk.eyJ1IjoiZGEtbWl0byIsImEiOiJjbHUydndyY3AwenNlMmtueG51N2g4NmNiIn0.T99nBsc9SPfPRQAoRgD8ew'
STYLES = ['mapbox/streets-v11', 'mapbox/dark-v10', 'mapbox/light-v10', 'mapbox/satellite-v9']
OUTPUT_DIR = './path'
ZOOM_LEVEL = 4

# Algeria bounding box
AREA = {
    'min_lat': 18.968147, 'max_lat': 37.092189,
    'min_lon': -8.668908, 'max_lon': 11.986451
}

def lat_lon_to_tile_coords(lat, lon, zoom):
    lat_rad = math.radians(lat)
    n = 2.0 ** zoom
    x_tile = int((lon + 180.0) / 360.0 * n)
    y_tile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
    return x_tile, y_tile

def download_tile(x, y, z, style):
    url = f"https://api.mapbox.com/styles/v1/{style}/tiles/{z}/{x}/{y}?access_token={MAPBOX_ACCESS_TOKEN}"
    response = requests.get(url)
    return response.content if response.status_code == 200 else None

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_tile(tile_data, path):
    with open(path, 'wb') as tile_file:
        tile_file.write(tile_data)
        print(f"Saved tile: {path}")

def download_tiles(style, zoom):
    min_x, min_y = lat_lon_to_tile_coords(AREA['min_lat'], AREA['min_lon'], zoom)
    max_x, max_y = lat_lon_to_tile_coords(AREA['max_lat'], AREA['max_lon'], zoom)
    for x in tqdm(range(min_x, max_x + 1)):
        for y in range(min_y, max_y + 1):
            tile_data = download_tile(x, y, zoom, style)
            if tile_data:
                path = os.path.join(OUTPUT_DIR, style.replace('/', '_'), str(zoom), str(x))
                ensure_dir(path)
                save_tile(tile_data, os.path.join(path, f"{y}.png"))

def zip_tiles(style):
    zipf = zipfile.ZipFile(f"{style.replace('/', '_')}.zip", 'w', zipfile.ZIP_DEFLATED)
    for root, _, files in os.walk(os.path.join(OUTPUT_DIR, style.replace('/', '_'))):
        for file in files:
            zipf.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(OUTPUT_DIR, style.replace('/', '_'))))
            print(f"Added to zip: {os.path.join(root, file)}")
    zipf.close()

if __name__ == "__main__":
    for style in STYLES:
        print(f"Downloading tiles for style: {style}")
        download_tiles(style, ZOOM_LEVEL)
        print(f"Zipping tiles for style: {style}")
        zip_tiles(style)
