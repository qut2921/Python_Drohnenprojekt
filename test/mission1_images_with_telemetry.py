import utils.image_processing_raspi as ip # type: ignore
import control.controller_functions as cl
from mavsdk import System
import asyncio

mission = 1
color_profile = 1
min_area = 900


drone = cl.connect_drone()
vid = ip.start_videoCapture(mission)
sequence = ip.main_mission_1(drone, vid)

ip.main_mission_1_post_processing(sequence, color_profile, min_area)

