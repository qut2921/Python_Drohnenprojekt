import asyncio
from mavsdk import System
from mavsdk.offboard import (OffboardError, VelocityBodyYawspeed, PositionNedYaw)
import control.controller_functions as cl
import control.error_message as em

async def monitor_flight_mode(drone):
    async for flight_mode in drone.telemetry.flight_mode():
        print(f"\r✈️  Current flight mode: {flight_mode}", end="")
        await asyncio.sleep(0.5)



async def run():

    # Connect to the drone
    drone = System()
    drone = await cl.connect_drone()

    # Arm the drone
    await cl.arm_drone(drone)

    # Start monitoring in background
    asyncio.create_task(monitor_flight_mode(drone))

    # Take off to the first altitude
    await cl.default_takeoff(drone, 5)

    # Start offboard mode
    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, 0.0, 0.0))
    try:
        await drone.offboard.start()
        print("Offboard mode activated")
    except OffboardError as error:
        message = f"Offboard mode could not be activated: {error._result.result}"
        print(message)
        em.log(message)
        message = "--> aborting"
        print(message)
        em.log(message)

        print(f"Offboard mode could not be activated: {error._result.result}")
        print("--> aborting")
        return
    
    await asyncio.sleep(2)

    # Start hold mode
    try:
        await drone.action.hold()
        print("Hold mode activated")
    except Exception as error:
        message = f"Hold mode could not be activated: {error}"
        print(message)
        em.log(message)
        print(f"Hold mode could not be activated: {error}")
        return
    await asyncio.sleep(2)

    # Land the drone
    await cl.default_land_and_disarm(drone)
    print("Landing...")



if __name__ == "__main__":
    asyncio.run(run())