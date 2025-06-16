"""This module provides functions to set color profiles for object detection.
It defines a function `set_colorProfiles` that returns the name and HSV bounds for different colors.
It is used for the image proccesing module that is used in the Raspberry Pi and for
the post-processing of the images that is done on the ground computer."""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def set_colorProfiles(n, condition):
    """Set color profiles for object detection.

    n: 0: blue, 1: red, 2: yellow, 3: red2
    """

    if condition == "cloudy":
        if n == 0:
            name = "Blau"
            hsv_lower = (0, 216, 69)
            hsv_upper = (24, 255, 255)
            return (name, hsv_lower, hsv_upper)

        if n == 1:
            name = "Rot"
            hsv_lower = (116, 115, 61)
            hsv_upper = (180, 255, 255)
            return (name, hsv_lower, hsv_upper)

        if n == 2:
            name = "Gelb"
            hsv_lower = (62, 31, 69)
            hsv_upper = (84, 160, 255)
            return (name, hsv_lower, hsv_upper)

        if n == 3:
            name = "Rot2"
            hsv_lower = (180, 255, 0)
            hsv_upper = (180, 255, 255)
            return (name, hsv_lower, hsv_upper)

        if n == 4:
            name = "Orange"
            hsv_lower = (101, 126, 0)
            hsv_upper = (180, 255, 255)
            return (name, hsv_lower, hsv_upper)
        
        if n == 5:
            name = "Black Blue"
            hsv_lower = (0, 0, 0)
            hsv_upper = (13, 204, 255)
            return (name, hsv_lower, hsv_upper)
        
        if n == 6:
            name = "Black Other"
            hsv_lower = (0, 0, 0)
            hsv_upper = (27, 255, 255)
            return (name, hsv_lower, hsv_upper)
    
    elif condition == "sunny":
        if n == 0:
            name = "Blau"
            hsv_lower = (0, 216, 69)
            hsv_upper = (24, 255, 255)
            return (name, hsv_lower, hsv_upper)

        if n == 1:
            name = "Rot"
            hsv_lower = (130, 0, 0)
            hsv_upper = (0, 255, 255)
            return (name, hsv_lower, hsv_upper)

        if n == 2:
            name = "Gelb"
            hsv_lower = (62, 31, 69)
            hsv_upper = (84, 160, 255)
            return (name, hsv_lower, hsv_upper)

        if n == 3:
            name = "Rot2"
            hsv_lower = (118, 0, 125)
            hsv_upper = (180, 255, 255)
            return (name, hsv_lower, hsv_upper)

        if n == 4:
            name = "Orange"
            hsv_lower = (102, 0, 137)
            hsv_upper = (113, 255, 255)
            return (name, hsv_lower, hsv_upper)
        
    else:
        raise ValueError("Invalid condition. Must be 'cloudy' or 'sunny'.")

