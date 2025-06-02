import control.controller_functions as cl 
import utils.image_processing as image_processing
import utils.image_processing_raspi as ip
from mavsdk.telemetry import LandedState
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

    #1. connect to the drone
    drone = await cl.connect_drone()

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
    await cl.arm_drone(drone)
    await asyncio.sleep(1)

    # set location 
    mission_locations = [(48.76758, 11.33717)] # target location

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
    await cl.default_takeoff(drone, target_altitude)
    await asyncio.sleep(1)

    #6. fly to location
    start_index = cl.load_progress()
    # lat und long muss bei Hanna umgedreht werden (longitude, latitude)
    for i, (latitude, longitude) in enumerate(mission_locations, start=1):
        # Skip already visited locations
        if i <= start_index:
            print(f"\n⏭️ Skipping location {i} (already completed)")
            continue
    
        print(
            f"\n🟣 Flying to location {i}/{len(mission_locations)}: "
            f"{latitude}, {longitude}, {target_altitude} m"
        )
        await cl.goto_location(drone, latitude, longitude, target_altitude)
        await drone.action.hold()

        if i < len(mission_locations):
            #7. precisionland on target
            await cl.precision_land_velocity_pid_method(drone, vid)

            async for state in drone.telemetry.landed_state():
                print(f"\r🔍 Landed State: {state}", end="")
                if state == LandedState.ON_GROUND:
                    print("\n✅ Drone is confirmed landed.")
                    print("Takeoff again")
                    await asyncio.sleep(1)
                    #8. takeoff to 15 meters
                    await cl.default_takeoff(drone, target_altitude)
                    break
        else:
            print("\n✅ All locations completed.")
            break

    #13. landing 
    await cl.default_land_and_disarm(drone)
    


