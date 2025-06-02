"""
This module contains functions for image processing using OpenCV and the 
Picamera2 library.
It includes functions for capturing images, converting color spaces,
locating objects based on color profiles, and saving images with telemetry data.
Depending on the mission different functions are used to process the images."""

import os
import time  # type:ignore
import cv2  # type:ignore
import numpy as np  # type:ignore
from picamera2 import Picamera2, Preview
from picamera2.controls import Controls
import asyncio
import control.communicator as cm


def set_colorProfiles(n):
    """Set color profiles for object detection.

    n: 0: blue, 1: red, 2: yellow, 3: red2
    """

    if n == 0:
        name = "Blau"
        hsv_lower = (90, 50, 50)
        hsv_upper = (130, 255, 255)
        return (name, hsv_lower, hsv_upper)

    if n == 1:
        name = "Rot"
        hsv_lower = (160, 100, 100)
        hsv_upper = (180, 255, 255)
        return (name, hsv_lower, hsv_upper)

    if n == 2:
        name = "Gelb"
        hsv_lower = (15, 100, 100)
        hsv_upper = (35, 255, 255)
        return (name, hsv_lower, hsv_upper)

    if n == 3:
        name = "Rot2"
        hsv_lower = (0, 100, 100)
        hsv_upper = (12, 255, 255)
        return (name, hsv_lower, hsv_upper)
    
    if n == 4:
        name = "Orange"
        hsv_lower = (0, 100, 100)
        hsv_upper = (12, 255, 255)
        return (name, hsv_lower, hsv_upper)


def set_sensor_properties():
    """Set sensor properties for the camera."""

    frame_width = 1920  # Maximum is 4608
    frame_height = 1080  # Maximum 2592

    camera_config = {"size": (frame_width, frame_height), "format": "RGB888"}
    # camera_config = {"size": (frame_width, frame_height), "format": "YUV420"}

    return camera_config


def set_camera_controls(vid):

    vid.set_controls({
        "AeEnable": False,              # Disable auto exposure
        # Set exposure time in microseconds (e.g., 10000 �s = 10ms)
        "ExposureTime": 500,
        # Set the analog gain (1.0 is default, usually between 1 and 16)
        "AnalogueGain": 1.0
    })


def set_camera_controls2(vid):

    vid.set_controls({
        "AeEnable": False,              # Disable auto exposure
        # Set exposure time in microseconds (e.g., 10000 �s = 10ms)
        "ExposureTime": 1000,
        # Set the analog gain (1.0 is default, usually between 1 and 16)
        "AnalogueGain": 1.0
    })


def set_camera_controls3(vid):

    vid.set_controls({
        "AeEnable": False,              # Disable auto exposure
        # Set exposure time in microseconds (e.g., 10000 �s = 10ms)
        "ExposureTime": 1500,
        # Set the analog gain (1.0 is default, usually between 1 and 16)
        "AnalogueGain": 1.0
    })


def start_videoCapture(mission_id):
    """
    Set frame properties and start video capture.
    For mission 1 the camera is set to preview mode, while for mission 2 and 3
    the camera is set to video mode for higher frame rates, as the objects
    have to be detected in real time.
    The funciton also sets camera controls for the image capture in mission 1.
    """

    # Initialize tuning file
    tuning = Picamera2.load_tuning_file("imx708.json")
    vid = Picamera2(tuning=tuning)

    # depending on the mission id, different settings are used
    if mission_id == 1:
        config = vid.create_preview_configuration(main=set_sensor_properties())
        vid.configure(config)
        #vid.start_preview(Preview.QTGL)
        

    elif mission_id == 2 or mission_id == 3:
        config = vid.create_video_configuration(main=set_sensor_properties())
        vid.configure(config)
        print

    else:
        raise ValueError("Invalid mission ID. Use 1, 2, or 3.")

    # Start camera with settings
    vid.start()
    print("Camera started")

    if mission_id == 1:
        # Set camera controls for mission 1
        set_camera_controls(vid)

    return vid


def capture_and_convert(vid):
    """
    Read a frame from the video capture and convert it to HSV color space.
    This function is used for live detection of the objects. Especially in 
    mission 2 and 3 it is useful, where the position of the object is used to 
    generate control inputs
    """

    # Capture frame
    frame = vid.capture_array()
    # Convert frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
    return hsv, frame


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


def calculate_gps(
        rect_x, rect_y, rect_w, rect_h,
        pitch, roll, altitude, heading,
        lat_position, long_position, frame):
    """Calculate GPS coordinates based on the rectangle position and telemetry data.

    rect_x, rect_y: coordinates of the rectangle

    rect_w, rect_h: width and height of the rectangle

    pitch, roll: telemetry data for pitch and roll

    altitude: telemetry data for altitude

    heading_: telemetry data for heading

    lat_position: current GPS position

    long_position: current GPS position

    frame: current frame from the video capture
    """

    # Get rectangle center coordinates
    pixel_x = rect_x + (rect_w / 2)  # [pixel]
    pixel_y = rect_y + (rect_h / 2)  # [pixel]

    # Camera sensor properties
    FOV_horizontal = 66  # [degrees]
    FOV_vertical = 41  # [degrees]

    # Get frame dimensions
    frame_height, frame_width = frame.shape[:2]

    # Calculate trigonometric angles to calculate distances
    delta = FOV_horizontal * \
        ((pixel_x / frame_width) - 0.5) + pitch  # [degrees]
    epsilon = FOV_vertical * \
        ((pixel_y / frame_height) - 0.5) - roll  # [degrees]

    # Calculate distances in frame coordinate system
    x_distance = altitude * np.tan(np.radians(delta))  # [m]
    y_distance = altitude * np.tan(np.radians(epsilon))  # [m]

    # Transform to NED coordinate system by rotating the frame around heading
    # Calculate distances in NED coordinate system
    n_ned = x_distance * np.cos(np.radians(heading)) - \
        y_distance * np.sin(np.radians(heading))  # [m]
    e_ned = x_distance * np.sin(np.radians(heading)) + \
        y_distance * np.cos(np.radians(heading))  # [m]

    # Calculate GPS coordinates for small distances https://kompf.de/gps/distcalc.html
    delta_lat = n_ned / 111320  # [degrees]
    delta_lon = e_ned / \
        (111320 * np.cos(np.radians(lat_position)))  # [degrees]
    lat_object = lat_position + delta_lat  # [degrees]
    lon_object = long_position + delta_lon  # [degrees]

    return x_distance, y_distance, lat_object, lon_object, n_ned, e_ned


def remove_noise(mask):
    """Remove noise from the mask using morphological operations."""

    kernel = np.ones((5, 5), np.uint8)

    # Remove small dots
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

    # Fill small holes
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask


def unsharp_masking(image):
    """Apply unsharp masking to enhance image details."""

    # Create a Gaussian blur of the image
    blurred = cv2.GaussianBlur(image, (9, 9), 10.0)

    # Subtract the blurred image from the original image
    sharpened = cv2.addWeighted(image, 1.5, blurred, -0.5, 0)

    return sharpened


def draw_rectangle_with_text(
        frame, name, x, y, w, h,
        x_distance, y_distance):
    """
    Draw a rectangle around the detected object and add text with its coordinates.
    If the text goes out of bounds, adjust its position and color.
    """

    # Set text properties
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.6
    thickness = 1
    text_colour = (0, 0, 255)  # Red

    # Write text and get width and size
    text = f"{name} ({x}, {y}) ({x_distance:.2f} m, {y_distance:.2f} m)"
    (text_width, text_height), _ = cv2.getTextSize(text, font, scale, thickness)

    # Set default text position
    text_x = x
    text_y = y - 10

    # Adjust text position if it goes out of bounds
    if text_x + text_width > frame.shape[1]:
        text_x = frame.shape[1] - text_width - 10
        text_colour = (255, 0, 0)  # blue

    if text_y - text_height < 0:
        text_y = y + h + text_height + 5
        text_colour = (255, 0, 0)  # blue

    # Draw rectangle and text
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
    cv2.putText(
        frame, text, (text_x, text_y),
        font, scale, text_colour, thickness)

    return frame


def locate_object_and_save(
        output_dir, image_filename,
        colorProfile, hsv,
        frame, min_area, detectedObject,
        pitch, roll, altitude, heading, lat_position, long_position):
    """
    Locate the object in the frame based on the specified color profile.
    This function is used for post-processing of the images that have been shot
    and saved along with the telemetry data. This function is used in mission1.
    """
    # mask for the specified color profile
    name, hsv_lower, hsv_upper = set_colorProfiles(colorProfile)
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)

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
                x, y, w, h = cv2.boundingRect(cnt)

                # calculate GPS coordinates
                x_distance, y_distance, lat_object, long_object, n_ned, e_ned = calculate_gps(
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
                    frame)

                
                # draw rectangle and text
                frame = draw_rectangle_with_text(
                        frame,
                        name,
                        x,
                        y,
                        w,
                        h,
                        x_distance,
                        y_distance)

                with open(f"{output_dir}/image_processed.csv", "a") as processed_log_file:
                    processed_log_file.write(
                        f"{output_dir}, {image_filename}, {x_distance}, {y_distance}, {lat_object}, {long_object}\n")

                if detectedObject == False:
                    detectedObject = True
                    print(f"Object detected")
            else:
                 # Reset flag if area is too small
                detectedObject = False
    else:
    # Reset flag if no contours are found	
     detectedObject = False
               
    return frame


def locate_object(
        colorProfile, hsv,
        frame, min_area, detectedObject,
        pitch, roll, altitude, heading, lat_position, long_position):
    """
    Locate the object in the frame based on the specified color profile.
    This function is used for post-processing of the images that have been shot
    and saved along with the telemetry data. This function is used in mission1.
    """
    # mask for the specified color profile
    _, hsv_lower, hsv_upper = set_colorProfiles(colorProfile)
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)

    # remove noise from mask
    # mask = remove_noise(mask)

    # find contours in the mask
    contours, _ = cv2.findContours(
        mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    e_ned = None
    n_ned = None

    if contours:
        biggest = sorted(contours, key=cv2.contourArea, reverse=True)[0] 
        area = cv2.contourArea(biggest)
        
        # Check if area is larger than minimum area
        if area >= min_area:
            x, y, w, h = cv2.boundingRect(biggest)

                # calculate GPS coordinates
            _, _, _, _, n_ned, e_ned = calculate_gps(
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
                    frame)

            if detectedObject == False:
                    detectedObject = True
                    print(f"Object detected")
            
            return n_ned, e_ned
                    
        else:
             # Reset flag if area is too small
            detectedObject = False
    else:
        # Reset flag if no contours are found
         detectedObject = False
               
    return n_ned, e_ned


def create_directory(sequence):
    """Create a directory for saving images.

    sequence: specifies the sequence of image savings based on the mission plan
    """

    output_dir = "/media/aviator/INTENSO/BildsequenzTest_{}".format(sequence)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("Creating directory" + output_dir + "...")
    return output_dir


def save_image(vid, frame_amount, output_dir, sequence):
    """Save the captured image to the specified directory."""

    still_camera_config = vid.create_still_configuration(
        main=set_sensor_properties())
    # Capture frame
    image_filename = 'frame_{}_{}.jpg'.format(sequence-1, frame_amount)
    vid.switch_mode_and_capture_file(
        still_camera_config, output_dir + '/' + image_filename)
    # cv2.imwrite(output_dir + '/' + image_filename, frame)
    print("Captured frame...")

    return image_filename


def test_velocity():
    """
    Test function to simulate velocity. This function was used to test the 
    functionality of the main modules. It is used to simulate varying velocities.
    A sine function is used to simulate the velocity.
    """
    velocity = 6*np.abs(np.sin(time.time()/4)) + 2  # [m/s]
    print(f"Velocity: {velocity:.2f} m/s")

    return velocity


def main_mission_1_post_processing(sequence, colorProfile, min_area):
    """
    After acquiring the images, this function processes and locates
    the object by reading the CSV files. In case an object is located, a 
    second CSV files with the GPS object coordinates is created.
    """

    # Read the CSV file with telemetry data
    for i in range(sequence):
        with open(f"/media/aviator/INTENSO/BildsequenzTest_{i}/image_saved.csv", "r") as log_file:
            lines = log_file.readlines()

        # Process each line in the CSV file
        for line in lines:
            # Split the line at ", "" to extract data
            output_dir, image_filename, pitch, roll, altitude, heading, lat_position, long_position = line.strip().split(", ")

            # Convert into float values
            pitch, roll, altitude, heading, lat_position, long_position = float(pitch), float(
                roll), float(altitude), float(heading), float(lat_position), float(long_position)

            # Read the image and convert it to HSV color space
            hsv, frame = read_image_and_convert(output_dir, image_filename)
            detectedObject = False

            # Locate the object and save locations in CSV file
            frame = locate_object_and_save(
                output_dir,
                image_filename,
                colorProfile,
                hsv,
                frame,
                min_area,
                detectedObject,
                pitch,
                roll,
                altitude,
                heading,
                lat_position,
                long_position
            )

            # Save the processed image
            cv2.imwrite(output_dir + '/processed_' + image_filename, frame)
            print("Captured frame...")


async def main_mission_1(drone, vid):
    """
    This is the concept for the image processing in Mission 1.
    The function just saves the image after specified time intervals and
    will not locate the object right away. The telemetry data is saved as
    timestamp for each image in order to calculate the distance later
    into a CSV files. 
    """

    # Initialize image saving variables
    new_dir = True
    last_time_saved = time.time()
    save_delay = 1  # Save image every 1 seconds
    sequence = 0

    while True:

        # Telemetry data that will come from the flight controller
        latitude, longitude, altitude, roll, pitch, yaw, status, scalar_velocity, key = await cm.get_parameters_for_image_processing(drone)

        if key == 1:
            for i in range(10):
                print("COMMUNICATION LOST!")
                asyncio.sleep(0.5)
            
            break

        # Check if new directory has to be created
        if scalar_velocity < 2:

            if new_dir == True:
                output_dir = create_directory(sequence)
                
                set_camera_controls(vid)
                camera_control_stamp = time.time()
                
                new_dir = False
                image_count = 0  # Reset numbering for images in new directory
                sequence += 1

            # Only save image every 1 seconds in the directory with
            # neccesary telemetry data
            if time.time() - last_time_saved >= save_delay:
                image_filename = save_image(
                    vid, 
                    image_count, 
                    output_dir, 
                    sequence)
                
            if time.time() - camera_control_stamp >= 15:
                set_camera_controls2(vid)
                print("Changed Camera Settings! Exposure:1000")

            if time.time() - camera_control_stamp >= 30:
                set_camera_controls3(vid)
                print("Changed Camera Settings! Exposure:1500")

                last_time_saved = time.time()
                image_count += 1

                with open(f"{output_dir}/image_saved.csv", "a") as log_file:
                    log_file.write(
                        f"{output_dir}, {image_filename}, {pitch}, {roll}, {altitude}, {yaw}, {latitude}, {longitude}\n")
                print("Captured frame...")

        else:
            new_dir = True

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    vid.stop()
    return sequence


async def main_mission_2(drone, vid, colorProfile):

    min_area = 900
    detectedObject = False

    latitude, longitude, altitude, roll, pitch, yaw, status, scalar_velocity, key = await cm.get_parameters_for_image_processing(drone)

    if key == 1:
        print("COMMUNICATION LOST!")
        return

    hsv, frame = capture_and_convert(vid)

    n_ned, e_ned = locate_object(
        colorProfile,
        hsv,
        frame,
        min_area,
        detectedObject,
        pitch,
        roll,
        altitude,
        yaw,
        latitude,
        longitude
        )

    if n_ned or e_ned == None:
        print("No object found!")

    return n_ned, e_ned
