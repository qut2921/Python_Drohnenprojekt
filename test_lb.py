from controller_functions import *
import asyncio

async def main():
    # Step 1: Connect to the drone
    drone = await connect_drone()

    # Step 2: Arm and take off to 5 meters
    target_altitude = 5.0
    await default_arm_and_takeoff(drone, target_altitude)

    # Optional: Warte z.B. 5 Sekunden in der Luft
    await asyncio.sleep(5)

    # Step 3: Land and disarm
    await default_land_and_disarm(drone)

# Run the main routine
asyncio.run(main())
