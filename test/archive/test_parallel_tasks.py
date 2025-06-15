import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import control.controller_functions as cl  # type: ignore
import control.communicator as cm  # type: ignore
import asyncio
import logging

async def test_telemetry(drone):
    while True:
        heading = await cm.get_heading(drone)
        print(f"\r Heading: {heading}", end="")

async def test_parallel_tasks():
    """
    Makes the drone fly in a spiral pattern.
    """
    # 1 ️ Connect to the drone
    drone = await cl.connect_drone()

    # 3 ️ Arm the drone
    await cl.arm_drone(drone)
    await asyncio.sleep(2)

    # Start parallel telemetry tasks
    asyncio.create_task(test_telemetry(drone))

    # 6  Loop through the remaining altitudes
    home_position = await drone.telemetry.home().__anext__()
    latitude = home_position.latitude_deg
    longitude = home_position.longitude_deg

    # 5  Take off to the first altitude
    await cl.default_takeoff(drone, 5)
    await asyncio.sleep(2)

    # 8  Land the drone
    await cl.default_land_and_disarm(drone)

asyncio.run(test_parallel_tasks())