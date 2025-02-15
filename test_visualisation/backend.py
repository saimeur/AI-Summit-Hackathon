from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Autoriser les requêtes depuis n'importe quelle origine (utile pour le développement)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/coordinates")
def get_coordinates():
    # Coordonnées en dur (ex: Paris, France)
    return {"lat": 48.8566, "lng": 2.3522}


# Lancer le serveur avec : uvicorn backend:app --reload
