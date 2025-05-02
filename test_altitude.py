import modules.controller_functions as cl # type: ignore
import asyncio


# Tests takeoff and landing
async def test_altitude():
    """
    Makes the drone fly up and down between different altitudes.
    Sequence: 5 → 10 → 15 → 10 → 5 meters, then lands.
    """
    altitudes = [5, 10, 15, 10, 5]

    # 1 ️ Connect to the drone
    drone = await cl.connect_drone()

    # 2  Arm and take off to the first altitude
    await cl.default_arm_and_takeoff(drone, altitudes[0])
    await drone.action.hold()
    await asyncio.sleep(2)

    # 3  Loop through the remaining altitudes
    home_position = await drone.telemetry.home().__anext__()
    latitude = home_position.latitude_deg
    longitude = home_position.longitude_deg

    for target_alt in altitudes[1:]:
        print(f"\n🔼 Changing altitude to {target_alt} meters")
        await cl.goto_location(drone, latitude, longitude, target_alt)

        # Optional: Hover 5 seconds at each altitude
        await drone.action.hold()
        await asyncio.sleep(5)

    # 4  Land
    await cl.default_land_and_disarm(drone)




# Run the mission
asyncio.run(test_altitude())
