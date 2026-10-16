from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
import os
from dotenv import load_dotenv

load_dotenv()

try:
    from supabase import create_client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
except:
    supabase = None

try:
    from tracking.router import router as tracking_router
    HAS_TRACKING = True
except Exception as e:
    print(f"Tracking no cargado aun: {e}")
    HAS_TRACKING = False

app = FastAPI(title="NODO Argentina API - V3.5 Final QR UNICO + BOTS + TRACKING REAL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "OK", "nodo": "V3.5 Final", "tracking": HAS_TRACKING, "supabase": supabase is not None}

try:
    templates = Jinja2Templates(directory="templates")
except:
    templates = None

try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except:
    pass

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    if templates:
        try:
            return templates.TemplateResponse("index.html", {"request": request})
        except Exception as e:
            print(f"Error index: {e}")
    return JSONResponse({
        "nodo-api": "Live V3.5 Final QR UNICO + BOTS",
        "base_url_acordada": "https://maxshop-api.onrender.com",
        "version_diseno": "642d635032ce",
        "status": "OK",
        "endpoints": {
            "health": "/health",
            "mapa": "/mapa-calles-real",
            "tracking_ruta": "/tracking/ruta/{envio_id}",
            "tracking_ping": "/tracking/ping"
        }
    })

@app.get("/mapa-calles-real", response_class=HTMLResponse)
def mapa_calles_real(request: Request):
    if templates:
        try:
            return templates.TemplateResponse("mapa-calles-real.html", {"request": request})
        except Exception as e:
            return HTMLResponse(f"<h1>Error mapa: {e}</h1>", status_code=500)
    return HTMLResponse("<h1>Template mapa-calles-real.html no encontrado</h1>", status_code=404)

if HAS_TRACKING:
    app.include_router(tracking_router)
    print("✅ Tracking conectado en /tracking")

import uuid
@app.get("/qr/generar")
def generar_qr():
    qr_id = str(uuid.uuid4())[:8].upper()
    return {"qr_id": qr_id, "url": f"https://maxshop-api.onrender.com/tracking/ruta/{qr_id}", "status": "generado"}

@app.get("/api/status")
def api_status():
    return {"api": "NODO Argentina", "version": "V3.5 Final", "health": "OK", "tracking": HAS_TRACKING}
