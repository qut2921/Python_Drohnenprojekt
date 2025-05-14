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
    #asyncio.ensure_future(print_euler(drone))
    # asyncio.ensure_future(print_velocity(drone))
    # asyncio.ensure_future(monitor_communication(drone))
    # asyncio.create_task(print_euler(drone))
    # asyncio.ensure_future(get_euler(drone))
    while True:
       await asyncio.sleep(0.1)
       euler = await print_euler(drone)
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
      

    


async def print_battery(drone):
    async for battery in drone.telemetry.battery():
        print(f"Battery: {battery.remaining_percent}")


async def print_gps_info(drone):
    async for gps_info in drone.telemetry.gps_info():
        print(f"GPS info: {gps_info}")


async def print_in_air(drone):
    async for in_air in drone.telemetry.in_air():
        print(f"In air: {in_air}")


async def print_position(drone):
    async for position in drone.telemetry.position():
        print(position)
   # position = await drone.telemetry.position().__anext__()
   # print(position)


async def print_heading(drone):
    async for heading in drone.telemetry.heading():
        print(f"Heading: {heading}")


async def print_altitude(drone):
    async for altitude in drone.telemetry.altitude():
        print(f"Altitude: {altitude}")


async def print_euler(drone):
    #async for euler in drone.telemetry.attitude_euler():
        #print(f"Euler angles: {euler}")
        #return euler
    
    try:
        euler = await asyncio.wait_for(drone.telemetry.attitude_euler().__anext__(), timeout=5.0)
        #print(f"Euler: {euler}")
        return euler
    
    except asyncio.TimeoutError:
        print("Timed out waiting for euler data.")
        euler = None
        return euler
        


async def print_velocity(drone):
    async for velocity in drone.telemetry.velocity_ned():
        print(f"Velocity: {velocity}")


async def monitor_communication(drone):
    #async for state in drone.core.connection_state():
        try:
            state = await asyncio.wait_for(drone.core.connection_state().__anext__(), timeout=5.0)
            return state
        
        except asyncio.TimeoutError:
            print("Timed out waiting for euler data.")
            state = None
            return state
        #if state.is_connected:
        #    print("✅ Connected")
       # else:
           # print("❌ Disconnected")


# async def print_roll(drone):
#    async for euler in drone.telemetry.attitude_euler():
#        print(f"Roll: {euler.roll_deg:.2f}°")

# async def print_pitch(drone):
#    async for euler in drone.telemetry.attitude_euler():
#        print(f"Pitch: {euler.pitch_deg:.2f}°")


if __name__ == "__main__":
    # Start the main function
    asyncio.run(run())
