import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import utils.processor_ground as processor
import utils.list_filter as lf

min_area = 300
# Blue = 0, Red = 1, Yellow = 2, Orange = 4
sequence = 1
condition = "sunny" # condition for color profile only input "cloudy" or "sunny"

for i in range(4):
    if i == 3:
        continue
    color_profile = i
    processor.main_mission_1_post_processing(sequence, color_profile, condition, min_area)
    lf.filter_near_duplicates(lf.choose_folder(color_profile))

