import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import control.controller_functions as cl 
import utils.image_processing as image_processing
import utils.image_processing_raspi as ip
import utils.colors as colors
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
    # Start logging
    logfile = "mission3.log"
    log.log("Mission 3 gestartet", logfile)
    mission_id = 3
    land_mode = "default"  # default or offboard


    # 1. connect to the drone
    drone = await cl.connect_drone(logfile)

    # 2. arm the drone and set location
    # arm the drone  
    await cl.arm_drone(drone, logfile)
    await asyncio.sleep(1)

    # set home location
    home = await drone.telemetry.home().__anext__()
    home_latitude = home.latitude_deg
    home_longitude = home.longitude_deg

    try:
        await drone.param.set_param_float("COM_DISARM_LAND", 0.0)
        log.log("🔧 Set COM_DISARM_LAND = 0.0 to prevent auto-disarm", logfile)
    except Exception as e:
        log.log(f"⚠️ Could not set COM_DISARM_LAND: {e}", logfile)

    # set location 
    mission_locations = [(48.76758, 11.33717, 0),   # blue target location
                         (48.76750, 11.33720, 2)]   # yellow target location

    # 3. Start camera
    weatherConditions = "cloudy"  # or "sunny"
    targetType = "blue"  # blue target
    color = colors.map_color_to_id(targetType)
    vid = ip.start_videoCapture(mission_id, weatherConditions, logfile)
  # condition for color profile only input "cloudy" or "sunny"

    # 4. takeoff to 15 meters
    target_altitude = 15.0
    await cl.default_takeoff(drone, target_altitude, logfile)
    await asyncio.sleep(1)

    # 5. fly to location
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
            else:    
                await cl.precision_land_velocity_pid_method(drone, vid, color, weatherConditions, land_mode,logfile) # oragne target

            async for state in drone.telemetry.landed_state():
                print(f"\r🔍 Landed State: {state}", end="")
                if state == LandedState.ON_GROUND:
                    log.log("✅ Drone is confirmed landed.", logfile)
                    log.log("Takeoff again in 5s", logfile)
                    await asyncio.sleep(5)
                    #8. takeoff to 15 meters
                    await cl.default_takeoff(drone, target_altitude, logfile)
                    break
        else:
            log.log("✅ All locations completed.", logfile)
            break

    # 6. landing 
    await cl.default_land_and_disarm(drone, logfile)
    ip.stop_videoCapture(vid, logfile)
    


