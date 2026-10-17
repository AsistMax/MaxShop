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

app = FastAPI(title="NODO Argentina V3.6 FINAL CONCRETO", version="3.6.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
templates = Jinja2Templates(directory="templates")

@app.get("/health")
def health():
    return {
        "status":"OK",
        "nodo":"Live V3.6 FINAL CONCRETO 100% REAL",
        "version_diseno":"642d635032ce",
        "tracking":HAS_TRACKING,
        "supabase":bool(os.getenv("SUPABASE_URL")),
        "mp":bool(os.getenv("MP_ACCESS_TOKEN")),
        "templates":True
    }

@app.get("/")
def root():
    return {"nodo-api":"Live V3.6 FINAL","base":"https://maxshop-api.onrender.com","version":"642d635032ce","status":"OK","tracking":HAS_TRACKING}

@app.get("/app", response_class=HTMLResponse)
async def app_sellada(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/mapa-calles-real", response_class=HTMLResponse)
async def mapa_calles_real(request: Request):
    return templates.TemplateResponse("mapa-calles-real.html", {"request": request})

@app.get("/cadete", response_class=HTMLResponse)
async def cadete_view(request: Request):
    return templates.TemplateResponse("cadete.html", {"request": request})

if HAS_TRACKING:
    app.include_router(tracking_router)
