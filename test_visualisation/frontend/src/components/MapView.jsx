import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import "leaflet.heat";
import { useMap } from "react-leaflet";


// Icône pour les points de départ et d'arrivée
const evacuationIcon = new L.Icon({
  iconUrl: 'https://upload.wikimedia.org/wikipedia/commons/e/ec/RedDot.svg',
  iconSize: [16, 16],  
  iconAnchor: [8, 8],  
  popupAnchor: [0, -8]
});

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
    shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
});

// function HeatmapLayer({ nodesElevation }) {
//   const map = useMap();

//   useEffect(() => {
//       if (!map || nodesElevation.length === 0) return;

//       // 🔹 Filtrer les nœuds inondés (altitude négative)
//       const heatData = nodesElevation
//           .filter(([lat, lng, elevation]) => elevation < 0)
//           .map(([lat, lng]) => [lat, lng, 1]); // Dernier paramètre = intensité

//       console.log("🔵 Points inondés détectés :", heatData);

//       if (heatData.length === 0) return;

//       const heatLayer = L.heatLayer(heatData, {
//           radius: 20,
//           blur: 15,
//           maxZoom: 13,
//           // Dégradé bleu → bleu clair 
//           gradient: { 0.4: 'blue', 0.65: 'cyan', 1: 'white' }
//       });

//       map.addLayer(heatLayer);

//       // ⚠️ Nettoyer la heatmap lors du démontage
//       return () => {
//           map.removeLayer(heatLayer);
//       };
//   }, [map, nodesElevation]);

//   return null;
// }

function FloodedZonesLayer({ floodedZones }) {
  const map = useMap(); // 🔥 Accès à la carte Leaflet

  useEffect(() => {
    if (!map || floodedZones.length === 0) return;

    console.log("📌 Polygones reçus :", floodedZones);

    // 🔹 Création des polygones
    const polygonLayers = floodedZones.map((zone, index) =>
      L.polygon(zone, {
        color: "blue",
        fillColor: "blue",
        fillOpacity: 0.5
      }).addTo(map)
    );

    // 🗑️ Nettoyage des anciens polygones
    return () => {
      polygonLayers.forEach(layer => map.removeLayer(layer));
    };
  }, [map, floodedZones]);

  return null;
}



export default function MapView() {
  const [path, setPath] = useState([]);
  const [city, setCity] = useState("Rennes");
  const [startPoint, setStartPoint] = useState("48.11588, -1.66927");
  const [endPoint, setEndPoint] = useState("48.11963, -1.65031");
  const [waterLevel, setWaterLevel] = useState(0);
  const [loading, setLoading] = useState(false);
  const [aucunChemin, setAucunChemin] = useState(false);
  // const [nodesElevation, setNodesElevation] = useState([]);
  const [floodedZones, setFloodedZones] = useState([]);


  const fetchEvacuationPath = async () => {
    try {
      setLoading(true);
      setAucunChemin(false);

      const [startLat, startLng] = startPoint.split(",").map(coord => parseFloat(coord.trim()));
      const [endLat, endLng] = endPoint.split(",").map(coord => parseFloat(coord.trim()));

      if (isNaN(startLat) || isNaN(startLng) || isNaN(endLat) || isNaN(endLng)) {
        alert("Erreur : Vérifiez les coordonnées saisies !");
        setLoading(false);
        return;
      }

      const response = await fetch(`http://localhost:8000/evacuation-path?place=${city}&origin_lat=${startLat}&origin_lng=${startLng}&destination_lat=${endLat}&destination_lng=${endLng}&water_level=${waterLevel}`);

      const data = await response.json();

      if (!data || !data.path || data.path === null) {
        console.warn("🚨 Aucun chemin trouvé, affichage de l'alerte !");
        setAucunChemin(true);
        setPath([]);
        console.log("Valeur de `aucunChemin` :", aucunChemin);
        return;
      }

      setPath(data.path.map(point => [point.lat, point.lng]));
      console.log("Chemin reçu :", data.path);
      console.log("Zones inondées reçues :", data.flooded_zones);

      if (data.flooded_zones) {
          setFloodedZones(data.flooded_zones);
      } else {
          setFloodedZones([]);
      }
    

    } catch (error) {
      console.error("Erreur lors du fetch :", error);
      setAucunChemin(true);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ 
      display: "grid", 
      gridTemplateColumns: "75% 25%",  
      height: "90vh", 
      width: "90vw",
      overflow: "hidden"
    }}>
    
      <div style={{ border: "3px solid black" }}>
      <MapContainer center={[48.1146, -1.657]} zoom={13} style={{ width: "100%", height: "100%" }}>
          <TileLayer
              url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
              attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          />

          {/* <HeatmapLayer nodesElevation={nodesElevation} /> */}
          <FloodedZonesLayer floodedZones={floodedZones} />

          {path.length > 1 && (
              <>
                  <Marker position={path[0]} icon={evacuationIcon}>
                      <Popup>Départ</Popup>
                  </Marker>
                  <Marker position={path[path.length - 1]} icon={evacuationIcon}>
                      <Popup>Arrivée</Popup>
                  </Marker>
              </>
          )}

          {path.length > 1 && <Polyline positions={path} color="green" />}
      </MapContainer>


        {aucunChemin && (
          <div style={{position: "absolute", top: "50%", left: "50%", transform: "translate(-50%, -50%)", backgroundColor: "rgba(255, 0, 0, 0.9)", color: "white",
            padding: "20px", borderRadius: "10px", textAlign: "center", width: "50%", maxWidth: "400px", boxShadow: "0px 0px 10px rgba(0,0,0,0.5)", zIndex: 9999
          }}>
            <h2 style={{ fontSize: "20px", fontWeight: "bold" }}>⚠️ Zone inondée ⚠️</h2>
            <p>Votre destination est inondée. Il est recommandé de rester en sécurité chez vous.</p>
            <button onClick={() => setAucunChemin(false)} 
              style={{ marginTop: "10px", padding: "10px", backgroundColor: "white", color: "red", border: "none", cursor: "pointer", fontWeight: "bold", borderRadius: "5px" }}>
              Fermer
            </button>
          </div>
        )}
      </div>
  
      {/* Colonne des paramètres */}
      <div style={{ background: "#242424", padding: "20px", display: "flex", flexDirection: "column", justifyContent: "space-between",borderLeft: "10px solid #242424", boxShadow: "-2px 0 5px rgba(0, 0, 0, 0.1)",}}>

        <h2 style={{ textAlign: "center", marginBottom: "20px" }}>Paramètres</h2>

        <div style={{ marginBottom: "20px" }}>
          <label>Ville</label>
          <br />
          <input type="text" value={city} onChange={(e) => setCity(e.target.value)} />
        </div>
  
        <div style={{ marginBottom: "20px" }}>
          <label >Point de départ</label>
          <br />
          <input type="text" value={startPoint} onChange={(e) => setStartPoint(e.target.value)} />
        </div>
  
        <div style={{ marginBottom: "20px" }}>
          <label>Point d'arrivée</label>
          <br />
          <input type="text" value={endPoint} onChange={(e) => setEndPoint(e.target.value)} />
        </div>

        <div style={{ marginBottom: "20px" }}>
          <label>🌧️ Niveau d'eau : {waterLevel}</label>
          <br />
          <input type="range" min="0" max="100" value={waterLevel} onChange={(e) => setWaterLevel(Number(e.target.value))} />
        </div>
  
        <button 
          style={{ width: "100%", padding: "10px", background: loading ? "gray" : "blue", color: "white", border: "none", cursor: loading ? "not-allowed" : "pointer" }}
          onClick={fetchEvacuationPath}
          disabled={loading}
        >
          {loading ? "Calcul en cours..." : "Envoyer au backend"}
        </button>
      </div>
    </div>
  );
}
