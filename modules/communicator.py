"""
Commands to read telemetry data from the drone and send it to the companion computer.

If communication is lost, an exception will be raised after a timeout.
"""

import asyncio
import mavsdk


async def get_battery_status(drone):
    try:
        battery = await asyncio.wait_for(drone.telemetry.battery().__anext__(), timeout=5.0)
        return battery

    except asyncio.TimeoutError:
        print("Timed out waiting for in battery info data.")
        battery = None
        return battery


async def get_gps_info(drone):
    try:
        gps_info = await asyncio.wait_for(drone.telemetry.gps_info().__anext__(), timeout=5.0)
        return gps_info

    except asyncio.TimeoutError:
        print("Timed out waiting for in gps info data.")
        gps_info = None
        return gps_info


async def get_in_air(drone):
    try:
        in_air = await asyncio.wait_for(drone.telemetry.in_air().__anext__(), timeout=5.0)
        return in_air

    except asyncio.TimeoutError:
        print("Timed out waiting for in air data.")
        in_air = None
        return in_air


async def get_position(drone):
    try:
        position = await asyncio.wait_for(drone.telemetry.position().__anext__(), timeout=5.0)
        return position

    except asyncio.TimeoutError:
        print("Timed out waiting for position data.")
        position = None
        return position


async def get_heading(drone):
    try:
        heading = await asyncio.wait_for(drone.telemetry.heading().__anext__(), timeout=5.0)
        return heading

    except asyncio.TimeoutError:
        print("Timed out waiting for heading data.")
        heading = None
        return heading


async def get_altitude(drone):
    try:
        altitude = await asyncio.wait_for(drone.telemetry.altitude().__anext__(), timeout=5.0)
        return altitude

    except asyncio.TimeoutError:
        print("Timed out waiting for altitude data.")
        altitude = None
        return altitude


async def get_euler(drone):
    try:
        euler = await asyncio.wait_for(drone.telemetry.attitude_euler().__anext__(), timeout=5.0)
        # print(f"Euler: {euler}")
        return euler

    except asyncio.TimeoutError:
        print("Timed out waiting for euler data.")
        euler = None
        return euler


async def get_velocity(drone):

    try:
        velocity = await asyncio.wait_for(drone.telemetry.velocity_ned().__anext__(), timeout=5.0)
        return velocity

    except asyncio.TimeoutError:
        print("Timed out waiting for velocity data.")
        velocity = None
        return velocity


async def monitor_communication(drone):
    try:
        state = await asyncio.wait_for(drone.core.connection_state().__anext__(), timeout=5.0)
        return state

    except asyncio.TimeoutError:
        print("Timed out waiting for status data.")
        state = None
        return state


async def get_parameters_for_image_processing(drone):
    # Set a global timeout for all operations combined
    results = await asyncio.gather(
        get_position(drone),
        get_euler(drone),
        get_heading(drone),
        monitor_communication(drone),
        get_velocity(drone),
    )

    positions, euler, heading, status, velocity = results

    if None in results:
        print("One or more parameters returned None. Exiting function.")
        return

    # Unpack the results
    latitude = positions.latitude_deg
    longitude = positions.longitude_deg
    altitude = positions.relative_altitude_m
    roll = euler.roll_deg
    pitch = euler.pitch_deg
    yaw = euler.yaw_deg
    
