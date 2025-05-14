import asyncio
from mavsdk import System
import modules.communicator as cm


async def run():
    # Init the drone
    drone = System()
    await drone.connect(system_address="serial:///dev/ttyAMA0:57600")

    # Start the tasks
    # asyncio.ensure_future(print_battery(drone))
    # asyncio.ensure_future(print_gps_info(drone))
    # asyncio.ensure_future(print_in_air(drone))
    # asyncio.ensure_future(print_position(drone))
    # asyncio.ensure_future(print_heading(drone))
    # asyncio.ensure_future(print_altitude(drone))
    # syncio.ensure_future(print_roll(drone))
    # asyncio.ensure_future(print_pitch(drone))
    # asyncio.ensure_future(print_euler(drone))
    # asyncio.ensure_future(print_velocity(drone))
    # asyncio.ensure_future(monitor_communication(drone))
    # asyncio.create_task(print_euler(drone))
    # asyncio.ensure_future(get_euler(drone))
    while True:
        await asyncio.sleep(0.1)
        euler = await get_euler(drone)
        print(euler)
        if euler == None:
            break
        print(euler)

        state = await monitor_communication(drone)
        print(state)
        if state == None:
            break
        print(state)

    print("RTL!!!!")


async def get_battery_status(drone):
    try:
        battery = await asyncio.wait_for(drone.telemetry.battery().__anext__(), timeout=5.0)
        return battery

    except asyncio.TimeoutError:
        print("Timed out waiting for in battery info data.")
        battery = None
        return battery


async def get_gps_info(drone):
    try:
        gps_info = await asyncio.wait_for(drone.telemetry.gps_info().__anext__(), timeout=5.0)
        return gps_info

    except asyncio.TimeoutError:
        print("Timed out waiting for in gps info data.")
        gps_info = None
        return gps_info


async def get_in_air(drone):
    try:
        in_air = await asyncio.wait_for(drone.telemetry.in_air().__anext__(), timeout=5.0)
        return in_air

    except asyncio.TimeoutError:
        print("Timed out waiting for in air data.")
        in_air = None
        return in_air


async def get_position(drone):
    try:
        position = await asyncio.wait_for(drone.telemetry.position().__anext__(), timeout=5.0)
        return position

    except asyncio.TimeoutError:
        print("Timed out waiting for position data.")
        position = None
        return position


async def get_heading(drone):
    try:
        heading = await asyncio.wait_for(drone.telemetry.heading().__anext__(), timeout=5.0)
        return heading

    except asyncio.TimeoutError:
        print("Timed out waiting for heading data.")
        heading = None
        return heading


async def get_altitude(drone):
    try:
        altitude = await asyncio.wait_for(drone.telemetry.altitude().__anext__(), timeout=5.0)
        return altitude

    except asyncio.TimeoutError:
        print("Timed out waiting for altitude data.")
        altitude = None
        return altitude


async def get_euler(drone):
    try:
        euler = await asyncio.wait_for(drone.telemetry.attitude_euler().__anext__(), timeout=5.0)
        # print(f"Euler: {euler}")
        return euler

    except asyncio.TimeoutError:
        print("Timed out waiting for euler data.")
        euler = None
        return euler


async def get_velocity(drone):

    try:
        velocity = await asyncio.wait_for(drone.telemetry.velocity_ned().__anext__(), timeout=5.0)
        return velocity

    except asyncio.TimeoutError:
        print("Timed out waiting for velocity data.")
        velocity = None
        return velocity


async def monitor_communication(drone):
    # async for state in drone.core.connection_state():
    try:
        state = await asyncio.wait_for(drone.core.connection_state().__anext__(), timeout=5.0)
        return state

    except asyncio.TimeoutError:
        print("Timed out waiting for status data.")
        state = None
        return state


if __name__ == "__main__":
    # Start the main function
    asyncio.run(run())
