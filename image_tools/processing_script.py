import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import utils.image_processing_raspi as ip

min_area = 3000
color_profile = 1
ip.main_mission_1_post_processing(1,color_profile,min_area)
