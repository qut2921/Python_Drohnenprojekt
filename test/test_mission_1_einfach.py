import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import control.controller_functions as cl  # type: ignore
import utils.image_processing_raspi as ip  # type: ignore
#from mavsdk.mission import MissionItem, MissionPlan
#from mavsdk.mission import Mission
import control.logging as log  # type: ignore
import asyncio
import os

# Mission 1
async def mission_1():
    """
    Mission 1
        1. Connect to the drone
        2. User confirmation before arming
        3. Arm the drone and set locations
        4. User confirmation before takeoff
        5. Start camera
        5. Take off to 5 meters
        6. Fly to each location
        7. Wait for 45 seconds at each location
        8. Land and disarm at home location
    """
    # Start logging
    logfile = "test_mission1.log"
    log.log("Mission 1 test gestartet", logfile)

    # 1. Connect to the drone
    drone = await cl.connect_drone(logfile)

    # 2. Arm and Mission locations
    # Arm the drone
    await cl.arm_drone(drone, logfile)

    # Set mission locations
    home = await drone.telemetry.home().__anext__()
    home_lat = home.latitude_deg
    home_long = home.longitude_deg
    mission_locations = [
        {48.76756, 11.33704},
        {48.76775, 11.33683},
        {48.76781, 11.33669},
        {home_lat, home_long}
    ]

    # 3. Start camera
    vid = ip.start_videoCapture(1, logfile)
    sequence = 0

    await cl.default_takeoff(drone, 0.0, logfile)
    await drone.action.hold()

    sequence = await ip.main_mission_1(drone, vid, sequence)

    # disarm the drone
    await drone.action.disarm()
    
# Run mission 1
asyncio.run(mission_1())
