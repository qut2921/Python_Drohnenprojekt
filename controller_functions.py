"""
Comands to controle the mission with repeating modules

"""
import asyncio
from mavsdk import System


async def connect_drone() -> System:
    """
    Connects to the drone via MAVSDK.

    Returns:
        System: The connected MAVSDK drone object.
    """
    drone = System()
    print("---Connecting to drone...")
    await drone.connect(system_address="udp://:14540")
    print("Drone connected")
    return drone


async def default_arm_and_takeoff(drone: System, target_altitude: float):
    """
    Arms the drone and performs an automatic takeoff.

    Inputs:
        drone (System): MAVSDK drone object to send commands.
        target_altitude (float, optional): Target altitude in meters.
        Default is 10.0 m.

    Steps:
        - Waits for connection to the drone
        - Arms the drone
        - Sets the target takeoff altitude
        - Initiates takeoff
        - Waits until target altitude (±0.5m) is reached
    """
    print("---Arming...")
    await drone.action.arm()
    print("Drone armed")

    print(f"Taking off to {target_altitude} m")
    await drone.action.set_takeoff_altitude(target_altitude)
    await drone.action.takeoff()
    # Waits until the drone reaches the target altitude
    async for position in drone.telemetry.position():
        current_height = position.relative_altitude_m
        print(f"\rCurrent height: {current_height:.1f} m", end="")
        if current_height >= target_altitude - 0.2:
            print("\nTarget altitude reached")
            break
        await asyncio.sleep(0.2)


async def check_battery(drone: System):
    """
    Checks the battery level of the drone.

    Inputs:
        drone (System): MAVSDK drone object to send commands.

    Steps:
        - Retrieves the battery level
        - Prints the battery level
    """
    print("Checking battery level...")
    # Gives the battery level in percent
    async for battery in drone.telemetry.battery():
        print(f"Battery: {battery.remaining_percent * 100:.1f}%")
        await asyncio.sleep(0.2)
        if battery.remaining_percent < 0.2:
            print("Battery low, returning to launch")
            await drone.action.return_to_launch()
            break


async def fail_safe(drone: System):
    """
    Initiates fail-safe procedures for the drone.

    Inputs:
        drone (System): MAVSDK drone object to send commands.

    Checks:
        - Checks the battery level
        - Checks the GPS status
    """
    print("Fail-safe initiated")
    await check_battery(drone)
    print("Fail-safe completed")
    # Checks the battery level of the drone
    battery = await drone.telemetry.battery()
    if battery.remaining_percent < 0.2:
            print("Battery low, returning to launch")
            await drone.action.return_to_launch()

    # Checks the drone's GPS status
    gps_info = await drone.telemetry.gps_info()
    if gps_info.num_satellites_visible < 5:
        print("GPS signal weak, returning to launch")
        await drone.action.return_to_launch()
            

async def goto_location(drone: System, target_latitude: float, 
                        target_longitude: float,
                        target_altitude: float):
    """
    Commands the drone to fly to a specific GPS location.

    Inputs:
        drone (System): MAVSDK drone object to send commands.
        target_latitude (float): Target latitude in degrees.
        target_longitude (float): Target longitude in degrees.
        target_altitude (float): Target altitude in meters.

    Steps:
        - Sets the drone's mode to "GUIDED"
        - Commands the drone to fly to the specified GPS location
    """
    print(
            f"Flying to location: {target_latitude}, "
            f"{target_longitude}, {target_altitude} m")
    await drone.action.set_flight_mode("GUIDED")
    print("Mode set to GUIDED")
    await drone.action.goto_location(target_latitude, 
                                     target_longitude, target_altitude, 0.0)
    print("Flying to target location...")
    # Waits until the drone reaches the target location
    async for position in drone.telemetry.position():
        current_latitude = position.latitude_deg
        current_longitude = position.longitude_deg
        current_height = position.relative_altitude_m    
        print(
                f"\rCurrent location: {current_latitude}, "
                f"{current_longitude}, {current_height:.1f} m",
                end=""
                )       
        # Checks if the drone reavhed target
        if (abs(current_latitude - target_latitude) < 0.0001 and
                abs(current_longitude - target_longitude) < 0.0001 and
                abs(current_height - target_altitude) < 0.2):
            print("\nTarget location reached")
            break
        await asyncio.sleep(0.2)


async def default_land_and_disarm(drone: System):
    """
    Commands the drone to land.

    Inputs:
        drone (System): MAVSDK drone object to send commands.

    Steps:
        - Sets the drone's mode to "LAND"
        - Initiates landing
    """
    print("Landing...")
    await drone.action.set_flight_mode("LAND")
    print("Mode set to LAND")
    await drone.action.land()
    if drone.telemetry.landed_state() == "Landed":
        print("Drone is landed")
    print("Disarming...")
    await drone.action.disarm()
    print("Drone disarmed")