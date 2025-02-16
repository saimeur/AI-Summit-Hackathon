from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import osmnx as ox
import time
from shapely.geometry import MultiPoint, Polygon
from scipy.spatial import ConvexHull

from model.XGboost import RiverLevelPredictor

app = FastAPI()

# On a besoin d'activer CORS sinon il bloque les requêtes venant du front
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales pour stocker la carte préchargée
current_city = "Rennes"  # Ville par défaut
G = None  # Graph de la carte

def get_flooded_zones(nodes_elevations):
    """Détecte les zones inondées et génère des polygones convexes en comparant avec les zones sèches."""
    flooded_points = [(lat, lng) for lat, lng, elevation in nodes_elevations if elevation < 0]
    safe_points = {(lat, lng) for lat, lng, elevation in nodes_elevations if elevation >= 0}
    
    print(f"DEBUG - Nombre total de nœuds analysés : {len(nodes_elevations)}")
    print(f"DEBUG - Nombre de points inondés détectés : {len(flooded_points)}")
    print(f"DEBUG - Exemples de points inondés : {flooded_points[:5]}")
    print(f"DEBUG - Nombre de points secs détectés : {len(safe_points)}")

    if len(flooded_points) < 3:
        return []

    # Trouver les frontières : points inondés ayant un voisin non inondé
    border_points = []
    for lat, lng in flooded_points:
        for dlat, dlng in [(-0.0002, 0), (0.0002, 0), (0, -0.0002), (0, 0.0002),
                            (-0.0002, -0.0002), (0.0002, 0.0002), (-0.0002, 0.0002), (0.0002, -0.0002)]:
            if (lat + dlat, lng + dlng) in safe_points:
                border_points.append((lat, lng))
                break


    if len(border_points) < 3:
        return []

    # Calcul des polygones convexes
    points = MultiPoint(border_points)
    hull = ConvexHull(border_points)
    
    print(f"DEBUG - Nombre de points formant la frontière : {len(border_points)}")
    print(f"DEBUG - Exemples de points frontière : {border_points[:5]}")


    # Liste des coordonnées des zones inondées sous forme de polygones
    polygon_coords = [(points.geoms[i].y, points.geoms[i].x) for i in hull.vertices]

    return [polygon_coords]  # Liste de polygones

def graph_with_0_to_river_level(G, river_level):
    for node, data in G.nodes(data=True):
        if "elevation" in data:  # Vérifier que l'élévation existe
            data["elevation"] -= river_level
    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)

    print(f"DEBUG - min elevation après offset : {gdf_nodes['elevation'].min()}")
    print(f"DEBUG - avg elevation après offset : {gdf_nodes['elevation'].mean()}")

    

def load_map(place: str, river_level: float, network_type="drive"):
    """Charge la carte d'une ville donnée avec les altitudes et met à jour la variable globale G."""
    global G, current_city

    if G is None or place.lower() != current_city.lower():
        print(f"Chargement de la carte pour {place}...")
        G = ox.graph_from_place(place, network_type=network_type, truncate_by_edge=True)

        # Ajouter l'altitude aux noeuds
        original_elevation_url = ox.settings.elevation_url_template
        ox.settings.elevation_url_template = (
            "https://api.opentopodata.org/v1/aster30m?locations={locations}"
        )
        G = ox.elevation.add_node_elevations_google(G, batch_size=100, pause=1)
        G = ox.elevation.add_edge_grades(G)
        ox.settings.elevation_url_template = original_elevation_url
        
        ######### Offset the river level to the graph elevation #########
        gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)
        print(f"DEBUG - min elevation avant offset : {gdf_nodes['elevation'].min()}")
        print(f"DEBUG - avg elevation avant offset : {gdf_nodes['elevation'].mean()}")
        graph_with_0_to_river_level(G, river_level)
        G = ox.elevation.add_edge_grades(G, add_absolute=True)

        current_city = place.lower()
        print(f"Carte de {place} chargée avec succès, élévation incluse !")
        print('TEEEEEEEEEEEEEEEESSST')


# Charger la carte initiale de Rennes avec les élévations au démarrage du serveur
load_map("Saintes, Nouvelle-Aquitaine", river_level=7)

def get_water_level_pred(curser1, curser2, curser3):
    estimator = RiverLevelPredictor()
    X_new = estimator.create_data_from_curser([curser1, curser2, curser3], (100, 1))
    pred = estimator.predict(X_new)
    print(f' DEBUG - Prédiction du niveau de l\'eau : {pred}')
    return pred

def coord_path_for_evacuation(place, origin, destination, network_type="drive", water_level=0):
    '''
    This function returns the coordinates of the path for evacuation

    Parameters
    ----------
    place : str
        "Chelles, Seine-et-Marne, France"
        The city adress.
    origin : tuple
        (48.883, 2.600)
        The coordinates of the origin (latitude, longitude).
    detination : tuple
        (48.885, 2.605)
        The coordinates of the destination (latitude, longitude).
    network_type : str, optional
        {"drive", "walk", "bike", "all", "all_private", "none"}
        The type of network to use for the path. The default is "drive".

    Returns
    -------
    coord_route : list
        [(48.883, 2.600), (48.884, 2.601), (48.885, 2.605)] or None if path is impossible .
        The coordinates of the path.
    all_nodes_elevations : list
        [(node1, latitude1, longitude1), (node2, latitude2, longitude2), ...]

    '''

    G_neg = G.copy()

    ######### Add water elevation to the graph #########
    # add water level to each of the nodes of the graph G
    for node, data in G_neg.nodes(data=True):
        if "elevation" in data:  # Vérifier que l'élévation existe
            data["elevation"] -= water_level

    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G_neg)
    print(f"DEBUG - min elevation après river_elevation : {gdf_nodes['elevation'].min()}")
    print(f"DEBUG - avg elevation après river_elevation : {gdf_nodes['elevation'].mean()}")

    G1 = G_neg.copy()

    # add edge grades and their absolute values

    gdf_nodes, gdf_edges = ox.graph_to_gdfs(G1)
    all_nodes_elevations = [(data["y"], data["x"], data["elevation"]) for node, data in G1.nodes(data=True)]

    ######### Remove nodes with negative elevation #########
    nodes_to_remove = [node for node, data in G1.nodes(data=True) if data.get("elevation", 0) < 0]
    print(f"Nœuds supprimés pour inondation : {len(nodes_to_remove)}")


    G_neg.remove_nodes_from(nodes_to_remove)

    gdf_filtered_nodes, gdf_edges = ox.graph_to_gdfs(G_neg)

    ######### Get the path #########

    '''
    # select an origin and destination node and a bounding box around them
    origin = ox.distance.nearest_nodes(G, origin[0], origin[1])
    destination = ox.distance.nearest_nodes(G, destination[0], destination[1])
    '''

    try:
        origin_node = ox.distance.nearest_nodes(G1, origin[1], origin[0])
        destination_node = ox.distance.nearest_nodes(G1, destination[1], destination[0])
    except Exception as e:
        print(f"Erreur : Impossible de trouver un nœud proche - {e}")
        return None, all_nodes_elevations



    route = ox.routing.shortest_path(G_neg, origin_node, destination_node, weight="length")
    if route is None:
        print("Aucun chemin trouvé, la destination est inaccessible.")
        return None , all_nodes_elevations

    coord_route = list(gdf_filtered_nodes.loc[route, ["y", "x"]].itertuples(index=False, name=None))
    print(f"Chemin trouvé avec {len(coord_route)} étapes.")

    print(f"DEBUG - Coordonnées du chemin : {coord_route[:5]}... (total: {len(coord_route)})")
    print(f"DEBUG - Premiers nœuds avec élévation : {all_nodes_elevations[:5]}... (total: {len(all_nodes_elevations)})")

    return coord_route , all_nodes_elevations


'''
def coord_path_for_evacuation(place, origin, destination, network_type="drive", water_level=0):
    """
    Cette fonction retourne les coordonnées du chemin d'évacuation.

    Parameters
    ----------
    place : str
        "Chelles, Seine-et-Marne, France"
        Le nom de la ville. 
    origin : tuple
        (48.883, 2.600)
        Coordonnées du point de départ (latitude, longitude).
    destination : tuple
        (48.885, 2.605)
        Coordonnées du point d'arrivée (latitude, longitude).
    network_type : str, optional
        {"drive", "walk", "bike", "all", "all_private", "none"}
        Type de réseau à utiliser pour la navigation.
    water_level : float, optional
        Niveau d'eau en mètres à soustraire à l'altitude des nœuds.

    Returns
    -------
    coord_route : list
        Liste des coordonnées [(lat1, lon1), (lat2, lon2), ...] du chemin optimal ou `None` si aucun chemin n'existe.
    all_nodes_elevations : list
        Liste des nœuds avec altitude [(node, lat, lon, elevation), ...]
    """

    start_time = time.time()
    print(f"Chargement du graphe pour {place}...")

    G = ox.graph_from_place(place, network_type=network_type, truncate_by_edge=True)

    load_time = time.time()
    print(f"Temps de chargement du graphe : {load_time - start_time:.2f} sec")

    # 🔹 Ajouter l'altitude aux nœuds
    original_elevation_url = ox.settings.elevation_url_template
    ox.settings.elevation_url_template = "https://api.opentopodata.org/v1/aster30m?locations={locations}"
    G = ox.elevation.add_node_elevations_google(G, batch_size=100, pause=1)
    G = ox.elevation.add_edge_grades(G)
    ox.settings.elevation_url_template = original_elevation_url

    # ⏳ Timer après ajout de l'altitude
    elevation_time = time.time()
    print(f"Temps d'ajout des altitudes : {elevation_time - load_time:.2f} sec")

    # 🔹 Réduire l'altitude des nœuds selon le niveau d'eau
    for node, data in G.nodes(data=True):
        if "elevation" in data:
            data["elevation"] -= water_level

    nodes_to_remove = [node for node, data in G.nodes(data=True) if data.get("elevation", 0) < 0]
    G.remove_nodes_from(nodes_to_remove)

    print(f"Nœuds supprimés pour inondation : {len(nodes_to_remove)}")

    filter_time = time.time()
    print(f"Temps de filtrage des nœuds inondés : {filter_time - elevation_time:.2f} sec")

    gdf_nodes, _ = ox.graph_to_gdfs(G)
    all_nodes_elevations = [(data["y"], data["x"], data["elevation"]) for node, data in G.nodes(data=True)]

    try:
        origin_node = ox.distance.nearest_nodes(G, origin[1], origin[0])
        destination_node = ox.distance.nearest_nodes(G, destination[1], destination[0])
    except Exception as e:
        print(f"Erreur : Impossible de trouver un nœud proche - {e}")
        return None, all_nodes_elevations

    nearest_time = time.time()
    print(f"Temps pour trouver les nœuds les plus proches : {nearest_time - filter_time:.2f} sec")

    route = ox.routing.shortest_path(G, origin_node, destination_node, weight="length")

    if route is None:
        print("Aucun chemin trouvé, la destination est inaccessible.")
        return None, all_nodes_elevations

    coord_route = list(gdf_nodes.loc[route, ["y", "x"]].itertuples(index=False, name=None))

    path_time = time.time()
    print(f"Temps pour calculer le chemin : {path_time - nearest_time:.2f} sec")

    print(f"Chemin trouvé avec {len(coord_route)} étapes.")
    
    print(f"DEBUG - Coordonnées du chemin : {coord_route[:5]}... (total: {len(coord_route)})")
    print(f"DEBUG - Premiers nœuds avec élévation : {all_nodes_elevations[:5]}... (total: {len(all_nodes_elevations)})")
    return coord_route, all_nodes_elevations




    coord_route = list(gdf_filtered_nodes.loc[route, ["y", "x"]].itertuples(index=False, name=None))

    return coord_route , all_nodes_elevations
'''

@app.get("/evacuation-path")
def get_evacuation_path(
    place: str,
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
    network_type: str = "drive",
    water_level: float = 0,
):
    print(f"Requête reçue: {place}, {origin_lat}, {origin_lng} → {destination_lat}, {destination_lng}, Eau: {water_level}")

    try:
        path, all_nodes_elevation = coord_path_for_evacuation(
            place, (origin_lat, origin_lng), (destination_lat, destination_lng), network_type, water_level
        )

        if path is None:
            print("Aucun chemin disponible, envoi d'une réponse 400 au front.")
            return {"error": "Aucun chemin possible, la destination est inondée."}, 400

        print(f"Chemin trouvé avec {len(path)} étapes")
        flooded_zones = get_flooded_zones(all_nodes_elevation)
        print(f"Zones inondées envoyées au frontend : {flooded_zones[:4]} ")
        return {
            "path": [{"lat": lat, "lng": lng} for lat, lng in path] if path else None,
            "flooded_zones": [[{"lat": lat, "lng": lng} for lat, lng in polygon] for polygon in flooded_zones]
        }

    except HTTPException as http_ex:
        raise http_ex

    except Exception as e:
        print(f"ERREUR : {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/coordinates")
def get_coordinates():
    return {
        "path": [
            {"lat": 48.8566, "lng": 2.3522},
            {"lat": 48.8575, "lng": 2.3555},
            {"lat": 48.8580, "lng": 2.3610},
            {"lat": 48.8605, "lng": 2.3650},
        ]
    }

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de prévision des inondations !"}
