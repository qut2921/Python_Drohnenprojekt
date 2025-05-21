import modules.controller_functions as cl  # type: ignore
import asyncio

async def test_spirale():
    """
    Makes the drone fly in a spiral pattern.
    """
    # 1 ️ Connect to the drone
    drone = await cl.connect_drone()

    # 3 ️ Arm the drone
    await cl.arm_drone(drone)
    await asyncio.sleep(2)

    # 6  Loop through the remaining altitudes
    home_position = await drone.telemetry.home().__anext__()
    latitude = home_position.latitude_deg
    longitude = home_position.longitude_deg

    # 5  Take off to the first altitude
    await cl.default_takeoff(drone, 5)
    await asyncio.sleep(2)

    # 7  Fly in a spiral pattern
    await cl.fly_spiral_search(drone, latitude, longitude, 5)

asyncio.run(test_spirale())