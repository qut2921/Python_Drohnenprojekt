import asyncio
import json
import logging
import os
import numpy as np
from shapely import geometry as geom

logging.basicConfig(level=logging.INFO)

# --- Punktquellen -----------------------------------------------------

def get_edgesfromplan(path):
    if not os.path.exists(path):
        logging.info(f"Fehler: Datei {path} wurde nicht gefunden.")
        exit(1)
    with open(path, 'r') as file:
        json_data = json.load(file)
    raw_edges = json_data['geoFence']['polygons'][0]['polygon']
    edges = [{"latitude": p[1], "longitude": p[0]} for p in raw_edges]
    logging.info(f"Edges aus Plan-Datei: {edges}")
    return edges

def get_edges_manual():
    edges = [
        {"latitude": 48.7683120, "longitude": 11.3358300},
        {"latitude": 48.7682250, "longitude": 11.3357260},
        {"latitude": 48.7675320, "longitude": 11.3371370},
        {"latitude": 48.7676310, "longitude": 11.3372290}
    ]
    logging.info(f"Manuelle Edges: {edges}")
    return edges

# def get_edges_from_excel(filepath, sheetname='Sheet1'):
#     if not os.path.exists(filepath):
#         logging.info(f"Fehler: Excel-Datei {filepath} wurde nicht gefunden.")
#         exit(1)
#     df = pd.read_excel(filepath, sheet_name=sheetname)
#     if 'latitude' not in df.columns or 'longitude' not in df.columns:
#         logging.info("Excel-Datei muss Spalten 'latitude' und 'longitude' enthalten.")
#         exit(1)
#     edges = df[['latitude', 'longitude']].to_dict(orient='records')
#     logging.info(f"Edges aus Excel-Datei: {edges}")
#     return edges

# --- Rasterpunkte erzeugen --------------------------------------------

def generate_cell_center_points(polygon: geom.Polygon, spacing=0.0001, padding=0.00005):
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

def geodetic_to_ned(lat, lon, alt, ref_lat, ref_lon, ref_alt=0):
    earth_radius = 6378137.0
    d_lat = lat - ref_lat
    d_lon = lon - ref_lon
    north = d_lat * (np.pi / 180) * earth_radius
    east = d_lon * (np.pi / 180) * earth_radius * np.cos(np.radians(ref_lat))
    down = ref_alt - alt
    return north, east, down

# --- Hauptprogramm ----------------------------------------------------

async def main(input_mode, path=None, excel_path=None):
    if input_mode == "manual":
        polygon_coords = get_edges_manual()
    elif input_mode == "plan":
        polygon_coords = get_edgesfromplan(path)
    else:
        logging.info("Ungültiger input_mode. Wähle 'manual' oder 'plan'.")
        return

    polygon = geom.Polygon([
        (point["longitude"], point["latitude"]) for point in polygon_coords
    ])

    path_coords = generate_cell_center_points(polygon)
    if not path_coords:
        logging.info("Keine gültigen Rasterpunkte gefunden.")
        return
    logging.info("Generierte Raster-Wegpunkte (lat, lon):")
    for lon, lat in path_coords:
        logging.info(f"{lat:.7f}, {lon:.7f}")

# --- Startkonfiguration -----------------------------------------------

if __name__ == "__main__":
    mode = "manual"  # Optionen: "manual", "plan"
    plan_path = r"TestPolygon.plan"
    asyncio.run(main(input_mode=mode, path=plan_path))
