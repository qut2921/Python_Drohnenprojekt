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


async def run(landingPosition, targetType, area, geofence=None):
    # Hier könnte der Code für die Ausführung der Mission 1 stehen
    print(f"Mission 1 gestartet mit Landeposition: {landingPosition}, Zieltyp: {targetType}, Suchgebiet: {area}")
    if geofence:
        print(f"Geofence aktiviert mit Punkten: {geofence}")
    else:
        print("Kein Geofence aktiviert")
    pass

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
    logfile = "mission1.log"
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
    mission_locations = [
        {48.76756, 11.33704},
        {48.76775, 11.33683},
        {48.76781, 11.33669},
        {home_lat, home_long}
    ]

    # 3. Start camera
    vid = ip.start_videoCapture(1, logfile)
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
        cl.save_progress(i)  

        if i < len(mission_locations):
            # ⏳ Nur warten, wenn es NICHT der letzte Punkt ist
            sequence = await ip.main_mission_1(drone, vid, sequence)
        else:
            log.log("🏁 Final point reached – skipping wait, preparing to land.", logfile)


    # 6. Land and disarm (last gps location must be the finsh)
    await cl.default_land_and_disarm(drone, logfile)
    vid.stop()
    cl.reset_progress()  # Reset progress after mission completion

# Run mission 1
asyncio.run(run())