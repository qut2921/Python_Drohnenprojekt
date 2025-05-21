import argparse
from missions import mission1_mapping, mission2_precision_landing, mission3_multi_target_landing

parser = argparse.ArgumentParser()
parser.add_argument('--mission', type=int, required=True)
args = parser.parse_args()

# weitere Argumente hinzu
# prüfen der Argumente

if args.mission == 1:
    mission1_mapping.run()
elif args.mission == 2:
    mission2_precision_landing.run()
elif args.mission == 3:
    mission3_multi_target_landing.run()