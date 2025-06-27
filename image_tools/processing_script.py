"""
Main script for post-processing image sequences in Mission 1 and filtering duplicate object detections.

This script imports utility modules for processing object detections (`processor_ground`) and
removing near-duplicate entries (`list_filter`). It sets the detection parameters, processes a 
specified image sequence to identify objects using HSV color segmentation, estimates their GPS 
positions, and annotates relevant metadata. Afterwards, it filters out duplicates based on spatial 
proximity and color similarity using the Haversine distance.

Steps:
    - Configure minimum contour area (`min_area`) for detection validity.
    - Specify weather condition ('sunny' or 'cloudy') to adapt HSV color profiles.
    - Process frames from the image sequence and save results with bounding boxes and CSV metadata.
    - Eliminate near-duplicate entries within 1.5 meters and matching color via `filter_near_duplicates`.

Note:
    - Requires the utilities `processor_ground.main_mission_1_post_processing` and `list_filter.filter_near_duplicates`.

Usage:
    Adjust `sequence`, `min_area`, and `condition` as needed before running the script.
    'sequence' should be set to highest sequence number in the Mission1 folder.
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import utils.processor_ground as processor
import utils.list_filter as lf

min_area = 1000
# Blue = 0, Red = 1, Yellow = 2, Orange = 4
sequence = 2
condition = "sunny" # condition for color profile only input "cloudy" or "sunny"


processor.main_mission_1_post_processing(sequence, condition, min_area)
lf.filter_near_duplicates()

