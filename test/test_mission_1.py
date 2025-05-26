import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import control.controller_functions as cl  # type: ignore
import utils.image_processing_raspi as ip  # type: ignore
import gridwithconnection3 as grid
from mavsdk.mission import MissionItem, MissionPlan
from mavsdk.mission import Mission
from shapely import geometry as geom  # type: ignore
import asyncio
import json
import os

# Mission 1
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

    # Generate the mission plan
    polygon_coords = [
        {"latitude": 48.76758, "longitude": 11.33733},
        {"latitude": 48.76747, "longitude": 11.33722},
        {"latitude": 48.76780, "longitude": 11.33651},
        {"latitude": 48.76791, "longitude": 11.33665}
    ]

    polygon = geom.Polygon([
        (point["longitude"], point["latitude"]) for point in polygon_coords])

    mission_locations = grid.generate_cell_center_points(polygon)

    mission_locations

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

    # Start camera
    vid = ip.start_videoCapture(1)

    # 5. Take off to 5 meters
    target_altitude = 15
    await cl.default_takeoff(drone, target_altitude)
    await asyncio.sleep(1)

    # 6. Start photo capture
    print("\nStarting photo capture...")
    try:
        asyncio.create_task(ip.main_mission_1(drone, vid))
    except Exception as e:
        print(f"⚠️ Error starting photo capture: {e}")
    print("Photo capture started.")

    # 7. Fly to each location
    start_index = cl.load_progress()
    target_altitude = 5.0  # Set target altitude for the mission
    for i, (longitude, latitude) in enumerate(mission_locations, start=1):
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
            wait_time = 45
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
