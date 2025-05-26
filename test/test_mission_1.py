import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import control.controller_functions as cl  # type: ignore
from mavsdk.mission import MissionItem, MissionPlan
from mavsdk.mission import Mission
import asyncio
import json
import os

# Mission 1 (eibene Funktion)
async def mission_1():
    """
    Mission 1
        1. Connect to the drone
        2. User confirmation before arming
        3. Arm the drone and set locations
        4. User confirmation before takeoff
        5. Take off to 5 meters
        6. Fly to each location
        7. Wait for 5 seconds at each location
        8. Land and disarm
    """

    # 1. Connect to the drone
    drone = await cl.connect_drone()

    # 2. User confirmation before arming
    while True:
        STATE_FILE = "mission1_state.json"
        if not os.path.exists(STATE_FILE):
            user_input = input(
                "🚦 Ready to arm the drone? (y/n): ").strip().lower()
            if user_input == "y":
                break
            elif user_input == "n":
                print("❌ Mission aborted by user.")
                exit(0)
            else:
                print("⚠️ Please enter 'y' to start or 'n' to abort.")
        else:
            user_input = input(
                "🚦 Ready to arm the drone to restart mission 1? (y/n): ").strip().lower()
            if user_input == "y":
                break
            elif user_input == "n":
                print("❌ Mission aborted by user.")
                exit(0)
            else:
                print("⚠️ Please enter 'y' to start or 'n' to abort.")

    # 3. Arm and Mission locations
    # Arm the drone
    await cl.arm_drone(drone)
    await asyncio.sleep(1)

    # Get the home location
    home_location = await drone.telemetry.home().__anext__()
    home_lat = home_location.latitude_deg
    home_lon = home_location.longitude_deg
    mission_locations = [
        # (home_lat, home_lon),  # Start at home
        (48.76758, 11.33717),
        (48.76786, 11.33649),
        (48.76758, 11.33717),
        (48.76786, 11.33649),
        (home_lat, home_lon),  # Return to home
    ]

    # 4. User confirmation before takeoff
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

    # 5. Take off to 5 meters
    target_altitude = 5.0
    await cl.default_takeoff(drone, target_altitude)
    await asyncio.sleep(1)

    # 6. Start photo capture
    print("Starting photo capture...")
    asyncio.create_task(cl.main_mission_1())

    
    # 7. Fly to each location
    start_index = cl.load_progress()
    target_altitude = 10.0
    for i, (latitude, longitude) in enumerate(mission_locations, start=1):
        # Skip already visited locations
        if i <= start_index:
            print(f"\n⏭️ Skipping location {i} (already completed)")
            continue
    
        print(
            f"\n🟣 Flying to location {i}/{len(mission_locations)}: "
            f"{latitude}, {longitude}, {target_altitude} m"
        )
        await cl.goto_location(drone,
                               latitude,
                               longitude,
                               target_altitude)
        # Wait for 5 seconds at each location to take a photo
        await drone.action.hold()
        cl.save_progress(i)    # Save progress after each location
        if i < len(mission_locations):
            # ⏳ Nur warten, wenn es NICHT der letzte Punkt ist
            wait_time = 5
            for remaining in range(wait_time, 0, -1):
                print(f"\r⏳ Waiting... {remaining} s ", end="")
                await asyncio.sleep(1)
            print("\r✅ Wait complete.")
        else:
            print("🏁 Final point reached – skipping wait, preparing to land.")


    # 8. Land and disarm (last gps location must be the finsh)
    await cl.default_land_and_disarm(drone)
    cl.reset_progress()  # Reset progress after mission completion

# Run mission 1
asyncio.run(mission_1())
