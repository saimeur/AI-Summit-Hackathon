import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, CircleMarker } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// 🔹 Icône pour les points de départ et d'arrivée
const evacuationIcon = new L.Icon({
  iconUrl: 'https://upload.wikimedia.org/wikipedia/commons/e/ec/RedDot.svg', // Point rouge
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

export default function MapView() {
  const [path, setPath] = useState([]);

  useEffect(() => {
    fetch("http://localhost:8000/coordinates")
      .then((response) => response.json())
      .then((data) => {
        if (data.path && data.path.length > 1) {
          setPath(data.path.map(point => [point.lat, point.lng]));
        }
      })
      .catch((error) => console.error("Erreur lors de la récupération du chemin:", error));
  }, []);

  return (
    <div style={{ 
      display: "grid", 
      gridTemplateColumns: "75% 25%",  
      height: "90vh", 
      width: "90vw",
      overflow: "hidden"
    }}>
    
      
      {/* 📌 Zone de la carte */}
      <div style={{ border: "3px solid black" }}>
        <MapContainer 
          center={[48.8566, 2.3522]} 
          zoom={13} 
          style={{ width: "100%", height: "100%" }}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          />
  
          {path.length > 1 && (
            <>
              <Marker position={path[0]} icon={evacuationIcon}>
                <Popup>🚨 Départ</Popup>
              </Marker>
              <Marker position={path[path.length - 1]} icon={evacuationIcon}>
                <Popup>✅ Arrivée</Popup>
              </Marker>
            </>
          )}
  
          {path.length > 2 && path.slice(1, -1).map((position, index) => (
            <CircleMarker 
              key={index} 
              center={position} 
              radius={4}  
              fillColor="blue" 
              color="transparent"
              fillOpacity={0.6}
            />
          ))}
  
          {path.length > 1 && <Polyline positions={path} color="blue" />}
        </MapContainer>
      </div>
  
      {/* 📌 Colonne des paramètres */}
      <div style={{ background: "#242424", padding: "20px", display: "flex", flexDirection: "column", justifyContent: "space-between",borderLeft: "10px solid #242424", boxShadow: "-2px 0 5px rgba(0, 0, 0, 0.1)",}}>

        <h2 style={{ textAlign: "center", marginBottom: "20px" }}>Paramètres</h2>
  
        {/* Sélection des points */}
        <div style={{ marginBottom: "20px" }}>
          <label>🏁 Point de départ</label>
          <input type="text" style={{ width: "100%", padding: "8px", border: "1px solid gray" }} placeholder="Latitude, Longitude" />
        </div>
  
        <div style={{ marginBottom: "20px" }}>
          <label>🚩 Point d'arrivée</label>
          <input type="text" style={{ width: "100%", padding: "8px", border: "1px solid gray" }} placeholder="Latitude, Longitude" />
        </div>
  
        {/* Sliders météo */}
        <div style={{ marginBottom: "20px" }}>
          <label>🌧️ Pluviométrie</label>
          <input type="range" min="0" max="100" style={{ width: "100%" }} />
        </div>
  
        <div style={{ marginBottom: "20px" }}>
          <label>🌡️ Température</label>
          <input type="range" min="-10" max="40" style={{ width: "100%" }} />
        </div>
  
        {/* Bouton Envoyer */}
        <button style={{ width: "100%", padding: "10px", background: "blue", color: "white", border: "none", cursor: "pointer" }}>
          Envoyer au backend
        </button>
      </div>
    </div>
  );
}  