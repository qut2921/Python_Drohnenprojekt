"""This module provides functions for image processing within the drone.
It is used with Raspberry Pi 5 and contains functions to set the camera
controls for Camera Module 3. Also main functions for the missions are defined.

A separate module is used for post-processing of the images that have been shot
and saved along with the telemetry data.
"""

from picamera2 import Picamera2, Preview
import utils.gps_calculator as gps
import utils.colors as colors
import control.logging as log
import control.communicator as cm
import asyncio
from picamera2.controls import Controls
import numpy as np  # type:ignore
import cv2  # type:ignore
import time  # type:ignore
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def set_sensor_properties():
    """Set sensor properties for the camera."""

    frame_width = 1920  # Maximum is 4608
    frame_height = 1080  # Maximum 2592

    camera_config = {"size": (frame_width, frame_height), "format": "RGB888"}
    # camera_config = {"size": (frame_width, frame_height), "format": "YUV420"}

    return camera_config


def set_camera_controls(vid, logfile):

    exposure_time = 2500  # Exposure time in microseconds (e.g., 2500 �s = 2.5ms)
    vid.set_controls({
        "AeEnable": False,              # Disable auto exposure
        # Set exposure time in microseconds (e.g., 10000 �s = 10ms)
        "ExposureTime": exposure_time,
        # Set the analog gain (1.0 is default, usually between 1 and 16)
        "AnalogueGain": 1.0
    })
    log.log(f"Changed Camera Settings! Exposure:{exposure_time}", logfile)


def set_camera_controls2(vid, logfile):

    exposure_time = 1500  # Exposure time in microseconds (e.g., 1500 �s = 1.5ms)
    vid.set_controls({
        "AeEnable": False,              # Disable auto exposure
        # Set exposure time in microseconds (e.g., 10000 �s = 10ms)
        "ExposureTime": exposure_time,
        # Set the analog gain (1.0 is default, usually between 1 and 16)
        "AnalogueGain": 1.0
    })

    log.log(f"Changed Camera Settings! Exposure:{exposure_time}", logfile)


def set_camera_controls3(vid, logfile):
    exposure_time = 1000  # Exposure time in microseconds (e.g., 1000 �s = 1ms)
    vid.set_controls({
        "AeEnable": False,              # Disable auto exposure
        # Set exposure time in microseconds (e.g., 10000 �s = 10ms)
        "ExposureTime": exposure_time,
        # Set the analog gain (1.0 is default, usually between 1 and 16)
        "AnalogueGain": 1.0
    })
    log.log(f"Changed Camera Settings! Exposure:{exposure_time}", logfile)


def start_videoCapture(mission_id, logfile):
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
        # vid.start_preview(Preview.QTGL)
        log.log("Mission 1 Preview configuration set", logfile)

    elif mission_id == 2 or mission_id == 3:
        config = vid.create_still_configuration(main=set_sensor_properties())
        # config = vid.create_preview_configuration(main=set_sensor_properties())
        # vid.start_preview(Preview.QTGL)
        vid.configure(config)
        log.log("Mission 2 or 3 Still configuration set", logfile)

    else:
        raise ValueError("Invalid mission ID. Use 1, 2, or 3.")

    # Start camera with settings
    try:
        vid.start()
        log.log("Camera started", logfile)
    except Exception as e:
        log.log(f"Error starting camera: {e}", logfile)

    if mission_id == 1:
        # Set camera controls for mission 1
        set_camera_controls(vid)

    if mission_id == 2:
        set_camera_controls(vid)

    return vid


def stop_videoCapture(vid, logfile):
    vid.stop()
    log.log("Camera stopped successfully", logfile)


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


def locate_object(
        colorProfile, condition, hsv,
        frame, min_area, detectedObject,
        pitch, roll, altitude, heading, lat_position, long_position):
    """
    Locate the object in the frame based on the specified color profile.
    This function is used for post-processing of the images that have been shot
    and saved along with the telemetry data. This function is used in mission1.
    """

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
    
    # remove noise from mask
    # mask = remove_noise(mask)
    
    # find contours in the mask
    contours, _ = cv2.findContours(
        mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    x_distance = None
    y_distance = None

    if contours:
        biggest = sorted(contours, key=cv2.contourArea, reverse=True)[0]
        area = cv2.contourArea(biggest)

        # Check if area is larger than minimum area
        if area >= min_area:
            x, y, w, h = cv2.boundingRect(biggest)

            # calculate GPS coordinates
            x_distance, y_distance, _, _, _, _ = gps.calculate_gps(
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

            return x_distance, y_distance

        else:
            # Reset flag if area is too small
            detectedObject = False

    return x_distance, y_distance


def create_directory(sequence, logfile):
    """Create a directory for saving images.

    sequence: specifies the sequence of image savings based on the mission plan
    """

    output_dir = "/media/aviator/INTENSO/BildsequenzTest_{}".format(sequence)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        log.log("Creating directory" + output_dir + "...", logfile)
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


async def main_mission_1(drone, vid, sequence, logfile):
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
    camera_control_stamp = time.time()
    save_delay = 1  # Save image every 1 seconds
    hover_time = 45
    setting_id = 0

    print("Inside function")

    while True:
        print("In the loop")

        # Telemetry data that will come from the flight controller
        latitude, longitude, altitude, roll, pitch, yaw, _, key = await cm.get_parameters_for_image_processing(drone)

        if key == 1:
            for i in range(10):
                log.log("COMMUNICATION LOST!",logfile)
                asyncio.sleep(0.5)

            break

        # Check if new directory has to be created
        if new_dir == True:
            output_dir = create_directory(sequence, logfile)
            set_camera_controls(vid, logfile)
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
            last_time_saved = time.time()
            image_count += 1
            with open(f"{output_dir}/image_saved.csv", "a") as log_file:
                log_file.write(
                    f"{output_dir}, {image_filename}, {pitch}, {roll}, {altitude}, {yaw}, {latitude}, {longitude}\n")
            print("Captured frame...")

        if time.time() - camera_control_stamp >= 15 and setting_id == 0:
            set_camera_controls2(vid, logfile)
            setting_id += 1

        if time.time() - camera_control_stamp >= 30 and setting_id == 1:
            set_camera_controls3(vid, logfile)
            setting_id += 1

        if time.time() - camera_control_stamp >= hover_time:
            log.log("Image capture finished", logfile)
            break

    return sequence


async def main_mission_2(drone, vid, colorProfile, condition, logfile):

    min_area = 300
    detectedObject = False

    # Telemetry data that will come from the flight controller
    latitude, longitude, altitude, roll, pitch, yaw, _, key = await cm.get_parameters_for_image_processing(drone)

    if key == 1:
        print("COMMUNICATION LOST!")
        return

    hsv, frame = capture_and_convert(vid)

    x_distance, y_distance = locate_object(
        colorProfile,
        condition,
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

    log.log(f"Object found at x: {x_distance}, y: {y_distance}", logfile)

    if x_distance == None or y_distance == None:
        log.log("No object found!", logfile)

    return x_distance, y_distance
