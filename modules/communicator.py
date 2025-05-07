"""
Commands to read telemetry data from the drone and send it to the raspi
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
        return altitude.relative_m


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