import os
from fastapi import FastAPI, Query, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import qrcode, io, base64
from datetime import datetime

app = FastAPI(title="NODO Argentina - Mundo Conectado")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
templates = Jinja2Templates(directory="templates")
ADM_KEYS = ["AsistMax2026", "AsistMax2026!"]

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
def health():
    return {"status":"ok","service":"nodo-api","region":"dynamic","time": datetime.now().isoformat()}

@app.get("/")
def home():
    return FileResponse("templates/index.html")

@app.get("/api/tareas")
def tareas(region: str = Query("Buenos Aires"), lat: float = Query(-34.6118), lng: float = Query(-58.3960)):
    # Detección dinámica por coordenadas
    detected = region
    if -35.2 < lat < -34.3 and -58.7 < lng < -58.2:
        detected = "Buenos Aires"
    elif -29.0 < lat < -27.0 and -66.5 < lng < -65.0:
        detected = "Catamarca"
    elif -32.0 < lat < -30.0 and -65.0 < lng < -63.0:
        detected = "Córdoba"
    
    if detected == "Catamarca":
        data = [
            {"id":"1","title":"Sacar foto local - Verificar comercio","tag":"FOTO","loc":"Catamarca • Capital - FOTO","lat":-28.46957,"lng":-65.78524,"price":"$1.500"},
            {"id":"2","title":"Llevar paquete cliente","tag":"ENVIO","loc":"Catamarca • La Chacarita","lat":-28.471,"lng":-65.79,"price":"$2.000"},
        ]
    else:
        data = [
            {"id":"3","title":"Electricista matriculado - Urgencia","tag":"OFICIO","loc":f"{detected} • CABA","lat":lat,"lng":lng,"price":"A convenir"},
            {"id":"4","title":"Sacar foto local Palermo","tag":"FOTO","loc":"CABA • Palermo","lat":lat,"lng":lng,"price":"$1.500"},
            {"id":"5","title":"Peluquera a domicilio","tag":"OFICIO","loc":f"{detected}","lat":lat,"lng":lng,"price":"$2.500"},
        ]
    return {"tareas": data, "region_detectada": detected, "lat": lat, "lng": lng}

@app.get("/api/comercios")
def comercios():
    return [{"id":"fc","nombre":"Farmacia Central Norte","rubro":"Farmacia","dir":"Av. Belgrano 1245, CABA","badge":"-20% OFF +10% C$B"}]

@app.post("/api/adm/login")
async def adm_login(request: Request):
    body = await request.json()
    key = body.get("key","").strip()
    clean = key.lower().replace("!","")
    if clean in [k.lower().replace("!","") for k in ADM_KEYS] or key in ADM_KEYS:
        return {"ok":True,"rol":"admin","msg":"Acceso NODO ADM"}
    return JSONResponse({"ok":False,"error":"Clave inválida"}, status_code=401)
