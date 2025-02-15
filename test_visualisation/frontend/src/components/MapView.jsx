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

// 🔹 Fix pour éviter un bug d'affichage des icônes Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
    shadowUrl: "https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png",
});

export default function MapView() {
  const [path, setPath] = useState([]);  // 🔹 Stocke la liste des points GPS

  // 🔹 Fetch pour récupérer les coordonnées du chemin d’évacuation
  useEffect(() => {
    fetch("http://localhost:8000/coordinates")
      .then((response) => response.json())
      .then((data) => {
        if (data.path && data.path.length > 1) {
          setPath(data.path.map(point => [point.lat, point.lng]));  // 🔹 Convertit les données pour Leaflet
        }
      })
      .catch((error) => console.error("Erreur lors de la récupération du chemin:", error));
  }, []);

  return (
    <div id="map" style={{ height: "90vh", width: "90vw", margin: "auto" }}>
      <MapContainer center={[48.8566, 2.3522]} zoom={13} style={{ height: "100%", width: "100%" }}>
        
        {/* 🔹 Fond de carte sobre */}
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
        />

        {/* 🔹 Affichage des marqueurs pour les points de départ et d'arrivée */}
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

        {/* 🔹 Affichage des points intermédiaires avec un style discret */}
        {path.length > 2 && path.slice(1, -1).map((position, index) => (
          <CircleMarker 
            key={index} 
            center={position} 
            radius={4}  // Taille réduite pour être discret
            fillColor="blue" 
            color="transparent"  // Contour transparent
            fillOpacity={0.6}  // Légèrement visible
          />
        ))}

        {/* 🔹 Affichage du chemin (une ligne bleue reliant tous les points) */}
        {path.length > 1 && <Polyline positions={path} color="blue" />}
      </MapContainer>
    </div>
  );
}
