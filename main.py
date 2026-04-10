import uvicorn
from fastapi import FastAPI, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from database import models, crud
from database.models import SessionLocal, engine
from core.engine import HNNInferenceEngine, load_hnn_engine

# Initialize Database Tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="The Scale API v2.7.2")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/broadcasts")
def read_broadcasts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_broadcasts(db, skip=skip, limit=limit)

# --- NEW SOURCES ENDPOINTS ---
@app.get("/sources")
def list_sources(db: Session = Depends(get_db)):
    return crud.get_sources(db)

@app.post("/sources")
def add_source(name: str, url: str, db: Session = Depends(get_db)):
    return crud.create_source(db, name=name, url=url)
# -----------------------------

@app.post("/process-now")
def trigger_manual_scale(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Check if we have sources before starting
    sources = crud.get_sources(db)
    if not sources:
        return {"message": "No sources found in database. Please add a source first."}
    
    background_tasks.add_task(run_crawler_task, db)
    return {"message": f"Scaling process started for {len(sources)} sources."}

def run_crawler_task(db: Session):
    config = load_hnn_engine()
    inference = HNNInferenceEngine(config)
    
    # Now pulling dynamically from your database!
    sources = crud.get_sources(db)
    
    for source in sources:
        url = source.url
        if crud.get_broadcast_by_url(db, url):
            continue
            
        broadcast_text = inference.generate_broadcast(url)
        if broadcast_text:
            crud.create_broadcast(db, url=url, content=broadcast_text)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)