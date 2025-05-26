import asyncio
import json
import logging
import os
import numpy as np
# import pandas as pd
from mavsdk import System
from mavsdk.offboard import PositionNedYaw, OffboardError
from shapely import geometry as geom


logging.basicConfig(level=logging.INFO)


# Funktion zum Einlesen der Plan-Datei
def get_edgesfromplan(plath):
    if not os.path.exists(plath):
        logging.info(f"Fehler: Datei {plath} wurde nicht gefunden.")
        exit(1)
    with open(plath, 'r') as file:
        json_data = json.load(file)
    raw_edges = json_data['geoFence']['polygons'][0]['polygon']
    edges = [{"latitude": p[1], "longitude": p[0]} for p in raw_edges]
    logging.info(f"Edges aus Plan-Datei: {edges}")
    return edges


# Manuelle Eingabe der Punkte
def get_edges_manual():
    edges = [
        {"latitude": 48.768440, "longitude": 11.336833},
        {"latitude": 48.768409, "longitude": 11.336800},
        {"latitude": 48.768298, "longitude": 11.337072},
        {"latitude": 48.768334, "longitude": 11.337113}
    ]
    logging.info(f"Manuelle Edges: {edges}")
    return edges

# Rasterpunkte erzeugen
def generate_cell_center_points(polygon: geom.Polygon, spacing=0.0002,
                                padding=0.00005):
    minx, miny, maxx, maxy = polygon.bounds
    minx -= padding
    miny -= padding
    maxx += padding
    maxy += padding

    x_origins = np.arange(minx - spacing, maxx + spacing, spacing)
    y_origins = np.arange(miny - spacing, maxy + spacing, spacing)

    center_points = []
    for i, x in enumerate(x_origins):
        column = []
        for y in y_origins:
            cell = geom.box(x, y, x + spacing, y + spacing)
            if polygon.intersects(cell):
                cx = x + spacing / 2
                cy = y + spacing / 2
                column.append((cx, cy))
        if i % 2 == 1:
            column.reverse()
        center_points.extend(column)
    return center_points

# LLA zu NED Umrechnung
def geodetic_to_ned(lat, lon, alt, ref_lat, ref_lon, ref_alt=0):
    earth_radius = 6378137.0
    d_lat = lat - ref_lat
    d_lon = lon - ref_lon
    north = d_lat * (np.pi / 180) * earth_radius
    east = d_lon * (np.pi / 180) * earth_radius * np.cos(np.radians(ref_lat))
    down = ref_alt - alt
    return north, east, down

# Offboard-Flugfunktion
async def fly_path(drone, path_coords, reference_point):
    logging.info("-- Arming")
    await drone.action.arm()

    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -2.0, 0.0))
    try:
        await drone.offboard.start()
    except OffboardError as e:
        logging.info(f"Offboard start failed: {e}")
        await drone.action.disarm()
        return

    logging.info("-- Starting mission")
    for lon, lat in path_coords:
        north, east, down = geodetic_to_ned(lat, lon, 0, reference_point[1], 
                                            reference_point[0])
        #logging.info(f"Flying to NED: N={north:.1f}, E={east:.1f}, D={down:.1f}")
        logging.info(f"Flying to GPS: lat={lat:.7f}, lon={lon:.7f}")
        await drone.offboard.set_position_ned(PositionNedYaw(north, east, -5.0,
                                                             0.0))
        await asyncio.sleep(5)

    logging.info("-- Landing")
    await drone.action.land()

# Hauptprogramm
async def main(path, use_manual=False):
    if use_manual:
        polygon_coords = get_edges_manual()
    else:
        polygon_coords = get_edgesfromplan(path)

    polygon = geom.Polygon([
        (point["longitude"], point["latitude"]) for point in polygon_coords
    ])

    path_coords = generate_cell_center_points(polygon)
    if not path_coords:
        logging.info("Keine gültigen Rasterpunkte gefunden.")
        return

    start_point = path_coords[0]

    drone = System()
    logging.info("Connecting to drone on udp://:14540 ...")
    await drone.connect(system_address="udp://:14540")

    logging.info("Warte auf Verbindung...")
    try:
        async def wait_for_connection(drone):
            async for state in drone.core.connection_state():
                if state.is_connected:
                    logging.info("-- Verbunden!")
                    return

        await asyncio.wait_for(wait_for_connection(drone), timeout=20)
    except asyncio.TimeoutError:
        logging.info("Fehler: Verbindung zur Drohne konnte nicht hergestellt werden.")
        return

    logging.info("Warte auf GPS-Fix...")
    try:
        async def wait_for_gps(drone):
            async for health in drone.telemetry.health():
                if health.is_global_position_ok:
                    logging.info("-- GPS OK")
                    return

        await asyncio.wait_for(wait_for_gps(drone), timeout=20)
    except asyncio.TimeoutError:
        logging.info("Fehler: GPS-Fix konnte nicht erreicht werden.")
        return

    await fly_path(drone, path_coords, start_point)

if __name__ == "__main__":
    path = r"TestPolygon.plan"
    use_manual = False  # True: manuelle Punkte, False: Plan-Datei verwenden
    asyncio.run(main(path, use_manual))
    logging.info("Programm beendet.")