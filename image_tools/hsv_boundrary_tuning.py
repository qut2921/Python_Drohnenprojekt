"""
Interactive HSV Threshold Tuning Tool for Color Segmentation using OpenCV.

This script loads an image and allows the user to interactively adjust HSV 
(Hue, Saturation, Value) thresholds using OpenCV trackbars to fine-tune a 
binary mask for color-based segmentation. It supports dual-range thresholding 
for red (due to red hue spanning across the HSV hue boundary) and standard 
single-range for other colors like blue or green. The result is shown in 
real-time alongside the original image and HSV image.

Usage:
    - Adjust sliders for lower and upper HSV bounds to isolate the desired color region.
    - For 'red', additional sliders will appear to cover the hue wraparound effect.
    - Press 'q' to quit the interactive window.

Args:
    image_file (str): Path to the image to be processed.
    color (str): Target color for thresholding. Supports 'red', 'blue', or 'green'.

Dependencies:
    - OpenCV
    - NumPy

Note:
    You can uncomment `cv2.resize` if you wish to normalize image resolution for consistent tuning.
"""

import cv2
import numpy as np


#image_file = "BildsequenzTest_0/Calibration/feldweg_2.png"
#image_file = "BildsequenzTest_0/Calibration/combined.png"
image_file = "BildsequenzTest_0/Calibration/frame_1_1.jpg"
color = "blue"  # Change to "blue" or "green" as needed

def nothing(x):
    pass

image = cv2.imread(image_file)
#image = cv2.resize(image, (1920, 1080))
hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)

cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)  # Make it resizable
cv2.resizeWindow("Frame", 800, 600)  

cv2.createTrackbar("L-H", "Frame", 0, 180, nothing)
cv2.createTrackbar("L-S", "Frame", 0, 255, nothing)
cv2.createTrackbar("L-V", "Frame", 0, 255, nothing)
cv2.createTrackbar("U-H", "Frame", 180, 180, nothing)
cv2.createTrackbar("U-S", "Frame", 255, 255, nothing)
cv2.createTrackbar("U-V", "Frame", 255, 255, nothing)

if color == "red":
    cv2.createTrackbar("L2-H", "Frame", 0, 180, nothing)
    cv2.createTrackbar("L2-S", "Frame", 0, 255, nothing)
    cv2.createTrackbar("L2-V", "Frame", 0, 255, nothing)
    cv2.createTrackbar("U2-H", "Frame", 180, 180, nothing)
    cv2.createTrackbar("U2-S", "Frame", 255, 255, nothing)
    cv2.createTrackbar("U2-V", "Frame", 255, 255, nothing)


while True:
    
    l_h = cv2.getTrackbarPos("L-H", "Frame")
    l_s = cv2.getTrackbarPos("L-S", "Frame")
    l_v = cv2.getTrackbarPos("L-V", "Frame")

    u_h = cv2.getTrackbarPos("U-H", "Frame")
    u_s = cv2.getTrackbarPos("U-S", "Frame")
    u_v = cv2.getTrackbarPos("U-V", "Frame")

    if color == "red":
        l_h2 = cv2.getTrackbarPos("L2-H", "Frame")
        l_s2 = cv2.getTrackbarPos("L2-S", "Frame")
        l_v2 = cv2.getTrackbarPos("L2-V", "Frame")

        u_h2 = cv2.getTrackbarPos("U2-H", "Frame")
        u_s2 = cv2.getTrackbarPos("U2-S", "Frame")
        u_v2 = cv2.getTrackbarPos("U2-V", "Frame")

    lower_red1 = np.array([l_h, l_s, l_v])
    upper_red1 = np.array([u_h, u_s, u_v])

    if color == "red":
        lower_red2 = np.array([l_h2, l_s2, l_v2])
        upper_red2 = np.array([u_h2, u_s2, u_v2])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)
        mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]

        result = cv2.bitwise_and(image, image, mask=mask)

    else:
        mask = cv2.inRange(hsv, lower_red1, upper_red1)

    cv2.imshow("image", image)
    cv2.imshow("mask", mask)
    cv2.imshow("hsv", hsv)
    
    key = cv2.waitKey(1) & 0xFF
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cv2.destroyAllWindows()

