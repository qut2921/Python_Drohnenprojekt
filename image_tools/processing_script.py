import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import utils.processor_ground as pro

min_area = 300
color_profile = 1
pro.main_mission_1_post_processing(1,color_profile,min_area)
