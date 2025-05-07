import modules.image_processing_raspi as ip # type: ignore
import modules.controller_functions as cl
from mavsdk import System
import asyncio


pitch = 2  # [degrees] dummy variable
roll = 10  # [degrees] dummy variable
altitude = 10  # [m] dummy variable
heading = 125  # [degrees] dummy variable
speed = 0  # dummy variable
lat_position = 42.01414 # dummy variable
long_position = 10.123213  # dummy variable
color_profile = 0  # 0: blue, 1: red, 2: yellow, 3: red2
min_area = 900  # minimum area for contour detection

async def main():
    drone = await cl.connect_drone()
    vid = ip.start_videoCapture()
    sequence = ip.module_main_mission_1_flighttest(drone, vid)

asyncio.run(main())