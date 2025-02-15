document.addEventListener("DOMContentLoaded", async function () {
    // Charger la carte avec Leaflet.js
    var map = L.map('map').setView([0, 0], 2); // Vue par défaut (monde)

    // Ajouter une couche OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Récupérer les coordonnées depuis l'API
    try {
        let response = await fetch("http://127.0.0.1:8080/coordinates");
        let data = await response.json();

        // Afficher un marqueur sur la carte
        var marker = L.marker([data.lat, data.lng]).addTo(map)
            .bindPopup("Coordonnées récupérées du backend.")
            .openPopup();

        // Centrer la carte sur ces coordonnées
        map.setView([data.lat, data.lng], 10);
    } catch (error) {
        console.error("Erreur lors de la récupération des coordonnées :", error);
    }
});
