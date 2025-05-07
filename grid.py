import matplotlib.pyplot as plt
import shapely.geometry as geom
import numpy as np


def generate_cell_center_points(polygon: geom.Polygon, spacing=0.0002,
                                padding=0.00005):
    minx, miny, maxx, maxy = polygon.bounds
    minx -= padding
    miny -= padding
    maxx += padding
    maxy += padding

    # Rasterursprünge
    x_origins = np.arange(minx - spacing, maxx + spacing, spacing)
    y_origins = np.arange(miny - spacing, maxy + spacing, spacing)

    center_points = []

    for i, x in enumerate(x_origins):
        column = []
        for y in y_origins:
            # Erzeuge Quadrat (Zelle)
            cell = geom.box(x, y, x + spacing, y + spacing)
            if polygon.intersects(cell):
                # Mittelpunkt des Quadrats
                cx = x + spacing / 2
                cy = y + spacing / 2
                column.append((cx, cy))
        if i % 2 == 1:
            column.reverse()  # Für Zickzack
        center_points.extend(column)

    return x_origins, y_origins, center_points


def plot_polygon_raster_path(polygon_coords, x_origins, y_origins, path_points,
                             start_point=None, end_point=None, spacing=0.0002):
    fig, ax = plt.subplots(figsize=(10, 10))
    poly = geom.Polygon(polygon_coords)

    # Polygon
    x, y = zip(*poly.exterior.coords)
    ax.plot(x, y, 'blue', label='Polygon')

    # Rasterlinien
    for x in x_origins:
        ax.plot([x, x], [y_origins[0], y_origins[-1]], 'r--', linewidth=0.5)
    for y in y_origins:
        ax.plot([x_origins[0], x_origins[-1]], [y, y], 'r--', linewidth=0.5)

    # Flugweg
    if path_points:
        px, py = zip(*path_points)
        ax.plot(px, py, 'g-', label='Flugweg')
        ax.plot(px, py, 'bo', markersize=3)

    # Start/Endpunkt
    if start_point:
        ax.plot(*start_point, 'go', markersize=10, label='Startpunkt')
    if end_point:
        ax.plot(*end_point, 'ro', markersize=10, label='Endpunkt')

    ax.set_aspect('equal')
    ax.set_title("Raster-Mittelpunkte & Flugweg")
    ax.set_xlabel("Längengrad (°)")
    ax.set_ylabel("Breitengrad (°)")
    ax.legend()
    ax.grid(True)
    plt.tight_layout()
    plt.show()


# Polygon-Koordinaten
polygon_coords = [
    (-73.8857, 40.7484),
    (-73.8850, 40.7484),
    (-73.8841, 40.7495),
    (-73.8853, 40.7489),
    (-73.8862, 40.7490),
    (-73.8861, 40.7487),
    (-73.8857, 40.7484)
]
polygon = geom.Polygon(polygon_coords)

spacing = 0.0002
x_origins, y_origins, path_points = generate_cell_center_points(
    polygon, spacing=spacing
)

# Startpunkt
# start_lat = polygon_coords[0][1]
# start_lon = (polygon_coords[0][0] + polygon_coords[6][0]) / 2
# start_point = (start_lon, start_lat)
start_point = (-73.8855, 40.7483)
# Endpunkt
# end_lat = polygon_coords[1][1]
# end_lon = (polygon_coords[1][0] + polygon_coords[2][0]) / 2
# end_point = (end_lon, end_lat)
end_point = (-73.8850, 40.7483)

# Flugweg mit Start/Endpunkt
path_points.insert(0, start_point)
path_points.append(end_point)

# Wegpunkte als Liste ausgeben (in Reihenfolge des Abflugs)
print("\nWegpunkte in GPS-Koordinaten (Längengrad, Breitengrad):")
for i, point in enumerate(path_points):
    print(f"{i+1:02d}: Lon: {point[0]:.7f}, Lat: {point[1]:.7f}")
# Plot
plot_polygon_raster_path(polygon_coords,
                         x_origins,
                         y_origins,
                         path_points,
                         start_point,
                         end_point,
                         spacing=spacing)
