import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import cv2
import numpy as np
import utils.processor_ground as processor
import utils.colors as colors


def create_roi(hsv, x, y, w, h):
    """
    Create a Region of Interest (ROI) from the image.
    
    Args:
        image: The input image.
        x: The x-coordinate of the top-left corner of the ROI.
        y: The y-coordinate of the top-left corner of the ROI.
        w: The width of the ROI.
        h: The height of the ROI.
    
    Returns:
        The cropped image representing the ROI.
    """
    return hsv[y:y+h, x:x+w]


def detect_shape(frame, hsv,x, y, w, h, color, condition):
    shape = "Unknown"
    roi_hsv = create_roi(hsv, x, y, w, h)
    roi = create_roi(frame, x, y, w, h)

    if color == 0:
        _, lower_black, upper_black = colors.set_colorProfiles(5, condition)
        black_mask = cv2.inRange(roi_hsv, lower_black, upper_black)
        black_mask = processor.remove_noise(black_mask)
    else:
        _, lower_black, upper_black = colors.set_colorProfiles(6, condition)
        black_mask = cv2.inRange(roi_hsv, lower_black, upper_black)
                
    contours_black, _ = cv2.findContours(black_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours_black:
        biggest = sorted(contours_black, key=cv2.contourArea, reverse=True)[0]

                

        if cv2.contourArea(biggest) >= 300:
            epsilon = 0.03*cv2.arcLength(biggest, True)
            approx = cv2.approxPolyDP(biggest, epsilon, True)

            cv2.drawContours(roi, [biggest], 0, (0, 255, 0), 2)

            x_black, y_black, w_black, h_black = cv2.boundingRect(approx)                        
            x_black_mid = int(x_black + w_black / 3)+x
            y_black_mid = int(y_black + h_black / 1.5)+y

            coords = (x_black_mid, y_black_mid)
            colour_text = (0, 0, 255)  # Red
            font = cv2.FONT_HERSHEY_DUPLEX

            if len(approx) == 3:
                shape = "Triangle"
                cv2.putText(frame, "Triangle", coords, font, 0.5, colour_text, 1)
                print("Dreieck erkannt")
            elif len(approx) == 4:
                shape = "Rectangle"
                cv2.putText(frame, "Rectangle", coords, font, 0.5, colour_text, 1)
                print("Rechteck erkannt")
            else:
                shape = "Circle"
                cv2.putText(frame, "Circle", coords, font, 0.5, colour_text, 1)
                print("Kreis erkannt")

            frame[y:y+h, x:x+w] = roi
        
    
    return frame, shape