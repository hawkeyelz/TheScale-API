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

@app.post("/process-now")
def trigger_manual_scale(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(run_crawler_task, db)
    return {"message": "Scaling process started in background."}

def run_crawler_task(db: Session):
    config = load_hnn_engine()
    inference = HNNInferenceEngine(config)
    
    # This list will eventually come from a 'sources' table in the DB
    watch_list = [
        "https://democracyforward.org/news/press-releases/federal-court-blocks-significant-pieces-of-administrations-sweeping-immigration-appeals-rule-that-eliminates-meaningful-judicial-review/",
        "https://nationaltoday.com/us/ny/new-york/news/2026/02/22/apple-news-accused-of-excluding-conservative-outlets/"
    ]
    
    for url in watch_list:
        if crud.get_broadcast_by_url(db, url):
            continue
            
        broadcast_text = inference.generate_broadcast(url)
        if broadcast_text:
            crud.create_broadcast(db, url=url, content=broadcast_text)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)