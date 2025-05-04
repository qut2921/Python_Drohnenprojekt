import modules.controller_functions as cl # type: ignore
from mavsdk.mission import MissionItem, MissionPlan
from mavsdk.mission import Mission
import asyncio




# Mission 1 (eibene Funktion)
async def mission_1():
    """
    Mission 1
        1. Connect to the drone
        2. User confirmation before arming
        3. Arm the drone and set locations
        4. Take off to 5 meters
        5. Fly to each location
        6. Wait for 5 seconds at each location
        7. Land and disarm
    """
    # 1. Connect to the drone
    drone = await cl.connect_drone()

    # 2. User confirmation before arming
    while True:
        user_input = input("🚦 Ready to arm and start mission? (y/n): ").strip().lower()
        if user_input == "y":
            print("✅ Starting mission...")
            break
        elif user_input == "n":
            print("❌ Mission aborted by user.")
            exit(0)
        else:
            print("⚠️ Please enter 'y' to start or 'n' to abort.")

    # 3. Arm and Mission locations
    # Arm the drone
    await cl.arm_drone(drone)
    await asyncio.sleep(2)

    # Get the home location
    home_location = await drone.telemetry.home().__anext__()
    home_lat = home_location.latitude_deg
    home_lon = home_location.longitude_deg
    mission_locations = [
        #(home_lat, home_lon),  # Start at home
        (48.7675058, 11.3364601),
        (48.7672850, 11.3361733),
        (48.7674827, 11.3358296),
        (48.7677421, 11.3361358),
        (home_lat, home_lon),  # Return to home
    ]

    # 4. Take off to 5 meters
    target_altitude = 5.0
    await cl.default_takeoff(drone, target_altitude)
    await asyncio.sleep(5)

    """
    # 4. Start photo captur
    print("Starting photo capture...")
    await module_main_mission_1(....)
    print("Photo capture started.")
    """
    # 6. Fly to each location
    target_altitude = 10.0
    for i, (latitude, longitude) in enumerate(mission_locations, start=1):
        print(
            f"\n🟣 Flying to location {i}/{len(mission_locations)}: "
            f"{latitude}, {longitude}, {target_altitude} m"
        )
        await cl.goto_location(drone, 
                                                 latitude, 
                                                 longitude, 
                                                 target_altitude)
        # Wait for 5 seconds at each location to take a photo
        await asyncio.sleep(5)

    # 7. Land and disarm (last gps location must be the finsh)
    await cl.default_land_and_disarm(drone)


# Mission 1 (MissionPlaner)
async def mission_1_planner():
    # 1. Connect to the drone
    drone = await cl.connect_drone()

    # 2. Create Mission Items
    home_position = await drone.telemetry.home().__anext__()
    home_lat = home_position.latitude_deg
    home_lon = home_position.longitude_deg

    mission_items = []

    waypoints = [
        (48.7675058, 11.3364601),
        (48.7672850, 11.3361733),
        (48.7674827, 11.3358296),
        (48.7677421, 11.3361358),
        (home_lat, home_lon),  # Return to home
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
    await cl.default_land_and_disarm(drone)

# Run mission 1
asyncio.run(mission_1())
