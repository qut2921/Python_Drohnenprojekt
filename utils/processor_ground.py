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
    This function is used for post-processing of the images that have been shot
    and saved along with the telemetry data. This function is used in mission 1
    """

    # Capture frame
    frame = cv2.imread(output_dir + '/' + image_name)

    # Sharpen image using unsharp masking
    frame = unsharp_masking(frame)

    # Convert frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    return hsv, frame


def unsharp_masking(image):
    """Apply unsharp masking to enhance image details."""

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
    Locate the object in the frame based on the specified color profile.
    This function is used for post-processing of the images that have been shot
    and saved along with the telemetry data. This function is used in mission1.
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
                        f"{output_dir}, {image_filename}, {object_id}, {name}, {shape}, {lat_object:.6f}, {long_object:.6f}\n")

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
    Draw a rectangle around the detected object and add text with its coordinates.
    If the text goes out of bounds, adjust its position and color.
    """

    # Set text properties
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.8
    thickness = 2
    text_colour = (0, 0, 255)  # Red

    # Write text and get width and size
    text = f"{name}, ({latitude:.6f} lat, {longitude:.6f} long, area: {area}, id: {object_id})"
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
    After acquiring the images, this function processes and locates
    the object by reading the CSV files. In case an object is located, a 
    second CSV files with the GPS object coordinates is created.
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

            base_path = '/media/aviator/INTENSO/'
            output_dir = output_dir.replace(base_path, '')
            

            # Read the image and convert it to HSV color space
            hsv, frame = read_image_and_convert(output_dir, image_filename)
            detectedObject = False

            # Save every color in a separate directory
            output_dir = change_output_and_create_folder()

            # Locate the object and save locations in CSV file
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
        
