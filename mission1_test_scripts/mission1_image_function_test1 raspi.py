import modules.image_processing as image_processing # type: ignore

pitch = 2  # [degrees] dummy variable
roll = 10  # [degrees] dummy variable
altitude = 10  # [m] dummy variable
heading = 125  # [degrees] dummy variable
speed = 0  # dummy variable
lat_position = 42.01414 # dummy variable
long_position = 10.123213  # dummy variable
color_profile = 1  # 0: blue, 1: red, 2: yellow, 3: red2
min_area = 900  # minimum area for contour detection

vid = image_processing.start_videoCapture()
frame = image_processing.module_main_mission_1(
    vid, color_profile, min_area, pitch, 
    roll, altitude, heading, speed, lat_position, long_position
    )
