# utils/sitemap.py
"""
Module to load image data from a YAML file.
This module provides a function to read image metadata from a YAML file.
"""

import os
import yaml
from PIL import Image
import gps_calculator as gps
import numpy as np

def load_image_data(yaml_path: str = "output/images.yaml"):
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

def compose_images(image_data, images_folder: str = "output/images", output_path: str = "output/composite.png"):
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
        output_folder (str): Folder path where the output image will be saved.
    Raises:
        ValueError: If no image data is provided or if the images cannot be loaded.
    Returns:
        Image: A PIL.Image object with the composed result.
    """

    if not image_data:
        raise ValueError("No image data provided.")

    # Referenz: Erstes Bild
    ref = image_data[0]
    ref_lat, ref_lon, ref_heading, ref_alt = ref["latitude_drone"], ref["longitude_drone"], ref["heading"], ref["altitude"]

    # Bildgröße in Metern (alle Bilder gleich, da gleiche Höhe)
    frame_width_m, frame_height_m = gps.calculate_frame_dimensions(ref_alt)
    # Lade das erste Bild, um die Pixelgröße zu bestimmen
    ref_img_path = os.path.join(images_folder, ref["filename"])
    ref_img = Image.open(ref_img_path)
    img_width_px, img_height_px = ref_img.size
    px_per_meter_x = img_width_px / frame_width_m
    px_per_meter_y = img_height_px / frame_height_m
    px_per_meter = (px_per_meter_x + px_per_meter_y) / 2  # Mittelwert

    # Koordinaten aller Bilder relativ zum ersten Bild (in Meter, rotiert)
    coords = []
    for img in image_data:
        n, e = gps.calculate_relative_x_y_distance(ref_lat, ref_lon, img["latitude_drone"], img["longitude_drone"])
        # Rotation um -ref_heading (damit das erste Bild "oben" ist)
        theta = np.radians(-ref_heading)
        n_rot = n * np.cos(theta) - e * np.sin(theta)
        e_rot = n * np.sin(theta) + e * np.cos(theta)
        coords.append((n_rot, e_rot, img))

    # Bildpositionen in Pixel
    positions = []
    for n_rot, e_rot, img in coords:
        x = e_rot * px_per_meter
        y = -n_rot * px_per_meter  # -n_rot, weil Bildy-Achse nach unten
        positions.append((x, y, img))

    # Bestimme Bounding Box
    min_x = min(x for x, y, _ in positions)
    min_y = min(y for x, y, _ in positions)
    max_x = max(x for x, y, _ in positions)
    max_y = max(y for x, y, _ in positions)

    # Größe des Gesamtbildes
    composite_width = int(np.ceil(max_x - min_x + img_width_px))
    composite_height = int(np.ceil(max_y - min_y + img_height_px))
    composite = Image.new("RGBA", (composite_width, composite_height), (0, 0, 0, 0))
    print(f"Composite image size: {composite_width}x{composite_height} pixels")

    # Füge alle Bilder ein
    for x, y, img in positions:
        img_path = os.path.join(images_folder, img["filename"])
        im = Image.open(img_path).convert("RGBA")
        # Rotiere Bild um (img_heading - ref_heading)
        rot_angle = -(img["heading"] - ref_heading)
        im_rot = im.rotate(rot_angle, expand=True, resample=Image.Resampling.BICUBIC)
        # Berechne Einfügeposition (Mitte des Bildes auf (x-min_x, y-min_y))
        paste_x = int(x - min_x )
        paste_y = int(y - min_y )
        composite.alpha_composite(im_rot, (paste_x, paste_y))

    # Speichere das Ergebnis
    composite.save(output_path)
    return composite

# Beispiel: Anwendung der Funktionen
if __name__ == "__main__":
    # Laden der Bilddaten aus der YAML-Datei
    image_data = load_image_data()
    print("Loaded image data:", image_data)
    composed_image = compose_images(image_data)