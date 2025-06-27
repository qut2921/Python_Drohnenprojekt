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
        1. connect to the drone
        2. arm the drone and set location
        3. set home location
        4. set mission locations
        5. Start camera
        6. takeoff to  15 meters
        7. fly to location (for all targets)
        8. landing (at final location)
    """
    # Start logging
    logfile = "mission1.log"
    log.log("---------------------------------", logfile)
    log.log("Mission 1 gestartet", logfile)

    # 1. Connect to the drone
    drone = await cl.connect_drone(logfile)

    # 2. Arm

    await cl.arm_drone(drone, logfile)

    # 3. Set home locations
    home = await drone.telemetry.home().__anext__()
    home_lat = home.latitude_deg
    home_long = home.longitude_deg
    
    # 4. Set mission locations
    mission_locations =  [
        {48.7683189, 11.3357803},
        {48.7682238, 11.3359790},
        {48.7681286, 11.3361777},
        {48.7680335, 11.3363763},
        {48.7679383, 11.3365750},
        {48.7678432, 11.3367737},
        {48.7677480, 11.3369724},
        {48.7676529, 11.3371711},
        {48.7675840, 11.3373149},
        {48.7677361, 11.3374616},
        {48.7678312, 11.3372629},
        {48.7679264, 11.3370642},
        {48.7680216, 11.3368655},
        {48.7681167, 11.3366668},
        {48.7682119, 11.3364681},
        {48.7683070, 11.3362694},
        {48.7684022, 11.3360707},
        {48.7684684, 11.3359324},
        {48.7682807, 11.3367886},
        {48.7681855, 11.3369873},
        {48.7680904, 11.3371860},
        {48.7679952, 11.3373847},
        {home_lat, home_long}  
    ]

    # 5. Start camera
    weatherConditions = "sunny"  # or "sunny"
    vid = ip.start_videoCapture(1, weatherConditions, logfile)
    sequence = 0

    # 6. Take off to 5 meters
    target_altitude = 5.0
    await cl.default_takeoff(drone, target_altitude, logfile)
    await asyncio.sleep(1)

    # 7. Fly to each location
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


    # 8. Land and disarm (last gps location must be the finsh)
    await cl.default_land_and_disarm(drone, logfile)
    ip.stop_videoCapture(vid,logfile)  # Stop video capture
    cl.reset_progress()  # Reset progress after mission completion

# Run mission 1
asyncio.run(mission_1())
