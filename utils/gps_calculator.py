import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import numpy as np  # type:ignore


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