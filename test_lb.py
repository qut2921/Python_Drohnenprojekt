import controller_functions # type: ignore
from mavsdk.mission import MissionItem, MissionPlan
from mavsdk.mission import Mission
import asyncio
# import Bildverarbeitung_V2 # type: ignore
# import cv2  # type: ignore


# Tests takeoff and landing
async def test_altitude():
    # Step 1: Connect to the drone
    drone = await controller_functions.connect_drone()

    # Step 2: Arm and take off to 5 meters
    target_altitude = 5.0
    await controller_functions.default_arm_and_takeoff(drone, target_altitude)

    # Optional: Warte z.B. 5 Sekunden in der Luft
    await asyncio.sleep(5)

    # Step 3: Land and disarm
    await controller_functions.default_land_and_disarm(drone)


# Mission 1 (eibene Funktion)


async def mission_1():
    """
    Mission 1
        1. Connect to the drone
        2. Arm and take off to 5 meters
        3. Fly to each location
        4. Take a photo at each location
        5. Land and disarm
    """
    # 1. Connect to the drone
    drone = await controller_functions.connect_drone()

    # 2. Mission locations
    home_location = await drone.telemetry.home().__anext__()
    home_lat = home_location.latitude_deg
    home_long = home_location.longitude_deg
    mission_locations = [
        (home_lat, home_long + 0.0001),  # Location 1
        (home_lat, home_long + 0.0004),  # Location 2
        (home_lat, home_long + 0.0007),  # Location 3
    ]

    # 3. Arm and take off to 5 meters
    target_altitude = 5.0
    await controller_functions.default_arm_and_takeoff(drone, target_altitude)
    await asyncio.sleep(5)

    """
    # 4. Start photo captur
    print("Starting photo capture...")
    await module_main_mission_1(....)
    print("Photo capture started.")
    """
    # 5. Fly to each location
    target_altitude = 10.0
    for i, (latitude, longitude) in enumerate(mission_locations, start=1):
        print(
            f"\n🟣 Flying to location {i}/{len(mission_locations)}: "
            f"{latitude}, {longitude}"
        )
        await controller_functions.goto_location(drone, 
                                                 latitude, 
                                                 longitude, 
                                                 target_altitude)
        # Wait for 5 seconds at each location to take a photo
        await asyncio.sleep(5)

    # 6. Land and disarm (last gps location must be the finsh)
    await controller_functions.default_land_and_disarm(drone)


# Mission 1 (MissionPlaner)
async def mission_1_planner():
    # 1. Connect to the drone
    drone = await controller_functions.connect_drone()

    # 2. Create Mission Items
    home_position = await drone.telemetry.home().__anext__()
    home_lat = home_position.latitude_deg
    home_lon = home_position.longitude_deg

    mission_items = []

    waypoints = [
        (home_lat, home_lon + 0.0001),  # ca. 10m nach Osten
        (home_lat, home_lon + 0.0002),
        (home_lat, home_lon + 0.0003),
    ]

    for lat, lon in waypoints:
        mission_items.append(
            Mission.MissionItem(
                lat_deg=lat,
                lon_deg=lon,
                rel_alt=10.0,  # relative altitude 10m
                speed_m_s=3.0,  # Fly at 3 m/s
                fly_through=False,  # Stop at waypoint
                gimbal_pitch_deg=0.0,
                gimbal_yaw_deg=0.0,
                camera_action=Mission.MissionItem.CameraAction.NONE,
            )
        )

    mission_plan = Mission.MissionPlan(mission_items)

    # 3. Upload Mission
    await drone.mission_raw.upload_mission(mission_plan)
    print("📋 Mission uploaded")

    # 4. Arm and Start Mission
    await drone.action.arm()
    print("✅ Drone armed")

    await drone.mission_raw.start_mission()
    print("🚀 Mission started")

    # 5. Wait until mission finished
    async for mission_progress in drone.mission_raw.mission_progress():
        print(f"\rMission progress: "
              f"{mission_progress.current}/{mission_progress.total}",
              end="")
        if mission_progress.current == mission_progress.total:
            print("\nMission completed")
            break
        await asyncio.sleep(0.5)

    # 6. Land and Disarm
    await controller_functions.default_land_and_disarm(drone)

# Run the main routine
# asyncio.run(main())

# Run the mission
asyncio.run(mission_1())
