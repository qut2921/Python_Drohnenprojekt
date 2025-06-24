# utils/sitemap.py
"""
Module to load image data from a YAML file.
This module provides a function to read image metadata from a YAML file.
"""

import os
import yaml
from PIL import Image
import gps_calculator as gps

def load_image_data(yaml_path: str):
    """
    Load image data from a YAML file.
    
    The YAML file should contain a list of dictionaries where each dictionary represents an image.
    Expected keys for each image:
      - 'filename'          : Filename of the image.
      - 'lat'               : Latitude of the image center.
      - 'lon'               : Longitude of the image center.
      - 'heading'            : Heading of the camera in degrees.
      - 'altitude'           : Altitude above ground of the camera.

    Parameters:
        yaml_path (str): The file path to the YAML file.
        
    Returns:
        list: A list of dictionaries containing image data.
    """
    with open(yaml_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    return data

def compose_images(image_data, images_folder: str, scale: float = 1000000):
    """
    Compose images into a single composite image based on their center coordinates and extents.
    The provided values (centre and extents) are treated as coordinates. A scaling factor is applied to convert these
    coordinate units into pixel units.

    Each image is pasted such that its center aligns with the specified 'centre'.
    The composite image is sized to cover the scaled coordinate bounding box.
    If images overlap, they are overlayed.
    
    Parameters:
        image_data (list): List of dictionaries containing image metadata.
        images_folder (str): Folder path where the image files are stored.
        scale (float): Multiplicative factor to convert coordinate units to pixels.
                       Default value is 1000000.
        
    Returns:
        Image: A PIL.Image object with the composed result.
    """
    # Determine bounding box for the images in coordinate space
    boxes = []
    for img in image_data:
        lat = float(img['lat'])
        lon = float(img['lon'])
        heading = float(img['heading'])
        width_coord, height_coord = gps.calculate_frame_dimensions(img['altitude'], lat)
        left = lon - width_coord / 2
        upper = lat - height_coord / 2
        right = lon + width_coord / 2
        lower = lat + height_coord / 2
        boxes.append((left, upper, right, lower))
    
    min_left = min(box[0] for box in boxes)
    min_upper = min(box[1] for box in boxes)
    max_right = max(box[2] for box in boxes)
    max_lower = max(box[3] for box in boxes)
    
    # Scale coordinate bounding box to pixels
    composite_width = int((max_right - min_left) * scale)
    composite_height = int((max_lower - min_upper) * scale)
    
    composite = Image.new("RGBA", (composite_width, composite_height), (255, 255, 255, 0))
    
    for img in image_data:
        filename = img['filename']
        lat = float(img['lat'])
        lon = float(img['lon'])
        heading = float(img['heading'])
        width_coord, height_coord = gps.calculate_frame_dimensions(img['altitude'], lat)
        print(f"Image {filename} at center ({lat}, {lon}) with width {width_coord} and height {height_coord}")
        width_pix = int(width_coord * scale)
        height_pix = int(height_coord * scale)

        image_path = os.path.join(images_folder, filename)
        try:
            im = Image.open(image_path).convert("RGBA")
        except Exception as e:
            print(f"Fehler beim Laden des Bildes {filename}: {e}")
            continue

        print(f"Processing image: {filename} at center ({lat}, {lon}) with size ({width_pix}, {height_pix})")
        # Resize image to given extents in pixels if needed
        if im.size != (width_pix, height_pix):
            im = im.resize((width_pix, height_pix), Image.Resampling.LANCZOS)

        # Rotate image by heading (negative for clockwise rotation)
        if heading != 0:
            im = im.rotate(-heading, expand=True, resample=Image.Resampling.BICUBIC)

        # Calculate top-left position for the image relative to composite (in pixels)
        left_offset = int((lon - width_coord/2 - min_left) * scale)
        upper_offset = int((lat - height_coord/2 - min_upper) * scale)
        composite.alpha_composite(im, dest=(left_offset, upper_offset))
        
    return composite

# Beispiel: Anwendung der Funktionen
if __name__ == "__main__":
    # Pfad zur YAML-Datei, z.B. "output/images.yaml"
    yaml_file_path = "output/images.yaml"
    images_folder = "output/images"  # Ordner, in dem die Bilddateien liegen
    image_data = load_image_data(yaml_file_path)
    print(f"{image_data}")
    composed_image = compose_images(image_data, images_folder)
    # Speichern des zusammengesetzten Bildes
    output_path = "output/composite.png"
    composed_image.save(output_path)
    print(f"Composite image saved to {output_path}")