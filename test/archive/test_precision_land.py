import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import control.controller_functions as cl 
from mavsdk.telemetry import LandedState
import control.logging as log
import asyncio
import math
from mavsdk import system


async def test_precision_landing():
    """
    Test for precision landing mission
    """
    logfile = "precision_landing.log"
    mission_id = 3
    
    # connect to the drone
    drone = await cl.connect_drone(logfile)

    # arm the drone
    await cl.arm_drone(drone, logfile)

    # takeoff to 5 meters
    target_altitude = 10.0
    await cl.default_takeoff(drone, target_altitude, logfile)
    await asyncio.sleep(1)

    # precision landing
    n_ned = 10.0
    e_ned = -10.0

    await cl.precision_land_test(drone, mission_id, n_ned, e_ned, logfile)

    async for state in drone.telemetry.landed_state():
        print(f"\r🔍 Landed State: {state}", end="")
        if state == LandedState.ON_GROUND:
            log.log("\n✅ Drone is confirmed landed.\n", logfile)
            await cl.default_takeoff(drone, target_altitude, logfile)
            break
        else:
            continue


# Run the test
if __name__ == "__main__":
    asyncio.run(test_precision_landing())
    print("Precision landing test completed.")