import asyncio
import numpy as np
import shapely.geometry as geom
import json
from mavsdk import System
from mavsdk.offboard import OffboardError, PositionNedYaw


def get_edgesfromplan(plath):
    with open(plath, 'r') as file:
        json_data = json.load(file)
    edges = json_data['geoFence']["polygons"][0]["polygon"]
    print(f"Edges: {edges}")
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

# LLA → NED Umrechnung


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
    print("-- Arming")
    await drone.action.arm()

    await drone.offboard.set_position_ned(PositionNedYaw(0.0, 0.0, -2.0, 0.0))
    try:
        await drone.offboard.start()
    except OffboardError as e:
        print(f"Offboard start failed: {e}")
        await drone.action.disarm()
        return

    print("-- Starting mission")
    for lat, lon in path_coords:
        north, east, down = geodetic_to_ned(lat, lon, 0, reference_point[1],
                                            reference_point[0])
        print(f"Flying to NED: N={north:.1f}, E={east:.1f}, D={down:.1f}")
        await drone.offboard.set_position_ned(PositionNedYaw(north, east, -5.0,
                                                             0.0))
        await asyncio.sleep(5)

    print("-- Landing")
    await drone.action.land()

# Hauptprogramm

async def main(path):
    polygon_coords = get_edgesfromplan(path)
    polygon = geom.Polygon(polygon_coords)

    path_coords = generate_cell_center_points(polygon)
    if not path_coords:
        print("Keine gültigen Rasterpunkte gefunden.")
        return

    start_point = path_coords[0]

    drone = System()
    print("Connecting to drone on udp://:14540 ...")
    await drone.connect(system_address="udp://:14540")

    print("Warte auf Verbindung...")
    async for state in drone.core.connection_state():
        if state.is_connected:
            print("-- Verbunden!")
            break

    print("Warte auf GPS-Fix...")
    async for health in drone.telemetry.health():
        if health.is_global_position_ok:
            print("-- GPS OK")
            break

    await fly_path(drone, path_coords, start_point)

# Start
if __name__ == "__main__":
    path = r"TestPolygon.plan"
    asyncio.run(main(path))
