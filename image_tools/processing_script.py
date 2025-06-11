import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import utils.processor_ground as processor

min_area = 300
# Blue = 0, Red = 1, Yellow = 2, Orange = 4
color_profile = 0 
sequence = 1
processor.main_mission_1_post_processing(sequence, color_profile, min_area)
