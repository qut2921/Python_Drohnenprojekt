import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import control.controller_functions as cl 
import utils.image_processing_raspi as ip
import utils.colors as colors
from mavsdk.telemetry import LandedState
import control.logging as log
import asyncio
import math
from mavsdk import system

async def run(landingPosition, waypoints, targetNumber, targetType, weatherConditions, geofence=None):
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
    logfile = "logs/mission3.log"
    log.log("---------------------------------", logfile)
    log.log("Mission 3 gestartet", logfile)

    # Hier könnte der Code für die Ausführung der Mission 3 stehen
    log.log(f"Mission 3 gestartet mit Landeposition: {landingPosition}, Wegpunkte: {waypoints}, Zielanzahl: {targetNumber}, Wetterbedingungen: {weatherConditions}", logfile)
    if geofence:
        log.log(f"Geofence aktiviert mit Punkten: {geofence}", logfile)
    else:
        log.log("Geofence über QGC gesetzt", logfile)
    pass

    
    mission_id = 3
    land_mode = "default"  # default or offboard


    # 1. connect to the drone
    drone = await cl.connect_drone(logfile)

    # 2. arm the drone and set location
    # arm the drone  
    await cl.arm_drone(drone, logfile)
    await asyncio.sleep(1)

    try:
        await drone.param.set_param_float("COM_DISARM_LAND", 0.0)
        log.log("🔧 Set COM_DISARM_LAND = 0.0 to prevent auto-disarm", logfile)
    except Exception as e:
        log.log(f"⚠️ Could not set COM_DISARM_LAND: {e}", logfile)

    # set location
    home = await drone.telemetry.home().__anext__()
    home_lat = home.latitude_deg
    home_long = home.longitude_deg
    landingPosition = (home_lat,home_long)
    mission_locations = waypoints.append(landingPosition)  # target location

    # 3. Start camera
    color = colors.map_color_to_id(targetType)  # convert target type to color ID
    vid = ip.start_videoCapture(mission_id, weatherConditions, logfile)

    # 4. takeoff to 15 meters
    target_altitude = 15.0
    await cl.default_takeoff(drone, target_altitude, logfile)
    await asyncio.sleep(1)

    # 5. fly to location
    start_index = cl.load_progress()
    # lat und long muss bei Hanna umgedreht werden (longitude, latitude)
    for i, (latitude, longitude) in enumerate(mission_locations, start=1):
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
                # Fly to next location
                continue
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