def run(landingPosition, targetType, area, geofence=None):
    # Hier könnte der Code für die Ausführung der Mission 1 stehen
    print(f"Mission 1 gestartet mit Landeposition: {landingPosition}, Zieltyp: {targetType}, Suchgebiet: {area}")
    if geofence:
        print(f"Geofence aktiviert mit Punkten: {geofence}")
    else:
        print("Kein Geofence aktiviert")
    pass