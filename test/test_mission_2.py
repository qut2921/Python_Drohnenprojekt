import control.controller_functions as cl 
import utils.image_processing as image_processing
import utils.image_processing_raspi as image_processing_raspi
import asyncio
import math
import picamera2
import picamera2.controls
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
    home_location = await drone.telemetry.home().__anext__()
    home_lat = home_location.latitude_deg
    home_lon = home_location.longitude_deg
    mission_locations = [(48.76758, 11.33717)] # target location

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
    target_altitude = 15.0
    for i, (latitude, longitude) in enumerate(mission_locations, start=1):
        print(
            f"\n🟣 Flying to location {i}/{len(mission_locations)}: "
            f"{latitude}, {longitude}, {target_altitude} m"
        )
        await cl.goto_location(drone,
                               latitude,
                               longitude,
                               target_altitude)
        await drone.action.hold()

    #7. check camera for target
    await image_processing_raspi.main_mission_2()

    #8. no target detected: fly spiral search 
    position = await drone.telemetry.position().__anext__()
    center_lat = position.latitude_deg
    center_lon = position.longitude_deg
    await cl.fly_spiral_search(drone, center_lat, center_lon)

    #8a. precision land
    await cl.precision_land_velocity_pid_method(drone, image_processing)
