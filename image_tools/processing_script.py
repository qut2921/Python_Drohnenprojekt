import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import utils.processor_ground as processor
import utils.list_filter as lf

min_area = 1000
# Blue = 0, Red = 1, Yellow = 2, Orange = 4
sequence = 8
condition = "sunny" # condition for color profile only input "cloudy" or "sunny"


processor.main_mission_1_post_processing(sequence, condition, min_area)
lf.filter_near_duplicates()

