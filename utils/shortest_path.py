import itertools
import math
import matplotlib.pyplot as plt   # Neuer Import für Diagramme

def total_distance(route):
    """Berechnet die Gesamtdistanz entlang eines Pfades."""
    distance = 0
    for i in range(len(route) - 1):
        distance += math.dist(route[i], route[i+1])
    return distance

def draw_path(launch_point, path, landing_point, all_targets=None):
    """
    Zeichnet einen Pfad als Diagramm.
    
    Parameter:
      launch_point (Tuple[float, float]): Der Startpunkt.
      path (List[Tuple[float, float]]): Liste der Zwischenpunkte.
      landing_point (Tuple[float, float]): Der Endpunkt.
      all_targets (List[Tuple[float, float]], optional): Vollständige Liste der verfügbaren Punkte.
         Falls angegeben, werden Punkte, die nicht im Pfad enthalten sind, zusätzlich angezeigt.
    """
    # Vollständiger Pfad: Startpunkt + Zwischenpunkte + Endpunkt       
    full_route = [launch_point] + list(path) + [landing_point]
    x_coords = [pt[0] for pt in full_route]
    y_coords = [pt[1] for pt in full_route]
    
    plt.figure()
    plt.plot(x_coords, y_coords, marker='o', linestyle='-', color='blue', label='Pfad')
    plt.scatter([launch_point[0]], [launch_point[1]], color='green', s=100, label='Start')
    plt.scatter([landing_point[0]], [landing_point[1]], color='red', s=100, label='Landing')
    
    if all_targets is not None:
        # Bestimme Punkte, die nicht im Pfad sind
        unused_targets = [pt for pt in all_targets if pt not in path]
        if unused_targets:
            x_unused = [pt[0] for pt in unused_targets]
            y_unused = [pt[1] for pt in unused_targets]
            plt.scatter(x_unused, y_unused, marker='x', color='orange', s=100, label='Nicht ausgewählt')
    
    plt.title("Kürzester Pfad")
    plt.xlabel("X-Koordinate")
    plt.ylabel("Y-Koordinate")
    plt.legend()
    plt.grid(True)
    plt.show()

def find_shortest_path(launch_point, landing_point, targets, n):
    """
    Ermittelt den kürzesten Pfad, der mit dem Launch-Punkt beginnt und mit dem Landing-Punkt endet,
    bestehend aus n Zwischenpunkten.

    Parameter:
      launch_point (Tuple[float, float]): Der Launch-Punkt des Pfades.
      landing_point (Tuple[float, float]): Der Landing-Punkt.
      targets (List[Tuple[float, float]]): Liste verfügbarer Zwischenpunkte.
      n (int): Anzahl der Zwischenpunkte im Pfad.

    Rückgabe:
      List[Tuple[float, float]]: Der Pfad als Liste von Punkten, wobei der Landing-Punkt nicht enthalten ist.
    
    Hinweis: Falls n > len(targets) wird eine ValueError ausgelöst.
    """
    if n < 0:
        raise ValueError("Die Anzahl n darf nicht negativ sein.")
    
    if n > len(targets):
        raise ValueError("Nicht genügend Zielpunkte vorhanden, um einen Pfad mit {} Zwischenpunkten zu bilden.".format(n))
    
    best_route = None
    best_distance = float("inf")
    
    # Wähle n Zwischenpunkte aus der Liste der targets
    for combo in itertools.combinations(targets, n):
        # Prüfe alle Permutationen der ausgewählten Zwischenpunkte
        for perm in itertools.permutations(combo):
            route = [launch_point] + list(perm) + [landing_point]
            dist = total_distance(route)
            if dist < best_distance:
                best_distance = dist
                best_route = route

    # Entferne den Start- und Landing-Punkt aus der zurückgegebenen Liste
    return best_route[1:-1]  # Rückgabe ohne den Start- und Landing-Punkt

if __name__ == "__main__":
    # Beispielaufruf
    points = [(3, 4), (4, 2), (6, 3), (5, 6), (1, 6)]
    start = (0, 0)
    landing = (3, 0)
    n = 3
    shortest_path = find_shortest_path(start, landing, points, n)
    print("The shortest path (without start and landing points) is:", shortest_path)
    print("The total distance is:", total_distance([start] + shortest_path + [landing]))
    
    # Zeichne den gefundenen Pfad als Diagramm und zeige zudem die nicht ausgewählten Zwischenpunkte
    draw_path(start, shortest_path, landing, all_targets=points)