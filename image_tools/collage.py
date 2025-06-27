"""
Creates a side-by-side visual collage from two image files for comparison purposes.

This script loads two images, optionally resizes them to a uniform dimension,
places them side-by-side in a new blank image canvas (collage), and displays the result.
Useful for visual analysis, calibration checks, or presentation of image pairings.
This script was used to find color boundraries used for object detection.

Steps:
    - Load images from specified file paths.
    - Resize images to a consistent size (600x400 pixels).
    - Combine them horizontally into one canvas.
    - Display the resulting collage in a separate window.

Dependencies:
    - PIL (Pillow)
    - matplotlib (used only for import, not utilized in this version)

"""

from PIL import Image
import matplotlib.pyplot as plt

# Lade die Bilder
image1_path = "BildsequenzTest_0/Calibration/frame_8_4.jpg"
image2_path = "BildsequenzTest_0/Calibration/frame_4_2.jpg"

image1 = Image.open(image1_path)
image2 = Image.open(image2_path)

# Größe der Bilder vereinheitlichen (optional)
image1 = image1.resize((600, 400))
image2 = image2.resize((600, 400))

# Collage nebeneinander erstellen
collage = Image.new('RGB', (image1.width + image2.width, image1.height))
collage.paste(image1, (0, 0))
collage.paste(image2, (image1.width, 0))

# Zeige die Collage
collage.show()