"""
Comands to controle the mission with repeating modules

"""
import asyncio
from mavsdk import System


async def connect_drone():
    """
    Connect to the drone and return the drone object.
    """
    drone = System()
    print("---Connecting to drone...")
    await drone.connect(system_address="udp://:14540")
    print("Drone connected")
    return drone


async def arm_and_takeoff(drone: System, target_altitude: float):
    """
    Arm the drone and take off to a specified altitude.
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

