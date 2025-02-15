import { useState, useEffect } from 'react';
import MapView from './components/MapView.jsx';
import './App.css';

export default function App() {
  const [showMap, setShowMap] = useState(false);

  useEffect(() => {
    console.log("showMap state:", showMap);
  }, [showMap]);

  console.log("App component is rendered"); // Ajoutez cette ligne pour vérifier que le composant est bien rendu

  return (
    <div className="h-screen w-full flex flex-col items-center justify-center bg-gray-100">
      {!showMap ? (
        <div className="text-center">
          <h1 className="text-4xl font-bold mb-4">Application de Prévision des Inondations</h1>
          <p className="text-lg mb-6">Ce projet a été réalisé par le groupe <strong>Les 4 en Plastique</strong> pour prédire les inondations et aider à la prévention.</p>
          <button 
            onClick={() => setShowMap(true)}
            className="px-8 py-4 bg-blue-600 text-white rounded-lg shadow-md hover:bg-blue-700 transition text-lg"
          >
            Voir la carte
          </button>
        </div>
      ) : (
        <MapView />
      )}
    </div>
  );
}
