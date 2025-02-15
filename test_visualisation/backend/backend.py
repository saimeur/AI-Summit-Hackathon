from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Activer CORS pour permettre la connexion avec le frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
