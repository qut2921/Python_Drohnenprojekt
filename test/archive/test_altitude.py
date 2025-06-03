import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import control.controller_functions as cl  # type: ignore
import control.logging as log  # type: ignore
import asyncio


# Tests takeoff and landing
async def test_altitude():
    """
    Makes the drone fly up and down between different altitudes.
    Sequence: 5 → 10 → 15 → 10 → 5 meters, then lands.
    """
    altitudes = [5, 10]

    #Start logging
    logfile = "alt_test.log"
    log.log("Altitude test gestartet", logfile)

    # 1 ️ Connect to the drone
    drone = await cl.connect_drone(logfile)

    # 2  User confirmation before arming
    while True:
        user_input = input(
            "🚦 Ready to arm and start mission? (y/n): ").strip().lower()
        if user_input == "y":
            break
        elif user_input == "n":
            print("❌ Mission aborted by user.")
            exit(0)
        else:
            print("⚠️ Please enter 'y' to start or 'n' to abort.")

    # 3 ️ Arm the drone
    await cl.arm_drone(drone, logfile)

    # 4  User confirmation before arming
    while True:
        user_input = input(
            "🚦 Ready to arm and start mission? (y/n): ").strip().lower()
        if user_input == "y":
            break
        elif user_input == "n":
            print("❌ Mission aborted by user.")
            exit(0)
        else:
            print("⚠️ Please enter 'y' to start or 'n' to abort.")

    # 5  Take off to the first altitude
    await cl.default_takeoff(drone, altitudes[0], logfile)
    await asyncio.sleep(2)

    # 6  Loop through the remaining altitudes
    home_position = await drone.telemetry.home().__anext__()
    latitude = home_position.latitude_deg
    longitude = home_position.longitude_deg

    for target_alt in altitudes[1:]:
        log.log(f"🔼 Changing altitude to {target_alt} meters")
        await cl.goto_location(drone, latitude, longitude, target_alt, logfile)

        # Hovers 5 seconds at each altitude
        await drone.action.hold()
        await asyncio.sleep(5)

    # 6  Land
    await cl.default_land_and_disarm(drone, logfile)


# Run the mission
asyncio.run(test_altitude())
