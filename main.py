import argparse
from missions import mission1_mapping, mission2_precision_landing, mission3_multi_target_landing

def parse_koord(s):
    try:
        lat, lon = map(float, s.split(","))
        return (lat, lon)
    except ValueError:
        raise argparse.ArgumentTypeError("Koordinaten müssen im Format LAT,LONG angegeben werden")

parser = argparse.ArgumentParser(description="Missionsstart mit Parametern")
parser.add_argument('--mission', type=int, choices=[1,2,3], required=True, help="Nummer der Mission")
parser.add_argument('--landingPosition', type=parse_koord, required=True, help="Landeposition (LAT,LONG)")
parser.add_argument('--targetType', type=str, choices=["red", "yellow", "blue"], help="Farbe der Targets")
parser.add_argument('--area', type=parse_koord, nargs="+", help="Liste der Eckpunkte des Suchgebietes (LAT,LONG)")
parser.add_argument('--geofence', type=parse_koord, nargs="+", help="Liste der Eckpunkte des Geofence (LAT,LONG)")
args = parser.parse_args()

# Check Arguments

if args.mission == 1:
    print("Mission 1")
    
    # required: landingPosition, targetType, area
    if not(args.landingPosition and args.targetType and args.area):
        parser.error("Mission 1 erfordert landingPosition, targetType und area")
        
    #mission1_mapping.run(args.landingPosition, args.targetType, args.area, args.geofence)
elif args.mission == 2:
    print("Mission 2")
    
    # required: landingPosition, targetType
    if not(args.landingPosition and args.targetType):
        parser.error("Mission 2 erfordert landingPosition und targetType")
        
    #mission2_precision_landing.run(args.landingPosition, args.targetType, args.geofence)
elif args.mission == 3:
    print("Mission 3")
    
    # required: landingPosition
    if not(args.landingPosition):
        parser.error("Mission 3 erfordert landingPosition")
        
    #mission3_multi_target_landing.run(args.landingPosition,args.geofence)
    
if args.targetType: 
    print(args.targetType)
    
if args.area:
    for index, (lat, lon) in enumerate(args.area):
        print(f"Punkt {index+1} (Breite: {lat}, Länge: {lon})")
        
if args.landingPosition:
    lat, lon = args.landingPosition
    print(f"Landeposition: {lat},{lon}")