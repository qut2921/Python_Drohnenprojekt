"""This module provides functions to set color profiles for object detection.
It defines a function `set_colorProfiles` that returns the name and HSV bounds for different colors.
It is used for the image proccesing module that is used in the Raspberry Pi and for
the post-processing of the images that is done on the ground computer.
A parameter `condition` is used to set the color profiles for different weather conditions.
In the project work, the the color profiles are used for both conditions "cloudy" and "sunny"
due to simplicity. If desired, the color profiles can be adjusted for different conditions."""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def set_colorProfiles(n, condition):
    """Set color profiles for object detection.

    Args:
        n: 0: blue, 1: red, 2: yellow, 3: red2
        condition: "cloudy" or "sunny"

    Returns:
        (name, hsv_lower, hsv_upper):
        A tuple containing the name and HSV bounds for the specified color profile.
        Name is a string representing the color,
        hsv_lower is a tuple representing the lower HSV bounds,
        hsv_upper is a tuple representing the upper HSV bounds.
    """

    if condition == "cloudy":
        if n == 0:
            name = "Blue"
            hsv_lower = (0, 167, 0)
            hsv_upper = (10, 255, 255)
            return (name, hsv_lower, hsv_upper)

        if n == 1:
            name = "Red"
            hsv_lower = (113, 67, 0)
            hsv_upper = (180, 255, 255)
            return (name, hsv_lower, hsv_upper)

        if n == 2:
            name = "Yellow"
            hsv_lower = (72, 52, 69)
            hsv_upper = (90, 160, 255)
            return (name, hsv_lower, hsv_upper)

        if n == 3:
            name = "Red"
            hsv_lower = (180, 255, 0)
            hsv_upper = (180, 255, 255)
            return (name, hsv_lower, hsv_upper)

        if n == 4:
            name = "Orange"
            hsv_lower = (102, 40, 0)
            hsv_upper = (116, 255, 255)
            return (name, hsv_lower, hsv_upper)
        
        if n == 5:
            name = "Black Blue"
            hsv_lower = (9, 0, 0)
            hsv_upper = (15, 225, 255)
            return (name, hsv_lower, hsv_upper)
        
        if n == 6:
            name = "Black Other"
            hsv_lower = (0, 0, 0)
            hsv_upper = (31, 255, 255)
            return (name, hsv_lower, hsv_upper)
    

    elif condition == "sunny":
        if n == 0:
            name = "Blue"
            hsv_lower = (0, 167, 0)
            hsv_upper = (10, 255, 255)
            return (name, hsv_lower, hsv_upper)

        if n == 1:
            name = "Red"
            hsv_lower = (113, 67, 0)
            hsv_upper = (180, 255, 255)
            return (name, hsv_lower, hsv_upper)

        if n == 2:
            name = "Yellow"
            hsv_lower = (64, 68, 69)
            hsv_upper = (94, 160, 255)
            return (name, hsv_lower, hsv_upper)

        if n == 3:
            name = "Red"
            hsv_lower = (6, 0, 0)
            hsv_upper = (0, 255, 255)
            return (name, hsv_lower, hsv_upper)

        if n == 4:
            name = "Orange"
            hsv_lower = (102, 140, 0)
            hsv_upper = (116, 255, 255)
            return (name, hsv_lower, hsv_upper)
        
        if n == 5:
            name = "Black Blue"
            hsv_lower = (9, 0, 0)
            hsv_upper = (15, 225, 255)
            return (name, hsv_lower, hsv_upper)
        
        if n == 6:
            name = "Black Other"
            hsv_lower = (0, 0, 0)
            hsv_upper = (31, 255, 255)
            return (name, hsv_lower, hsv_upper)
        
    else:
        raise ValueError("Invalid condition. Must be 'cloudy' or 'sunny'.")

def map_color_to_id(color):
    """Map color names to IDs. This is used as part of the webserver which
    utilizes a GUI to start the mission scripts. For various functions, the color
    is represented by an ID, which is used to identify the color in the code.
    In the GUI, the color is represented by a string.
    
    Args:
        color (str): The color name as a string. Must be one of "blue", "red", "yellow", or "orange".

    Returns:
        int: The ID corresponding to the color.
    """
    
    if color == "blue":
        return 0
    elif color == "red":
        return 1
    elif color == "yellow":
        return 2
    elif color == "orange":
        return 4
    else:
        raise ValueError("Invalid color. Must be 'blue', 'red', 'yellow', or 'orange'.")