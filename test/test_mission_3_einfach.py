import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import control.controller_functions as cl 
#import utils.image_processing_raspi as ip
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


    # 1. connect to the drone
    drone = await cl.connect_drone(logfile)

    # 2. arm the drone and set location
    # arm the drone  
    await cl.arm_drone(drone, logfile)
    await asyncio.sleep(1)

    # set location 
    mission_locations = [(48.767651, 11.337041, 1),
                         (48.767771, 11.336773, 4),
                         (48.767838, 11.336844, 2)]

    # 3. Start camera
    #vid = ip.start_videoCapture(2)

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
            await drone.action.land()

            async for state in drone.telemetry.landed_state():
                print(f"\r🔍 Landed State: {state}", end="")
                if state == LandedState.ON_GROUND:
                    log.log("✅ Drone is confirmed landed.", logfile)
                    log.log("Takeoff again in 2s", logfile)
                    await asyncio.sleep(2)
                    await cl.arm_drone(drone, logfile)
                    #8. takeoff to 15 meters
                    await cl.default_takeoff(drone, target_altitude, logfile)
                    break
        else:
            log.log("✅ All locations completed.", logfile)
            break

    # 6. landing 
    await cl.default_land_and_disarm(drone, logfile)


if __name__ == "__main__":
    asyncio.run(mission_3())
    print("Mission 3 completed.")
    


