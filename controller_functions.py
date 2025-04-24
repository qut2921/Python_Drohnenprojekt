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


async def arm_and_takeoff(drone: System, target_altitude: float):
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

    async for position in drone.telemetry.position():
        current_height = position.relative_altitude_m
        print(f"\rCurrent height: {current_height:.1f} m", end="")
        if current_height >= target_altitude - 0.5:
            print("\nTarget altitude reached")
            break
        await asyncio.sleep(0.2)

