"""
Interactive Canny Edge Detection Threshold Tuning using OpenCV.

This script loads a grayscale image and allows the user to interactively adjust the 
lower and upper thresholds for the Canny edge detector using OpenCV trackbars. The resulting 
edges are displayed in real-time alongside the original image, allowing for fine-tuned visual 
exploration of edge detection parameters.

Features:
    - Two trackbars ("L-THRES", "H-THRES") control the Canny threshold values.
    - Displays original and edge-detected images in separate windows.
    - Resizable GUI window for flexibility across screen sizes.
    - Press 'q' to exit the window loop.

Dependencies:
    - OpenCV
    - NumPy

Note:
    - The input image is read from the path specified in `image_file`.
    - The grayscale conversion uses `cv2.COLOR_RGB2GRAY`, assuming the image is loaded in RGB order.
"""
import cv2
import numpy as np


image_file = "BildsequenzTest_0/frame_0_2.jpg"


def nothing(x):
    pass


image = cv2.imread(image_file)
hsv = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

cv2.namedWindow("Frame", cv2.WINDOW_NORMAL)  # Make it resizable


cv2.createTrackbar("L-THRES", "Frame", 0, 255, nothing)
cv2.createTrackbar("H-THRES", "Frame", 0, 255, nothing)


while True:

    l_thres = cv2.getTrackbarPos("L-THRES", "Frame")
    h_thres = cv2.getTrackbarPos("H-THRES", "Frame")

    edges = cv2.Canny(image, l_thres, h_thres)

    cv2.imshow("image", image)
    cv2.imshow("edges", edges)

    key = cv2.waitKey(1) & 0xFF
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


cv2.destroyAllWindows()
