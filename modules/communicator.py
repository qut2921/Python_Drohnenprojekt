"""
Commands to read telemetry data from the drone and send it to the companion computer.

If communication is lost, an exception will be raised after a timeout.
"""

import asyncio
import mavsdk
import numpy as np
import modules.error_message as em


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
    """This function gets the parameters needed for image processing.
    The function are executed in parallel to save time.
    Once a function times out due to a lost of communication, the function will
    break which will lead to RTL.
    """

    # Set a global timeout for all operations combined
    results = await asyncio.gather(
        get_position(drone),
        get_euler(drone),
        # get_heading(drone),
        monitor_communication(drone),
        get_velocity(drone),
    )

    positions, euler, status, velocity = results
    # positions, euler, status = results

    if None in results:
        print("One or more parameters returned None. Exiting function.")
        key = 1
        return None, None, None, None, None, None, None, None, key

    # Unpack the results
    latitude = positions.latitude_deg
    longitude = positions.longitude_deg
    altitude = positions.relative_altitude_m
    roll = euler.roll_deg
    pitch = euler.pitch_deg
    yaw = euler.yaw_deg
    scalar_velocity = np.sqrt(
        np.power(velocity.north_ms, 2)+np.power(velocity.east_ms, 2))
    key = 0

    return latitude, longitude, altitude, roll, pitch, yaw, status, scalar_velocity, key
    # return latitude, longitude, roll, pitch, yaw, status, key
