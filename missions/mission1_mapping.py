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


async def run(landingPosition, waypoints, weatherConditions, geofence=None):
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
    # Hier könnte der Code für die Ausführung der Mission 1 stehen
    log.log(f"Mission 1 gestartet mit Landeposition: {landingPosition}, Wegpunkte: {waypoints}, Wetterbedingungen: {weatherConditions}",logfile)
    if geofence:
        log.log(f"Geofence aktiviert mit Punkten: {geofence}",logfile)
    else:
        log.log("Geofence über QGC gesetzt",logfile)
    pass

    # Start logging
    logfile = "logs/mission1.log"
    log.log("---------------------------------", logfile)
    log.log("Mission 1 gestartet", logfile)

    # 1. Connect to the drone
    drone = await cl.connect_drone(logfile)

    # 2. Arm and Mission locations
    # Arm the drone
    await cl.arm_drone(drone, logfile)

    # Set mission locations
    home = await drone.telemetry.home().__anext__()
    home_lat = home.latitude_deg
    home_long = home.longitude_deg
    landingPosition = (home_lat,home_long)
    mission_locations = waypoints.append(landingPosition)  # Add landing position to the end of the waypoints

    # 3. Start camera
    vid = ip.start_videoCapture(1, weatherConditions, logfile)
    sequence = 0

    # 4. Take off to 5 meters
    target_altitude = 5.0
    await cl.default_takeoff(drone, target_altitude, logfile)
    await asyncio.sleep(1)

    # 5. Fly to each location
    start_index = cl.load_progress()
    target_altitude = 15.0  # Set target altitude for the mission
    # lat und long muss bei Hanna umgedreht werden (longitude, latitude)
    for i, (latitude, longitude) in enumerate(mission_locations, start=1):
        # Skip already visited locations
        if i <= start_index:
            log.log(f"\n⏭️ Skipping location {i} (already completed)", logfile)
            continue
    
        log.log(
            f"\n🟣 Flying to location {i}/{len(mission_locations)}: "
            f"{latitude}, {longitude}, {target_altitude} m", logfile
        )
        await cl.goto_location(drone,
                               latitude,
                               longitude,
                               target_altitude,
                               logfile)
        await drone.action.hold()
         

        if i < len(mission_locations):
            # ⏳ Nur warten, wenn es NICHT der letzte Punkt ist
            sequence = await ip.main_mission_1(drone, vid, sequence, logfile)
            cl.save_progress(i) 
        else:
            log.log("🏁 Final point reached – skipping wait, preparing to land.", logfile)


    # 6. Land and disarm (last gps location must be the finsh)
    await cl.default_land_and_disarm(drone, logfile)
    ip.stop_videoCapture(vid,logfile)  # Stop video capture
    cl.reset_progress()  # Reset progress after mission completion