import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import control.controller_functions as cl 
import utils.image_processing as image_processing
import utils.image_processing_raspi as ip
import control.logging as log
import asyncio
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
    logfile = "mission2.log"
    log.log("Mission 2 gestartet", logfile)

    #1. connect to the drone
    drone = await cl.connect_drone(logfile)

    #2. user confirmation before arming
    while True:
        user_input = input(
            "🚦 Ready to arm the drone? (y/n): ").strip().lower()
        if user_input == "y":
            break
        elif user_input == "n":
            print("❌ Mission aborted by user.")
            exit(0)
        else:
            print("⚠️ Please enter 'y' to start or 'n' to abort.")

    
    #3. arm the drone and set location
    # arm the drone
    await cl.arm_drone(drone, logfile)
    await asyncio.sleep(1)

    # set location
    mission_locations = [(48.76786, 11.33668)] # target location

    # Start camera
    vid = ip.start_videoCapture(2)
    color = 4  # orange target

    #4. user confirmation before takeoff
    while True:
        user_input = input(
            "🚦 Ready to takeoff? (y/n): ").strip().lower()
        if user_input == "y":
            break
        elif user_input == "n":
            print("❌ Mission aborted by user.")
            exit(0)
        else:
            print("⚠️ Please enter 'y' to start or 'n' to abort.")

    #5. takeoff to 15 meters
    target_altitude = 5.0
    await cl.default_takeoff(drone, target_altitude, logfile)
    await asyncio.sleep(1)

    #6. fly to location
    target_altitude = 15.0
    latitude, longitude = mission_locations[0]
    log.log(
            f"🟣 Flying to single location: "
            f"{latitude}, {longitude}, {target_altitude} m", logfile
        )
    await cl.goto_location(drone, latitude, longitude, target_altitude, logfile)
    await drone.action.hold()

    #7. if no target detected: fly spiral search 
    position = await drone.telemetry.position().__anext__()
    center_lat = position.latitude_deg
    center_lon = position.longitude_deg

    n_ned, e_ned = await ip.main_mission_2(drone, vid, color) # orange target
    if n_ned is None or e_ned is None:
        print("TARGET NOT FOUND")
        bool = await cl.fly_spiral_search(drone, center_lat,
                                          center_lon, vid, color, target_altitude,
                                          logfile)
    else:
        bool = True

    position = await drone.telemetry.position().__anext__()
    center_lat = position.latitude_deg
    center_lon = position.longitude_deg

    n_ned, e_ned = await ip.main_mission_2(drone, vid, color) # oragne target
    if n_ned is None or e_ned is None:
        print("TARGET NOT FOUND")
        bool = await cl.fly_spiral_search(drone, center_lat,
                                          center_lon, vid, color,
                                          target_altitude, logfile)
    else:
        bool = True

    if bool == False:
        #Return to land
        log.log("No target found, returning to home location.", logfile)
        home = await drone.telemetry.home().__anext__()
        latitude = home.latitude_deg
        longitude = home.longitude_deg
        await cl.goto_location(drone,
                               latitude,
                               longitude,
                               target_altitude,
                               logfile)
        await cl.default_land_and_disarm(drone, logfile)
    else:    
        #8. precision land
        await cl.precision_land_velocity_pid_method(drone, vid, color, logfile) # oragne target


asyncio.run(mission_2())