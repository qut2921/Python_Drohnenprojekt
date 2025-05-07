import modules.image_processing_raspi as ip # type: ignore
import modules.controller_functions as cl
from mavsdk import System
import asyncio

color_profile = 0  # 0: blue, 1: red, 2: yellow, 3: red2
min_area = 900  # minimum area for contour detection

async def main():
    drone = await cl.connect_drone()
    vid = ip.start_videoCapture()
    sequence = await ip.module_main_mission_1_flighttest(drone, vid)
    await ip.module_main_mission_1_v2_processing(sequence, color_profile, min_area)

asyncio.run(main())