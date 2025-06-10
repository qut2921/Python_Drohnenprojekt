import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import control.controller_functions as cl 
import utils.image_processing_raspi as ip
import control.logging as log
import asyncio
import math
import time  # type:ignore
from mavsdk import system
import cv2

async def mission_2(): 
    """
    1. connect to the drone
    2. user confirmation before arming
    3. arm the drone and set location
    4. user confirmation before takeoff
    5. takeoff to 15 meters
    6. fly to location
    7. check camera for target
    7a. if target detected: activate precision land
    8. no target detected: fly spiral search 
    8a. precision land

    """
    # Start logging
    logfile = "test_mission2_einfach.log"
    log.log("Mission 2 gestartet", logfile)
    mission_id = 2

    # 1. connect to the drone
    drone = await cl.connect_drone(logfile)
    
    # 2. arm the drone and set location
    # arm the drone
    #await cl.arm_drone(drone, logfile)

    # set home location
    home = await drone.telemetry.home().__anext__()
    home_latitude = home.latitude_deg
    home_longitude = home.longitude_deg
    
    # set location
    mission_locations = [(48.76786, 11.33668)] # target location
    # 3. Start camera
    vid = ip.start_videoCapture(2,logfile)
    color = 1  # orange target

    bool = False

    n_ned, e_ned = await ip.main_mission_2(drone, vid, color) # orange target
    if n_ned is None or e_ned is None:
        log.log("TARGET NOT FOUND", logfile)    
    else:
        bool = True


    if bool == False:
        #Return to land
        log.log("No target found, returning to home location.", logfile)
    else:    
       timestamp = time.time()
       while time.time() - timestamp < 30:  # wait for 30 seconds
              n_ned, e_ned = await ip.main_mission_2(drone, vid, color)
              log.log(f"n_ned: {n_ned}, e_ned: {e_ned}", logfile)
              asyncio.sleep(0.5)
           

asyncio.run(mission_2())