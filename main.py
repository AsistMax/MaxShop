from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

# ================= Tracking =================
try:
    from tracking.router import router as tracking_router
    HAS_TRACKING = True
except Exception as e:
    print(f"Tracking no cargado: {e}")
    HAS_TRACKING = False

app = FastAPI(title="NODO Argentina V3.6 FINAL CONCRETO", version="3.6.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# ================= Helper Supabase =================
def get_supabase_status():
    url = os.getenv("SUPABASE_URL")
    # Soporta ambos nombres: viejo SERVICE_ROLE y nuevo SECRET_KEY
    key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY") 
        or os.getenv("SUPABASE_SECRET_KEY") 
        or os.getenv("SUPABASE_SERVICE_KEY")
    )
    return bool(url and key), url, key

# ================= FIX RENDER - HEALTH =================
@app.get("/health")
def health():
    supabase_ok, _, _ = get_supabase_status()
    return {
        "status": "OK",
        "nodo": "Live V3.6 FINAL CONCRETO 100% REAL",
        "version_diseno": "642d635032ce",
        "tracking": HAS_TRACKING,
        "supabase": supabase_ok,
        "supabase_url": os.getenv("SUPABASE_URL"),
        "templates": True,
        "mp": bool(os.getenv("MP_ACCESS_TOKEN")),
        "nota": "Si supabase=false, pega SUPABASE_SECRET_KEY en Render como SERVICE_ROLE_KEY"
    }

@app.get("/")
def root():
    supabase_ok, _, _ = get_supabase_status()
    return {
        "nodo-api": "Live V3.6 FINAL CONCRETO",
        "base_url_acordada": "https://maxshop-api.onrender.com",
        "version_diseno": "642d635032ce",
        "status": "OK",
        "tracking": HAS_TRACKING,
        "supabase": supabase_ok,
        "rutas": {
            "app_sellada": "/app",
            "health": "/health",
            "mapa_real": "/mapa-calles-real?envio=TEST123",
            "cadete": "/cadete",
            "tracking_ping": "/tracking/ping",
            "tracking_estado": "/tracking/estado",
            "tracking_ruta": "/tracking/ruta/{envio_id}",
            "pago_split": "/pago/crear",
            "chat": "/chat/{trabajo_id}"
        }
    }

# ================= APP SELLADA ANCLADA =================
@app.get("/app", response_class=HTMLResponse)
async def app_sellada(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/mapa-calles-real", response_class=HTMLResponse)
async def mapa_calles_real(request: Request):
    # CORREGIDO: Request no dict
    return templates.TemplateResponse("mapa-calles-real.html", {"request": request})

@app.get("/cadete", response_class=HTMLResponse)
async def cadete_view(request: Request):
    return templates.TemplateResponse("cadete.html", {"request": request})

# ================= TRACKING + PAGOS + CHAT =================
if HAS_TRACKING:
    app.include_router(tracking_router)
