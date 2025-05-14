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
  
    health = drone.telemetry.health()
    print(health)
    altitude_data = await get_altitude(drone)
    altitude = altitude_data.bottom_clearance_m
    print(altitude)
    heading = await get_heading(drone)
    print(heading)
    (lat_position, long_position, ) = await get_position(drone)
    pitch = await get_pitch(drone)
    print(pitch)
    roll = await get_roll(drone)
    print(roll)
    velocity = await get_velocity(drone)
    print(velocity)

    return health, altitude, heading, (lat_position, long_position), pitch, roll, velocity