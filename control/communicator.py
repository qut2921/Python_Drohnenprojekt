"""
Asynchronous telemetry interface for retrieving real-time drone data using MAVSDK.

This module defines asynchronous functions to read telemetry data from a drone and forward it
to a companion computer for further use in control logic, logging, or image processing tasks.
It includes timeout-handling mechanisms to detect communication loss and trigger fallback actions.

Functionality includes:
    - Retrieving drone parameters such as battery, position, altitude, orientation 
        (Euler angles), velocity, GPS info, and heading.
    - Monitoring connection status to detect communication interruptions.
    - Aggregating key parameters in parallel for time-sensitive tasks,
        like real-time image processing or testing scenarios.

All telemetry reads are wrapped in `asyncio.wait_for()` to ensure graceful 
failure and logging on timeout.

Usage:
    Call these functions from an `asyncio` event loop with a connected MAVSDK 
    drone instance.

Note:
    - Requires the MAVSDK-Python library (`mavsdk`).
    - Logs timeout exceptions using a custom `control.error_message` module.
    - Example use cases: drone navigation, camera tracking, position estimation.

"""


import asyncio
import mavsdk
import numpy as np
import control.error_message as em


async def get_battery_status(drone):
    try:
        battery = await asyncio.wait_for(drone.telemetry.battery().__anext__(), timeout=5.0)
        return battery

    except asyncio.TimeoutError:
        message = "Timed out waiting for in battery info data."
        print(message)
        em.log(message)
        battery = None
        return battery


async def get_gps_info(drone):
    try:
        gps_info = await asyncio.wait_for(drone.telemetry.gps_info().__anext__(), timeout=5.0)
        return gps_info

    except asyncio.TimeoutError:
        message = "Timed out waiting for in gps info data."
        print(message)
        em.log(message)
        gps_info = None
        return gps_info


async def get_in_air(drone):
    try:
        in_air = await asyncio.wait_for(drone.telemetry.in_air().__anext__(), timeout=5.0)
        return in_air

    except asyncio.TimeoutError:
        message = "Timed out waiting for in air data."
        print(message)
        em.log(message)
        in_air = None
        return in_air


async def get_position(drone):
    try:
        position = await asyncio.wait_for(drone.telemetry.position().__anext__(), timeout=5.0)
        return position

    except asyncio.TimeoutError:
        message = "Timed out waiting for position data."
        print(message)
        em.log(message)
        position = None
        return position


async def get_heading(drone):
    try:
        heading = await asyncio.wait_for(drone.telemetry.heading().__anext__(), timeout=5.0)
        return heading

    except asyncio.TimeoutError:
        message = "Timed out waiting for heading data."
        print(message)
        em.log(message)
        heading = None
        return heading


async def get_altitude(drone):
    try:
        altitude = await asyncio.wait_for(drone.telemetry.altitude().__anext__(), timeout=5.0)
        return altitude

    except asyncio.TimeoutError:
        message = "Timed out waiting for altitude data."
        print(message)
        em.log(message)
        altitude = None
        return altitude


async def get_euler(drone):
    try:
        euler = await asyncio.wait_for(drone.telemetry.attitude_euler().__anext__(), timeout=5.0)
        # print(f"Euler: {euler}")
        return euler

    except asyncio.TimeoutError:
        message = "Timed out waiting for euler data."
        print(message)
        em.log(message)
        euler = None
        return euler


async def get_velocity(drone):

    try:
        velocity = await asyncio.wait_for(drone.telemetry.velocity_ned().__anext__(), timeout=5.0)
        return velocity

    except asyncio.TimeoutError:
        message = "Timed out waiting for velocity data."
        print(message)
        em.log(message)
        velocity = None
        return velocity


async def monitor_communication(drone):
    try:
        state = await asyncio.wait_for(drone.core.connection_state().__anext__(), timeout=5.0)
        return state

    except asyncio.TimeoutError:
        message = "Timed out waiting for status data."
        print(message)
        em.log(message)
        state = None
        return state


async def get_parameters_for_image_processing(drone):
    """
    Retrieves key telemetry parameters required for image processing tasks.

    This asynchronous function concurrently gathers the drone's GPS position,
    Euler attitude angles, and communication status using the MAVSDK telemetry API.
    By executing requests in parallel via `asyncio.gather`, the function optimizes for latency.
    If any parameter retrieval fails (e.g. due to lost connection), it returns `None` for all values
    and sets a fallback key flag, which may trigger a Return-to-Launch (RTL) procedure.

    Args:
        drone: MAVSDK drone instance from which telemetry data is fetched.

    Returns:
        tuple:
            - latitude: Latitude in degrees.
            - longitude: Longitude in degrees.
            - altitude: Relative altitude in meters.
            - roll: Roll angle in degrees.
            - pitch: Pitch angle in degrees.
            - yaw: Yaw angle in degrees.
            - status: Drone connection status object.
            - key: Status flag (0 if successful, 1 if any telemetry data failed).
"""

    # Set a global timeout for all operations combined
    results = await asyncio.gather(
        get_position(drone),
        get_euler(drone),
        # get_heading(drone),
        monitor_communication(drone),
    )

    positions, euler, status = results

    if None in results:
        print("One or more parameters returned None. Exiting function.")
        key = 1
        return None, None, None, None, None, None, None, key

    # Unpack the results
    latitude = positions.latitude_deg
    longitude = positions.longitude_deg
    altitude = positions.relative_altitude_m
    roll = euler.roll_deg
    pitch = euler.pitch_deg
    yaw = euler.yaw_deg
    key = 0

    return latitude, longitude, altitude, roll, pitch, yaw, status, key


async def get_parameters_for_indoor_testing(drone):
    """
    Retrieves key telemetry parameters required for image processing tasks.
    This asynchronous function concurrently gathers the drone's GPS position,
    Euler attitude angles, and communication status using the MAVSDK telemetry API.
    By executing requests in parallel via `asyncio.gather`, the function optimizes for latency.
    If any parameter retrieval fails (e.g. due to lost connection), it returns `None` for all values
    and sets a fallback key flag, which may trigger a Return-to-Launch (RTL) procedure.
    For indoor test, pre defined values for latitude, longitude and altitude
    are defined. This is to adress the lack of GPS connection inside the flight
    lab.

    Args:
        drone: MAVSDK drone instance from which telemetry data is fetched.
        
    Returns:
        tuple:
            - latitude: Latitude in degrees.
            - longitude: Longitude in degrees.
            - altitude: Relative altitude in meters.
            - roll: Roll angle in degrees.
            - pitch: Pitch angle in degrees.
            - yaw: Yaw angle in degrees.
            - status: Drone connection status object.
            - key: Status flag (0 if successful, 1 if any telemetry data failed).
        """

    # Set a global timeout for all operations combined
    results = await asyncio.gather(
        get_euler(drone),
        # get_heading(drone),
        monitor_communication(drone),
    )

    euler, status = results

    if None in results:
        print("One or more parameters returned None. Exiting function.")
        key = 1
        return None, None, None, None, None, None, None, key

    # Unpack the results
    latitude = 48.4558
    longitude = 11.2359
    altitude = 1.5
    roll = euler.roll_deg
    pitch = euler.pitch_deg
    yaw = euler.yaw_deg
    key = 0

    return latitude, longitude, altitude, roll, pitch, yaw, status, key
    
