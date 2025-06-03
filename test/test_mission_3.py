import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import control.controller_functions as cl 
import utils.image_processing as image_processing
import utils.image_processing_raspi as ip
from mavsdk.telemetry import LandedState
import control.logging as log
import asyncio
import math
from mavsdk import system

async def mission_3():
    


    """
    1. connect to the drone
    2. user confirmation before arming
    3. arm the drone and set location
    4. user confirmation before takeoff
    5. takeoff to  15 meters
    6. fly to location (for all targets)
    7. precisionland on target (for all targets)
    8. takeoff to 15 meters (for all targets)
    13. landing (at final location)

    """
    #0. Start logging
    logfile = "mission3.log"
    log.log("Mission 3 gestartet", logfile)


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
    mission_locations = [(48.76758, 11.33717, 0),   # blue target location
                         (48.76750, 11.33720, 2)]   # yellow target location

    # Start camera
    vid = ip.start_videoCapture(2)

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
    target_altitude = 15.0
    await cl.default_takeoff(drone, target_altitude, logfile)
    await asyncio.sleep(1)

    #6. fly to location
    start_index = cl.load_progress()
    # lat und long muss bei Hanna umgedreht werden (longitude, latitude)
    for i, (latitude, longitude, color) in enumerate(mission_locations, start=1):
        # Skip already visited locations
        if i <= start_index:
            log.log(f"⏭️ Skipping location {i} (already completed)", logfile)
            continue
    
        log.log(
            f"\n🟣 Flying to location {i}/{len(mission_locations)}: "
            f"{latitude}, {longitude}, {target_altitude} m, Color: {color}", logfile
        )
        await cl.goto_location(drone, latitude, longitude, target_altitude, logfile)
        await drone.action.hold()

        if i < len(mission_locations):
            #7. precisionland on target
            await cl.precision_land_velocity_pid_method(drone, vid, color, logfile)

            async for state in drone.telemetry.landed_state():
                print(f"\r🔍 Landed State: {state}", end="")
                if state == LandedState.ON_GROUND:
                    log.log("✅ Drone is confirmed landed.", logfile)
                    log.log("Takeoff again in 2s", logfile)
                    await asyncio.sleep(2)
                    #8. takeoff to 15 meters
                    await cl.default_takeoff(drone, target_altitude, logfile)
                    break
        else:
            log.log("✅ All locations completed.", logfile)
            break

    #13. landing 
    await cl.default_land_and_disarm(drone, logfile)
    


