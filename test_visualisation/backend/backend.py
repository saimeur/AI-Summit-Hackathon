from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import osmnx as ox

app = FastAPI()

# Activer CORS pour permettre la connexion avec le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales pour stocker la carte préchargée
current_city = "Rennes"  # Ville par défaut
G = None  # Graph de la carte


def load_map(place: str, network_type="drive"):
    """Charge la carte d'une ville donnée avec les altitudes et met à jour la variable globale G."""
    global G, current_city

    if G is None or place.lower() != current_city.lower():
        print(f"📍 Chargement de la carte pour {place}...")
        G = ox.graph_from_place(place, network_type=network_type, truncate_by_edge=True)

        # Ajouter l'altitude aux noeuds
        original_elevation_url = ox.settings.elevation_url_template
        ox.settings.elevation_url_template = (
            "https://api.opentopodata.org/v1/aster30m?locations={locations}"
        )
        G = ox.elevation.add_node_elevations_google(G, batch_size=100, pause=1)
        G = ox.elevation.add_edge_grades(G)
        ox.settings.elevation_url_template = original_elevation_url

        current_city = place.lower()
        print(f"✅ Carte de {place} chargée avec succès, élévation incluse !")


# Charger la carte initiale de Rennes avec les élévations au démarrage du serveur
load_map("Rennes")


def coord_path_for_evacuation(
    place, origin, destination, network_type="drive", water_level=0
):
    """
    Cette fonction retourne les coordonnées du chemin d'évacuation.
    """
    global G, current_city

    # Vérifier si la carte actuelle correspond à la ville demandée
    if place.lower() != current_city.lower():
        load_map(place, network_type)
        print("🔄 Changement de ville")

    # Ajuster le niveau d'eau
    for node, data in G.nodes(data=True):
        if "elevation" in data:
            data["elevation"] -= water_level

    # Supprimer les noeuds inondés
    nodes_to_remove = [
        node for node, data in G.nodes(data=True) if data.get("elevation", 0) < 0
    ]
    G.remove_nodes_from(nodes_to_remove)

    # Convertir le graph en dataframe pour récupérer les coordonnées
    gdf_nodes, _ = ox.graph_to_gdfs(G)

    # Trouver les noeuds les plus proches de l'origine et de la destination
    origin_node = ox.distance.nearest_nodes(G, origin[1], origin[0])
    destination_node = ox.distance.nearest_nodes(G, destination[1], destination[0])

    # Trouver le chemin le plus court
    route = ox.routing.shortest_path(G, origin_node, destination_node, weight="length")

    # Convertir en liste de coordonnées
    coord_route = list(
        gdf_nodes.loc[route, ["y", "x"]].itertuples(index=False, name=None)
    )

    return coord_route


@app.get("/evacuation-path")
def get_evacuation_path(
    place: str = Query(..., description="Nom de la ville ou de la région"),
    origin_lat: float = Query(..., description="Latitude de l'origine"),
    origin_lng: float = Query(..., description="Longitude de l'origine"),
    destination_lat: float = Query(..., description="Latitude de la destination"),
    destination_lng: float = Query(..., description="Longitude de la destination"),
    network_type: str = Query("drive", description="Type de réseau de transport"),
    water_level: float = Query(0, description="Niveau d'eau ajouté aux élévations"),
):
    path = coord_path_for_evacuation(
        place,
        (origin_lat, origin_lng),
        (destination_lat, destination_lng),
        network_type,
        water_level,
    )
    return {"path": [{"lat": lat, "lng": lng} for lat, lng in path]}


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
