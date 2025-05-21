import asyncio
from mavsdk import System
import control.communicator as cm


async def run():

    drone = System()
    await drone.connect(system_address="serial:///dev/ttyAMA0:57600")

    while True:
        await asyncio.sleep(0.1)

        latitude, longitude, altitude, roll, pitch, yaw, status, speed, key = await cm.get_parameters_for_image_processing(drone)

        if key == 1:
            break

        print(f"Latitude: {latitude}")
        print(f"Longitude: {longitude}")
        print(f"Altitude: {altitude}")
        print(f"Roll: {roll}")
        print(f"Pitch: {pitch}")
        print(f"Yaw: {yaw}")
        print(f"Velocity: {speed}")
        print(f"Status: {status}")

    print("OPERATION TERMINATED. SIGNAL LOST!!!! RTL")

if __name__ == "__main__":
    # Start the main function
    asyncio.run(run())
