import controller_functions # type: ignore
from mavsdk.mission import MissionItem, MissionPlan
from mavsdk.mission import Mission
import asyncio
# import Bildverarbeitung_V2 # type: ignore
# import cv2  # type: ignore


# Tests takeoff and landing
async def test_altitude():
    # Step 1: Connect to the drone
    drone = await controller_functions.connect_drone()

    # Step 2: Arm and take off to 5 meters
    target_altitude = 5.0
    await controller_functions.default_arm_and_takeoff(drone, target_altitude)

    # Optional: Warte z.B. 5 Sekunden in der Luft
    await asyncio.sleep(5)

    # Step 3: Land and disarm
    await controller_functions.default_land_and_disarm(drone)




# Run the mission
asyncio.run(test_altitude())
