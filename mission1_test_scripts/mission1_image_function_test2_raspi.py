import modules.image_processing_raspi as image_processing  # type: ignore

pitch = 0  # [degrees] dummy variable
roll = 0  # [degrees] dummy variable
altitude = 10  # [m] dummy variable
heading = 0  # [degrees] dummy variable
speed = 0  # dummy variable
lat_position = 0
long_position = 0  # dummy variable
color_profile = 0  # 0: blue, 1: red, 2: yellow, 3: red2
min_area = 700  # minimum area for contour detection


vid = image_processing.start_videoCapture()
sequence = image_processing.module_main_mission_1_v2(
    vid, pitch, roll, altitude, heading, speed, lat_position, long_position)
image_processing.module_main_mission_1_v2_processing(sequence, color_profile, min_area)
