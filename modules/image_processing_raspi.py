import os
import time  # type:ignore
import cv2  # type:ignore
import numpy as np  # type:ignore
from picamera2 import Picamera2, Preview
from picamera2.controls import Controls
import datetime  # type:ignore
import mavsdk
import asyncio


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


def start_videoCapture():
    """Set frame properties and start video capture."""

    # Set frame dimensions
    frame_width = 1280  # Maximum is 4608
    frame_height = 720  # Maximum 2592

    # Initialize tuning file
    tuning = Picamera2.load_tuning_file("imx708.json")

    # Start video capture and tune
    vid = Picamera2(tuning=tuning)
    config = vid.create_preview_configuration(
        main={"size": (frame_width, frame_height)})
    vid.configure(config)
    vid.start()

    return vid


def capture_and_convert(vid):
    """Read a frame from the video capture and convert it to HSV color space."""

    # Capture frame
    frame = vid.capture_array()
    # Convert frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    return hsv, frame


def read_image_and_convert(output_dir, image_name):
    """Read a frame from the video capture and convert it to HSV color space."""

    # Capture frame
    frame = cv2.imread(output_dir + '/' + image_name)

    # Convert frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
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
        ((pixel_y / frame_height) - 0.5) + roll  # [degrees]

    # Calculate distances in frame coordinate system
    x_distance = altitude * np.tan(np.radians(delta))  # [m]
    y_distance = altitude * np.tan(np.radians(epsilon))  # [m]

    # Transform to NED coordinate system by rotating the frame around heading
    # Calculate distances in NED coordinate system
    n_ned = x_distance * np.cos(np.radians(heading)) + \
        y_distance * np.sin(np.radians(heading))  # [m]
    e_ned = x_distance * np.sin(np.radians(heading)) - \
        y_distance * np.cos(np.radians(heading))  # [m]

    # Calculate GPS coordinates for small distances https://kompf.de/gps/distcalc.html
    delta_lat = n_ned / 111320  # [degrees]
    delta_lon = e_ned / \
        (111320 * np.cos(np.radians(lat_position)))  # [degrees]
    lat_object = lat_position + delta_lat  # [degrees]
    lon_object = long_position + delta_lon  # [degrees]

    return x_distance, y_distance, lat_object, lon_object


def remove_noise(mask):
    """Remove noise from the mask using morphological operations."""
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)  # Remove small dots
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Fill small holes
    return mask


def draw_rectangle_with_text(
        frame, name, x, y, w, h,
        x_distance, y_distance):
    """Draw a rectangle around the detected object and add text with its coordinates.

    If the text goes out of bounds, adjust its position and color."""
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
        font, scale, text_colour, thickness
    )

    return frame


def locate_object(
        colorProfile, hsv, frame, min_area, detectedObject,
        pitch, roll, altitude, heading, lat_position, long_position):
    """Locate the object in the frame based on the specified color profile."""
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
                x_distance, y_distance, _, _ = calculate_gps(
                    x, y, w, h,
                    pitch, roll, altitude, heading,
                    lat_position, long_position, frame
                )

                # draw rectangle and text
                frame = draw_rectangle_with_text(
                    frame, name, x, y, w, h,
                    x_distance, y_distance)

                if detectedObject == False:
                    detectedObject = True
                    print(f"Object detected")
                else:
                    # Reset flag if object is not detected anymore
                    detectedObject = False
            else:
                # Reset flag if area is too small
                detectedObject = False
    return mask, hsv, frame


def locate_object_and_save(
        output_dir, image_filename, colorProfile, hsv,
        frame, min_area, detectedObject,
        pitch, roll, altitude, heading, lat_position, long_position):
    """Locate the object in the frame based on the specified color profile."""
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
                x_distance, y_distance, lat_object, long_object = calculate_gps(
                    x, y, w, h,
                    pitch, roll, altitude, heading,
                    lat_position, long_position, frame
                )

                # draw rectangle and text
                frame = draw_rectangle_with_text(
                    frame, name, x, y, w, h,
                    x_distance, y_distance)

                with open(f"{output_dir}/image_processed.csv", "a") as processed_log_file:
                    processed_log_file.write(
                        f"{output_dir}, {image_filename}, {x_distance}, {y_distance}, {lat_object}, {long_object}\n")

                if detectedObject == False:
                    detectedObject = True
                    print(f"Object detected")
                else:
                    # Reset flag if object is not detected anymore
                    detectedObject = False
            else:
                # Reset flag if area is too small
                detectedObject = False
    return mask, hsv, frame,


def create_directory(sequence):
    """Create a directory for saving images.

    sequence: specifies the sequence of image savings based on the mission plan
    """
    output_dir = "/media/aviator/INTENSO/BildsequenzTest_{}".format(sequence)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("Creating directory" + output_dir + "...")
    return output_dir


def save_image(
        frame, frame_amount, output_dir, sequence):
    """Save the captured image to the specified directory."""
    # Capture frame
    image_filename = 'frame_{}_{}.jpg'.format(sequence-1, frame_amount)
    cv2.imwrite(
        output_dir + '/' + image_filename, frame)
    print("Captured frame...")
    return image_filename


def save_data():
    abc = 0


def test_velocity():
    """Test function to simulate velocity."""
    velocity = 6*np.abs(np.sin(time.time()/4)) + 2  # [m/s]
    print(f"Velocity: {velocity:.2f} m/s")
    return velocity


def module_main_mission_1(
        vid, colorProfile, min_area,
        pitch, roll, altitude, heading, speed, lat_position, long_position
):
    """This is a concept for the image processing in Mission 1.
    The function continously locates the object in the frame and saves the 
    image after specified time intervals.
    The telemetry data is not saved in this version."""
    # Initialize object detection variables
    cv2.startWindowThread()
    detectedObject = False
    speed = speed

    # Initialize image saving variables
    new_dir = True
    last_time_saved = time.time()
    save_delay = 1  # Save image every 1 seconds
    sequence = 0

    while True:

        velocity = test_velocity()
        # Capture frame and convert to HSV
        hsv, frame = capture_and_convert(vid)

        mask, hsv, frame = locate_object(
            colorProfile, hsv, frame, min_area,
            detectedObject, pitch, roll, altitude, heading,
            lat_position, long_position
        )

        # Display the original frame and the grayscale frame
        cv2.putText(frame, f"Berechnung Distanz", (30, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        cv2.imshow('Mask', mask)
        cv2.imshow('HSV', hsv)
        cv2.imshow('Original Frame', frame)

        if velocity < 5:

            # Check if new directory has to be created
            if new_dir == True:
                output_dir = create_directory(sequence)
                new_dir = False
                image_count = 0  # Reset numbering for images in new directory
                sequence += 1

            # Only save image every 1 seconds
            if time.time() - last_time_saved >= save_delay:
                save_image(frame, image_count, output_dir, sequence)
                last_time_saved = time.time()
                image_count += 1

        else:
            new_dir = True

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()


def module_main_mission_1_v2(
        vid, pitch, roll, altitude,
        heading, speed, lat_position, long_position
):
    """This is the second concept for the image processing in Mission 1.
    The function just saves the image after specified time intervals and
    will not locate the object right away. The telemetry data is saved as
    timestamp for each image in order to calculate the distance later
    into a CSV files."""
    # Initialize object detection variables
    speed = speed

    # Initialize image saving variables
    new_dir = True
    last_time_saved = time.time()
    save_delay = 1  # Save image every 1 seconds
    sequence = 0

    while True:
        # Capture frame and convert to HSV
        _, frame = capture_and_convert(vid)
       

        # Telemetry data that will come from the flight controller
        velocity = test_velocity()
        altitude = altitude
        heading = heading
        lat_position = lat_position
        long_position = long_position
        pitch = pitch
        roll = roll

        # Display the original frame and the grayscale frame
        cv2.imshow('Original Frame', frame)

        if velocity < 5:
            # Check if new directory has to be created
            if new_dir == True:
                output_dir = create_directory(sequence)
                new_dir = False
                image_count = 0  # Reset numbering for images in new directory
                sequence += 1

            # Only save image every 1 seconds in the directory with
            # neccesary telemetry data
            if time.time() - last_time_saved >= save_delay:
                image_filename = save_image(
                    frame, image_count, output_dir, sequence)
                last_time_saved = time.time()
                image_count += 1
                with open(f"{output_dir}/image_saved.csv", "a") as log_file:
                    log_file.write(
                        f"{output_dir}, {image_filename}, {pitch}, {roll}, {altitude}, {heading}, {lat_position}, {long_position}\n")
                print("Captured frame...")

        else:
            new_dir = True

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()
    return sequence


def module_main_mission_1_v2_processing(sqeuence, colorProfile, min_area):
    """After acquiring the images, this function processes and locates
    the object by reading the CSV files. In case an object is located, a 
    second CSV files with the GPS object coordinates is created."""
    # Read the CSV file with telemetry data
    for i in range(sqeuence):
        with open(f"/media/aviator/INTENSO/BildsequenzTest_{i}/image_saved.csv", "r") as log_file:
            lines = log_file.readlines()

        # Process each line in the CSV file
        for line in lines:
            # Split the line at ", "" to extract data
            output_dir, image_filename, pitch, roll, altitude, heading, lat_position, long_position = line.strip().split(", ")

            # Convert into integers
            pitch, roll, altitude, heading, lat_position, long_position = int(pitch), int(
                roll), int(altitude), int(heading), float(lat_position), float(long_position)

            # Read the image and convert it to HSV color space
            hsv, frame = read_image_and_convert(output_dir, image_filename)
            detectedObject = False

            # Locate the object and save locations in CSV file
            _, _, frame = locate_object_and_save(
                output_dir, image_filename, colorProfile, hsv, frame,
                min_area, detectedObject, pitch, roll, altitude,
                heading, lat_position, long_position
            )

            # Save the processed image
            cv2.imwrite(output_dir + '/processed_' + image_filename, frame)
            print("Captured frame...")


async def get_position(drone):
    async for position in drone.telemetry.position():
        return (position)


async def get_heading(drone):
    async for heading in drone.telemetry.heading():
        return heading


async def get_altitude(drone):
    async for altitude in drone.telemetry.altitude():
        return altitude


async def get_roll(drone):
    async for euler in drone.telemetry.attitude_euler():
        return euler.roll_deg


async def get_pitch(drone):
    async for euler in drone.telemetry.attitude_euler():
        return euler.pitch_deg


async def get_yaw(drone):
    async for euler in drone.telemetry.attitude_euler():
        return euler.yaw_deg


def module_main_mission_1_flighttest(
        drone, vid
):

    # Initialize image saving variables
    new_dir = True
    last_time_saved = time.time()
    save_delay = 1  # Save image every 1 seconds
    sequence = 0

    while True:
        # Capture frame and convert to HSV
        _, frame = capture_and_convert(vid)
        

        # Telemetry data that will come from the flight controller
        altitude = get_altitude(drone)
        print(altitude)
        heading = get_heading(drone)
        print(heading)
        lat_position = 40.123123
        long_position = 150.123521
        pitch = get_pitch(drone)
        print(pitch)
        roll = get_roll(drone)
        print(roll)

        # Display the original frame and the grayscale frame
        cv2.imshow('Original Frame', frame)

        # Check if new directory has to be created
        if new_dir == True:
            output_dir = create_directory(sequence)
            new_dir = False
            image_count = 0  # Reset numbering for images in new directory
            sequence += 1

            # Only save image every 1 seconds in the directory with
            # neccesary telemetry data
        if time.time() - last_time_saved >= save_delay:
            image_filename = save_image(
                frame, image_count, output_dir, sequence)
            last_time_saved = time.time()
            image_count += 1
            with open(f"{output_dir}/image_saved.csv", "a") as log_file:
                log_file.write(
                    f"{output_dir}, {image_filename}, {pitch}, {roll}, {altitude}, {heading}, {lat_position}, {long_position}\n")
            print("Captured frame...")

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()
    return sequence
