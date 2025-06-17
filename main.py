import argparse
from missions import mission1_mapping, mission2_precision_landing, mission3_multi_target_landing

def parse_coord(s):
    # If the string contains spaces AND more than one coordinate, split and check only one coordinate
    if " " in s:
        coords = s.split()
        if len(coords) > 1:
            raise argparse.ArgumentTypeError(
                "Nur eine Koordinate erlaubt"
            )
    try:
        lat, lon = map(float, s.split(","))
        return (lat, lon)
    except ValueError:
        raise argparse.ArgumentTypeError("Koordinaten müssen im Format LAT,LONG angegeben werden")

def parse_coord_list(s):
    # Split the input string by whitespace and parse each coordinate
    tokens = s.split()
    if not tokens:
        raise argparse.ArgumentTypeError("Es wurden keine Koordinaten gefunden")
    return [parse_coord(token) for token in tokens]

parser = argparse.ArgumentParser(description="Missionsstart mit Parametern")
parser.add_argument('--mission', type=int, choices=[1,2,3], required=True, help="Nummer der Mission")
parser.add_argument('--landingPosition', type=parse_coord, required=True, help="Landeposition (LAT,LONG)")
parser.add_argument('--targetType', type=str, choices=["red", "yellow", "blue"], help="Farbe der Targets")
parser.add_argument('--area', type=parse_coord_list, help="Liste der Eckpunkte des Suchgebietes (LAT,LONG)")
parser.add_argument('--geofence', type=parse_coord_list, help="Liste der Eckpunkte des Geofence (LAT,LONG)")
parser.add_argument('--targetNumber', type=int, help="Anzahl der Targets")
parser.add_argument('--waypoints', type=parse_coord_list, help="Liste der Wegpunkte (LAT,LONG)")
args = parser.parse_args()

# Check Arguments

if args.mission == 1:
    print("Mission 1")
    # required: landingPosition, targetType and (area XOR waypoints)
    if not (args.landingPosition and args.targetType and ((args.area and not args.waypoints) or (args.waypoints and not args.area))):
        parser.error("Mission 1 erfordert landingPosition, targetType und entweder area oder waypoints (exklusiv)")
    print(f"Landeposition: {args.landingPosition}, Zieltyp: {args.targetType}")
    if args.area:
        print(f"Suchgebiet: {args.area}")
    if args.waypoints:
        print(f"Wegpunkte: {args.waypoints}")
        
    mission1_mapping.run(args.landingPosition, args.targetType, args.area or args.waypoints, args.geofence)
elif args.mission == 2:
    print("Mission 2")
    # required: landingPosition, targetType
    if not(args.landingPosition and args.targetType):
        parser.error("Mission 2 erfordert landingPosition und targetType")
    mission2_precision_landing.run(args.landingPosition, args.targetType, args.geofence)
elif args.mission == 3:
    print("Mission 3")
    # required: landingPosition and targetNumber
    if not(args.landingPosition and args.targetNumber is not None):
        parser.error("Mission 3 erfordert landingPosition und targetNumber")
        
    mission3_multi_target_landing.run(args.landingPosition, args.targetNumber, args.geofence)
    
if args.targetType: 
    print(args.targetType)
    
if args.area:
    for index, (lat, lon) in enumerate(args.area):
        print(f"Punkt {index+1} (Breite: {lat}, Länge: {lon})")
        
if args.landingPosition:
    lat, lon = args.landingPosition
    print(f"Landeposition: {lat},{lon}")