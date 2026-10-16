from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
import uuid

load_dotenv()

try:
    from supabase import create_client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
except:
    supabase = None

# Tracking opcional - no rompe si no está
try:
    from tracking.router import router as tracking_router
    HAS_TRACKING = True
except Exception as e:
    print(f"Tracking no cargado aun: {e}")
    HAS_TRACKING = False
    tracking_router = None

app = FastAPI(title="NODO Argentina API - V3.6 FINAL APP + MAPA + TRACKING")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates opcional
try:
    templates = Jinja2Templates(directory="templates")
    HAS_TEMPLATES = True
except:
    templates = None
    HAS_TEMPLATES = False

# Static opcional - no rompe si no existe
if os.path.exists("static"):
    try:
        app.mount("/static", StaticFiles(directory="static"), name="static")
    except:
        pass

@app.get("/health")
def health():
    return {"status": "OK", "nodo": "V3.6 Final APP + MAPA", "tracking": HAS_TRACKING, "supabase": supabase is not None, "templates": HAS_TEMPLATES}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    # 1. Intenta templates/index.html
    if HAS_TEMPLATES and templates:
        try:
            return templates.TemplateResponse("index.html", {"request": request})
        except:
            pass
    
    # 2. Intenta app.html sellado gigante (tu app anclada)
    if os.path.exists("app.html"):
        with open("app.html", "r", encoding="utf-8") as f:
            return f.read()
    
    # 3. Fallback JSON
    return JSONResponse({
        "nodo-api": "Live V3.6 FINAL APP + MAPA + QR UNICO + BOTS",
        "base_url": "https://maxshop-api.onrender.com",
        "version_diseno": "642d635032ce",
        "status": "OK",
        "rutas": {
            "app_sellada": "/app",
            "health": "/health",
            "mapa": "/mapa-calles-real",
            "tracking_ruta": "/tracking/ruta/{envio_id}" if HAS_TRACKING else "no cargado",
            "qr_generar": "/qr/generar"
        }
    })

@app.get("/app", response_class=HTMLResponse)
def app_sellada(request: Request):
    # Tu APP ANCLADA SELLADA con candado
    if os.path.exists("app.html"):
        with open("app.html", "r", encoding="utf-8") as f:
            return f.read()
    if HAS_TEMPLATES and templates:
        try:
            return templates.TemplateResponse("index.html", {"request": request})
        except:
            pass
    return HTMLResponse("<h1>app.html no encontrado</h1><p>Subí tu index.html sellado como app.html</p>", status_code=404)

@app.get("/mapa-calles-real", response_class=HTMLResponse)
def mapa_calles_real(request: Request):
    if HAS_TEMPLATES and templates:
        try:
            return templates.TemplateResponse("mapa-calles-real.html", {"request": request})
        except Exception as e:
            return HTMLResponse(f"<h1>Error mapa: {e}</h1><p>¿Subiste templates/mapa-calles-real.html?</p>", status_code=500)
    return HTMLResponse("<h1>Template mapa-calles-real.html no encontrado</h1><p>Creá carpeta templates/ con el archivo</p>", status_code=404)

# Tracking solo si existe
if HAS_TRACKING and tracking_router:
    app.include_router(tracking_router)
    print("✅ Tracking conectado en /tracking")

@app.get("/qr/generar")
def generar_qr():
    qr_id = str(uuid.uuid4())[:8].upper()
    return {"qr_id": qr_id, "url": f"https://maxshop-api.onrender.com/tracking/ruta/{qr_id}", "status": "generado"}

@app.get("/api/status")
def api_status():
    return {"api": "NODO Argentina", "version": "V3.6 Final", "health": "OK", "tracking": HAS_TRACKING, "app_sellada": os.path.exists("app.html")}
