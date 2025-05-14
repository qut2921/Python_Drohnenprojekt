"""
Commands to read telemetry data from the drone and send it to the companion computer.
"""

import asyncio
import mavsdk


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


async def get_velocity(drone):
    async for velocity in drone.telemetry.velocity_body():
        return (velocity)

    
async def get_data_for_image_processing(drone):
  
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