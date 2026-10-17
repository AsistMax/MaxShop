from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

try:
    from tracking.router import router as tracking_router
    HAS_TRACKING = True
except:
    HAS_TRACKING = False

app = FastAPI(title="NODO V3.6 FINAL CONCRETO", version="3.6.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
templates = Jinja2Templates(directory="templates")

def get_supabase_status():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SECRET_KEY")
    return bool(url and key)

@app.get("/health")
def health():
    return {"status":"OK","nodo":"Live V3.6 FINAL","version":"642d635032ce","tracking":HAS_TRACKING,"supabase":get_supabase_status(),"mp":bool(os.getenv("MP_ACCESS_TOKEN"))}

@app.get("/")
def root():
    return {"status":"OK","url":"https://maxshop-api.onrender.com"}

@app.get("/app", response_class=HTMLResponse)
async def app_view(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/mapa-calles-real", response_class=HTMLResponse)
async def mapa_calles_real(request: Request):
    return templates.TemplateResponse("mapa-calles-real.html", {"request": request})

@app.get("/cadete", response_class=HTMLResponse)
async def cadete_view(request: Request):
    return templates.TemplateResponse("cadete.html", {"request": request})

@app.get("/qr/{qr_id}", response_class=HTMLResponse)
async def qr_redirect(request: Request, qr_id: str):
    return templates.TemplateResponse("index.html", {"request": request})

if HAS_TRACKING:
    app.include_router(tracking_router)
