from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import json

from model_service import service
import database

BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"

app = FastAPI(
    title="PlantGuard AI - Crop Disease Detection & Diagnosis",
    description="Deep Learning API for crop disease classification with Grad-CAM explainability.",
    version="1.0.0"
)

# Enable CORS for local testing or external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Disable caching so frontend changes are always live immediately
@app.middleware("http")
async def add_no_cache_header(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Ensure database table exists
database.init_db()

@app.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "model_loaded": service.model is not None,
        "classes_count": len(service.class_names),
        "knowledge_entries": len(service.knowledge),
        "database_connected": True
    }

@app.post("/api/predict")
async def predict_disease(
    file: UploadFile = File(...),
    notes: str = Query("", description="Optional notes from farmer/user"),
    crop_filter: str = Query("auto", description="Target crop filter (e.g. Apple, Tomato, auto)")
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a valid image (JPEG/PNG/WebP).")

    try:
        image_bytes = await file.read()
        analysis = service.analyze_leaf(
            image_bytes, 
            filename=file.filename,
            crop_filter=crop_filter
        )
        
        # Save scan to SQLite history
        scan_id = database.save_scan(
            filename=file.filename,
            predicted_class=analysis["predicted_class"],
            crop=analysis["crop"],
            disease=analysis["disease"],
            confidence=analysis["confidence"],
            severity=analysis["severity"],
            top_predictions=analysis["top_predictions"],
            notes=notes
        )
        analysis["scan_id"] = scan_id
        
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")

@app.get("/api/history")
async def get_history(limit: int = 30):
    scans = database.get_recent_scans(limit=limit)
    return {"scans": scans}

@app.delete("/api/history")
async def clear_history():
    database.clear_all_history()
    return {"message": "Scan history cleared successfully"}

@app.get("/api/stats")
async def get_analytics():
    return database.get_scan_stats()

@app.get("/api/diseases")
async def get_all_diseases():
    return {"total": len(service.knowledge), "diseases": service.knowledge}

# Mount static web directory
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(str(STATIC_DIR / "index.html"))
