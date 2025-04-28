import Bildverarbeitung_V2  # type: ignore

pitch = 0  # [degrees] dummy variable
roll = 0  # [degrees] dummy variable
altitude = 10  # [m] dummy variable
heading = 125  # [degrees] dummy variable
speed = 0  # dummy variable
gps_position = (0, 0)  # dummy variable
color_profile = 0  # 0: blue, 1: red, 2: yellow, 3: red2
min_area = 700  # minimum area for contour detection

vid = Bildverarbeitung_V2.start_videoCapture()
frame = Bildverarbeitung_V2.module_main_mission_1(
    vid, color_profile, min_area,
    pitch, roll, altitude, heading, speed, gps_position)
