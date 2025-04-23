import os
import time  # type:ignore
import cv2  # type:ignore
import numpy as np  # type:ignore


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

    # Start video capture
    vid = cv2.VideoCapture(1)

    # Set video capture properties
    vid.set(3, frame_width)  # Set width of the frame
    vid.set(4, frame_height)  # Set height of the frame

    return vid


def capture_and_convert(vid):
    """Read a frame from the video capture and convert it to HSV color space."""

    # Capture frame
    success, frame = vid.read()

    # Convert frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    if not success:
        return None, None, None
    else:
        return success, hsv, frame


def calculate_gps(
        rect_x, rect_y, rect_w, rect_h,
        pitch_telem, roll_telem, altitude_telem, heading_telem,
        gps_position, frame):
    """Calculate GPS coordinates based on the rectangle position and telemetry data.

    rect_x, rect_y: coordinates of the rectangle

    rect_w, rect_h: width and height of the rectangle

    pitch_telem, roll_telem: telemetry data for pitch and roll

    altitude_telem: telemetry data for altitude

    heading_telem: telemetry data for heading

    gps_position: current GPS position

    frame: current frame from the video capture
    """
    # Get telemetry data
    pitch = pitch_telem
    roll = roll_telem  # dummy variable
    altitude = altitude_telem  # dummy variable [m]
    heading = heading_telem  # dummy variable [degrees]

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
        (111320 * np.cos(np.radians(gps_position[0])))  # [degrees]
    lat_object = gps_position[0] + delta_lat  # [degrees]
    lon_object = gps_position[1] + delta_lon  # [degrees]

    return x_distance, y_distance, n_ned, e_ned


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
        pitch, roll, altitude, heading, gps_position):
    """Locate the object in the frame based on the specified color profile."""
    # mask for the specified color profile
    name, hsv_lower, hsv_upper = set_colorProfiles(colorProfile)
    mask = cv2.inRange(hsv, hsv_lower, hsv_upper)

    # remove noise from mask
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)  # Remove small dots
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)  # Fill small holes

    # find contours in the mask
    contours, hierarchy = cv2.findContours(
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
                    gps_position, frame
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
    return mask, hsv, frame,


def create_directory(sequence):
    """Create a directory for saving images.
    
    sequence: specifies the sequence of image savings based on the mission plan
    """
    output_dir = "BildsequenzTest_{}".format(sequence)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print("Creating directory" + output_dir + "...")
    return output_dir


def save_image(
        frame, frame_amount, output_dir, sequence):
    """Save the captured image to the specified directory."""
    # Capture frame
    cv2.imwrite(
        output_dir + '/frame_{}_{}.jpg'.format(sequence-1, frame_amount), frame)
    print("Captured frame...")


def test_velocity():

    # simulate velocity with sinus
    velocity = 6*np.abs(np.sin(time.time()/4)) + 2  # [m/s]
    print(f"Velocity: {velocity:.2f} m/s")
    return velocity


def module_main_mission_1(
        vid, colorProfile, min_area,
        pitch, roll, altitude, heading, speed, gps_position
):

    # Initialize object detection variables
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
        success, hsv, frame = capture_and_convert(vid)
        if not success:
            break

        mask, hsv, frame = locate_object(
            colorProfile, hsv, frame, min_area,
            detectedObject, pitch, roll, altitude, heading, gps_position
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
    vid.release()
    cv2.destroyAllWindows()

def module_main_mission_2(
        vid, colorProfile, min_area,
        pitch, roll, altitude, heading, speed, gps_position
):
    roll