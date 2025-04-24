import Bildverarbeitung_V2  # type: ignore

pitch = 0  # [degrees] dummy variable
roll = 0  # [degrees] dummy variable
altitude = 10  # [m] dummy variable
heading = 125  # [degrees] dummy variable
speed = 0  # dummy variable
gps_position = (47.0134, 10.134)  # dummy variable
color_profile = 1  # 0: blue, 1: red, 2: yellow, 3: red2
min_area = 900  # minimum area for contour detection

vid = Bildverarbeitung_V2.start_videoCapture()
frame = Bildverarbeitung_V2.module_main_mission_1_v2(
    vid, pitch, roll, altitude, heading, speed, gps_position)