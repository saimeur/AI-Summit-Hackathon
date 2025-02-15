from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Ajouter CORS si besoin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/coordinates")
def get_coordinates():
    return {"lat": 48.8566, "lng": 2.3522}

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur l'API de prévision des inondations !"}
