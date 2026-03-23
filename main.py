from fastapi import FastAPI
import threading
from database import init_db, save_broadcast, SessionLocal, Broadcast
from engine import HNNInferenceEngine, load_hnn_engine

app = FastAPI()
config = load_hnn_engine()
inference = HNNInferenceEngine(config)

@app.on_event("startup")
def startup_event():
    init_db()
    # Start the scraper in the background
    threading.Thread(target=background_scraper, daemon=True).start()

def background_scraper():
    # Loop through watchlist, call inference.generate_broadcast(), 
    # then call save_broadcast()
    pass

@app.get("/api/v1/broadcasts")
def read_broadcasts():
    db = SessionLocal()
    return db.query(Broadcast).all()