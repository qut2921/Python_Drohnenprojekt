"""This module contains a function to calculate GPS coordinates based on
the position of the rectangle that is bounding the detected object.
"""
import numpy as np  # type:ignore
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def calculate_gps(
        rect_x, rect_y, rect_w, rect_h,
        pitch, roll, altitude, heading,
        lat_position, long_position, frame):
    """Calculate GPS coordinates based on the rectangle position and telemetry data.

    rect_x, rect_y: coordinates of the rectangle bounding the detected object

    rect_w, rect_h: width and height of the rectangle bounding the detected object

    pitch, roll: telemetry data for pitch and roll

    altitude: telemetry data for altitude

    heading_: telemetry data for heading (yaw)

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


def calculate_frame_dimensions(altitude, fov_horizontal=66, fov_vertical=41):
    """Calculate the frame dimensions based on GPS position.

    Returns the width and height of the frame in meters based on the altitude and field of view (FOV) of the camera.

    Args:
        altitude (float): Altitude of the drone in meters.
        fov_horizontal (float, optional): Horizontal field of view of the camera in degrees. Defaults to 66.
        fov_vertical (float, optional): Vertical field of view of the camera in degrees. Defaults to 41.
    Returns:
        tuple: A tuple containing the width and height of the frame in meters.
    """

    # Convert FOV from degrees to radians
    fov_horizontal_rad = np.radians(fov_horizontal)
    fov_vertical_rad = np.radians(fov_vertical)

    # Calculate the width and height of the frame in meters
    width = 2 * altitude * np.tan(fov_horizontal_rad / 2)
    height = 2 * altitude * np.tan(fov_vertical_rad / 2)

    return width, height



def calculate_relative_x_y_distance(lat1, lon1, lat2, lon2):
    """Calculate the relative distance between two GPS coordinates.

    Args:
        lat1 (float): Latitude of the first point in degrees.
        lon1 (float): Longitude of the first point in degrees.
        lat2 (float): Latitude of the second point in degrees.
        lon2 (float): Longitude of the second point in degrees.

    Returns:
        (float, float): A tuple containing the relative distance in the North and East directions in meters.
    """
    # Convert latitude and longitude from degrees to radians
    lat1_rad = np.radians(lat1)
    lon1_rad = np.radians(lon1)
    lat2_rad = np.radians(lat2)
    lon2_rad = np.radians(lon2)

    # Calculate the differences in coordinates
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    # Radius of the Earth in meters
    R = 6371000

    # Calculate the North and East distances using the Haversine formula
    n_distance = R * dlat  # North distance in meters
    # East distance in meters
    e_distance = R * dlon * np.cos((lat1_rad + lat2_rad) / 2)

    return n_distance, e_distance
