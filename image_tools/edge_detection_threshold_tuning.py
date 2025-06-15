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