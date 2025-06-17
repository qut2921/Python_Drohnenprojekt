import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import control.controller_functions as cl 
import utils.image_processing_raspi as ip
import control.logging as log
import asyncio
import utils.colors as colors
import math
from mavsdk import system

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
    logfile = "logs/mission2.log"
    log.log("Mission 2 gestartet", logfile)
    mission_id = 2
    land_mode = "default"  # default or offboard

    # 1. connect to the drone
    drone = await cl.connect_drone(logfile)
    
    # 2. arm the drone and set location
    # arm the drone
    await cl.arm_drone(drone, logfile)

    # set home location
    home = await drone.telemetry.home().__anext__()
    home_latitude = home.latitude_deg
    home_longitude = home.longitude_deg
    
    # set target location
    mission_locations = [(48.76786, 11.33668)] # target location

    # 3. Start camera
    weatherConditions = "cloudy"  # or "sunny"
    targetType = "orange"  # orange target
    color = colors.map_color_to_id(targetType) # convert target type to color ID
    vid = ip.start_videoCapture(mission_id, weatherConditions, logfile)

    # 4. takeoff to 5 meters
    target_altitude = 5.0
    await cl.default_takeoff(drone, target_altitude, logfile)
    await asyncio.sleep(1)

    # 5. fly to location and climb to 15 meters
    target_altitude = 15.0
    latitude, longitude = mission_locations[0]
    log.log(
            f"🟣 Flying to single location: "
            f"{latitude}, {longitude}, {target_altitude} m", logfile
        )
    await cl.goto_location(drone, latitude, longitude, target_altitude, logfile)
    await drone.action.hold()

    # 6. if no target detected: fly spiral search 
    position = await drone.telemetry.position().__anext__()
    center_lat = position.latitude_deg
    center_lon = position.longitude_deg

    for i in range(4):
        x_distance, y_distance = await ip.main_mission_2(drone, vid, color, weatherConditions, logfile) # orange target

    if x_distance is None or y_distance is None:
        log.log("TARGET NOT FOUND", logfile)
        bool = await cl.fly_spiral_search(drone, center_lat,
                                          center_lon, vid, color, weatherConditions, target_altitude,
                                          logfile)
    else:
        bool = True


    if bool == False:
        #Return to land
        log.log("No target found, returning to home location.", logfile)
        await cl.goto_location(drone,
                               home_latitude,
                               home_longitude,
                               target_altitude,
                               logfile)
        await cl.default_land_and_disarm(drone, logfile)
        ip.stop_videoCapture(vid, logfile)
    else:    
        #8. precision land
        await cl.precision_land_velocity_pid_method(drone, vid, color, weatherConditions, land_mode, logfile) # oragne target
        ip.stop_videoCapture(vid, logfile)


asyncio.run(mission_2())