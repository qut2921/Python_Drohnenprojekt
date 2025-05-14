import modules.image_processing_raspi as ip # type: ignore
import modules.controller_functions as cl
from mavsdk import System
import asyncio

color_profile = 0  # 0: blue, 1: red, 2: yellow, 3: red2
min_area = 900  # minimum area for contour detection
pitch = 0
roll = 0
altitude = 10
heading = 120
speed = 10
lat_position = 42.1231221312
long_position = 102.124214124
mission = 1  # mission number

vid = ip.start_videoCapture(mission)
sequence = ip.test_main_mission_1(vid, pitch, roll, altitude, heading, speed, lat_position, long_position)
ip.main_mission_1_post_processing(sequence, color_profile, min_area)
