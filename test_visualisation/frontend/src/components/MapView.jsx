import { MapContainer, TileLayer, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { useEffect } from 'react';

// Fix pour les icônes de leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});

function MapLogger() {
  const map = useMap();
  useEffect(() => {
    console.log("Map center:", map.getCenter());
    console.log("Map zoom:", map.getZoom());
    console.log("Map size:", map.getSize());
  }, [map]);
  return null;
}

export default function MapView() {
  console.log("MapView component is rendered"); // Ajoutez cette ligne pour vérifier que le composant est bien rendu

  return (
    <div id="map" style={{ height: "90vh", width: "90vw", margin: "auto" }}>
      <MapContainer center={[48.8566, 2.3522]} zoom={13} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          subdomains='abcd'
          maxZoom={20}
          onLoad={() => console.log("TileLayer loaded")}
          onError={(error) => console.error("TileLayer error:", error)}
        />
        <MapLogger />
      </MapContainer>
    </div>
  );
}
