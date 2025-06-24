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