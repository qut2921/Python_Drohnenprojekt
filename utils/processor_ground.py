"""This module is used for post-processing of the images that have been shot
and saved along with the telemetry data. It includes functions to read images,
locate objects, and save processed images. It is used on the ground computer.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np
import cv2
import utils.colors as colors
import utils.gps_calculator as gps
import utils.shape_detector as sd
import utils.list_filter as lf


def read_image_and_convert(output_dir, image_name):
    """
    Read a frame from the video capture and convert it to HSV color space.
    Then sharpen the image using unsharp masking, which enhances the details
    distorted by vibrations and other factors. Then, conver the image to HSV
    color space, which is used for color-based object detection.

    Args:
        output_dir: The directory where the image is saved.
        image_name: The name of the image file to be processed.

    Returns:
        hsv: The image converted to HSV color space.
        frame: The original image frame after sharpening.
    """

    # Capture frame
    frame = cv2.imread(output_dir + '/' + image_name)

    # Sharpen image using unsharp masking
    frame = unsharp_masking(frame)

    # Convert frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    return hsv, frame


def unsharp_masking(image):
    """
    Apply unsharp masking to enhance image details.
    
    Args:
        image: The input image to be sharpened.

    Returns:
        sharpened: The sharpened image.
    """

    # Create a Gaussian blur of the image
    blurred = cv2.GaussianBlur(image, (9, 9), 10.0)

    # Subtract the blurred image from the original image
    sharpened = cv2.addWeighted(image, 1.5, blurred, -0.5, 0)

    return sharpened


def locate_object_and_save(
        output_dir, image_filename,
        colorProfile, condition, hsv,
        frame, min_area, detectedObject,
        pitch, roll, altitude, heading, lat_position, long_position, object_id):
    
    """
    Processes a saved image and its associated telemetry data to detect objects 
    of a specific color, classify their shape, determine their GPS position, 
    and log the results.

    This function is intended for post-processing during Mission 1. It segments 
    the image using a specified HSV color profile to detect colored objects. 
    If contours meet the specified area threshold, it calculates GPS coordinates 
    using telemetry data, identifies the shape using a dedicated shape-detection 
    routine, draws annotations onto the frame, and writes detection data to a CSV file.

    Args:
        output_dir: Directory path to store the processed data and CSV file.
        image_filename: Name of the input image file being processed.
        colorProfile: Integer code representing which color profile to use.
        condition: Contextual data used for color profile adjustment.
        hsv: The HSV-converted version of the original frame.
        frame: The original BGR image frame for drawing annotations.
        min_area: Minimum area threshold for an object to be considered valid.
        detectedObject (bool): Flag indicating if an object was detected in the current image.
        pitch: Pitch angle from telemetry data.
        roll: Roll angle from telemetry data.
        altitude: Altitude in meters at the time the image was captured.
        heading: Compass heading in degrees.
        lat_position: Latitude of the capture location.
        long_position: Longitude of the capture location.
        object_id: Counter for uniquely identifying detected objects.

    Returns:
        tuple:
            - frame: The annotated image with bounding boxes and labels.
            - object_id: Updated object ID counter after processing.
    """
    # mask for the specified color profile
    if colorProfile == 1:
        name, lower_red1, upper_red1 = colors.set_colorProfiles(1, condition)
        name, lower_red2, upper_red2 = colors.set_colorProfiles(3, condition)
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)
        mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)[1]

    else:
        name, hsv_lower, hsv_upper = colors.set_colorProfiles(colorProfile, condition)
        mask = cv2.inRange(hsv, hsv_lower, hsv_upper)

    print(f"Processing {name}...")

    # remove noise from mask
    # mask = remove_noise(mask)

    # find contours in the mask
    contours, _ = cv2.findContours(
        mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if contours:
        for cnt in contours:
            area = cv2.contourArea(cnt)

            # Check if area is larger than minimum area
            if area >= min_area:
                object_id += 1
                x, y, w, h = cv2.boundingRect(cnt)

                # calculate GPS coordinates
                x_distance, y_distance, lat_object, long_object, n_ned, e_ned = gps.calculate_gps(
                    x,
                    y,
                    w,
                    h,
                    pitch,
                    roll,
                    altitude,
                    heading,
                    lat_position,
                    long_position,
                    frame,)

                frame, shape = sd.detect_shape(frame, hsv, x, y, w, h, colorProfile, condition)

                # draw rectangle and text
                frame = draw_rectangle_with_text(
                    frame,
                    name,
                    x,
                    y,
                    w,
                    h,
                    lat_object,
                    long_object,
                    shape,
                    area,
                    object_id
                )

                with open(f"{output_dir}/image_processed.csv", "a") as processed_log_file:
                    processed_log_file.write(
                        f"{output_dir},processed_{image_filename},{object_id},{name},{shape},{lat_object:.6f},{long_object:.6f},{lat_position:.6f},{long_position:.6f}\n")

                if detectedObject == False:
                    detectedObject = True
                    print(f"Object detected")
            else:
                # Reset flag if area is too small
                detectedObject = False
    else:
        # Reset flag if no contours are found
        detectedObject = False

    return frame, object_id


def change_output_and_create_folder():
    """Create a directory for saving processed images.
    A separate directory is used to store all processed images.
    """

    output_dir = f"Mission1/Found_Object"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("Creating directory" + output_dir + "...")
    return output_dir


def draw_rectangle_with_text(
        frame, name, x, y, w, h,
        latitude, longitude, shape, area, object_id):
    """
        Draws a yellow bounding rectangle around a detected object and annotates it with text
        containing the object's name and unique ID. If the annotation would fall outside the
        image bounds, the position and color of the text are adjusted accordingly.

        Args:
            frame: The image on which to draw.
            name: The label or color name of the detected object.
            x: X-coordinate of the top-left corner of the object bounding box.
            y: Y-coordinate of the top-left corner of the object bounding box.
            w: Width of the bounding box.
            h: Height of the bounding box.
            latitude: GPS latitude of the object (unused in this function).
            longitude: GPS longitude of the object (unused in this function).
            shape: The detected shape of the object (unused in this function).
            area: The area of the detected contour (unused in this function).
            object_id: A unique identifier for the object.

        Returns:
            frame: The frame with the annotated bounding box and text.

        Notes:
            - latitude, longitude, area and shape will not be displayed in the
                frame with current configuration
        """


    # Set text properties
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 3
    thickness = 3
    text_colour = (0, 0, 255)  # Red

    # Write text and get width and size
    text = f"{name}, id: {object_id}"
    (text_width, text_height), _ = cv2.getTextSize(text, font, scale, thickness)

    # Set default text position
    text_x = x
    text_y = y - 10

    # Adjust text position if it goes out of bounds
    if text_x + text_width > frame.shape[1]:
        text_x = frame.shape[1] - text_width - 10
        text_colour = (0, 0, 255)  # red

    if text_y - text_height < 0:
        text_y = y + h + text_height + 5
        text_colour = (0, 0, 255)  # red

    # Draw rectangle and text
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
    cv2.putText(
        frame, text, (text_x, text_y),
        font, scale, text_colour, thickness)

    return frame


def remove_noise(mask):
    """Remove noise from the mask using morphological operations."""

    kernel = np.ones((5, 5), np.uint8)

    # Remove small dots
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Fill small holes
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask


def main_mission_1_post_processing(sequence, condition, min_area):
    """
    Executes post-processing for a sequence of captured images by locating colored objects,
    calculating their GPS coordinates, and logging them to a CSV file.

    The function loops through multiple image sequences containing saved telemetry data.
    For each image, it reads its associated metadata, processes the image by detecting objects 
    of different color profiles, and annotates them with bounding boxes. If objects are found 
    that exceed a specified minimum area, their location is determined using telemetry input,
    and a new CSV file is updated with their GPS coordinates and attributes.

    Args:
        sequence (int): Number of image sequences to process.
        condition (Any): Parameter for adjusting color thresholds dynamically.
        min_area (float): Minimum contour area required to consider an object valid.

    Notes:
        - Each sequence corresponds to a directory containing image and telemetry data.
        - Images are annotated, saved, and an additional CSV file is created if any valid
          object is found.
        - The function supports up to 3 color profiles (skipping index 3 in the loop).
    """

    object_id = 0
    
    # Read the CSV file with telemetry data
    for i in range(sequence+1):
        with open(f"Mission1/Bildsequenz_{i}/image_saved.csv", "r") as log_file:
            lines = log_file.readlines()
        print(f"Processing sequence {i}...")
        # Process each line in the CSV file
        
        for line in lines:
            # Split the line at ", "" to extract data
            output_dir, image_filename, pitch, roll, altitude, heading, lat_position, long_position = line.strip().split(", ")

            # Convert into float values
            pitch, roll, altitude, heading, lat_position, long_position = float(pitch), float(
                roll), float(altitude), float(heading), float(lat_position), float(long_position)

            # Remove OS save path of Raspberry Pi
            base_path = '/media/aviator/INTENSO/'
            output_dir = output_dir.replace(base_path, '')
            
            # Read the image and convert it to HSV color space
            hsv, frame = read_image_and_convert(output_dir, image_filename)
            detectedObject = False

            # Save every processed frame in seperate directory
            output_dir = change_output_and_create_folder()

            # Locate the object and save locations in CSV file
            # Loop through colors blue, red, yellow
            for i in range(4):
                if i == 3:
                    continue
                colorProfile = i
                frame, object_id = locate_object_and_save(
                    output_dir,
                    image_filename,
                    colorProfile,
                    condition,
                    hsv,
                    frame,
                    min_area,
                    detectedObject,
                    pitch,
                    roll,
                    altitude,
                    heading,
                    lat_position,
                    long_position,
                    object_id
            )

            # Save the processed image
            cv2.imwrite(output_dir + '/processed_' + image_filename, frame)
            print("Captured frame...")
        
