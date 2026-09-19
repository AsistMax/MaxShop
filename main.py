import os, uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(title="MaxShop V7.4")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

COMERCIOS_ADHERIDOS = {"felipe", "panaderia_pm", "lomitos_lo_mas"}

class PagoRequest(BaseModel):
    user_id: str
    comercio_id: str
    monto_original: float

@app.get("/api")
def api():
    return {"msg": "MaxShop V7.4 FINAL", "comision": "1.7%", "csb": "10% / 5%", "ley": "25.326"}

@app.get("/", response_class=HTMLResponse)
def root():
    path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>MaxShop V7.4</h1><p>Subi index.html, logo.png y banner.jpg al repo</p>")

@app.get("/logo.png")
def logo():
    path = os.path.join(os.path.dirname(__file__), "logo.png")
    if os.path.exists(path):
        return FileResponse(path)
    raise HTTPException(404)

@app.get("/banner.jpg")
def banner():
    path = os.path.join(os.path.dirname(__file__), "banner.jpg")
    if os.path.exists(path):
        return FileResponse(path)
    raise HTTPException(404)

@app.get("/comercios/cercanos")
def cercanos(lat: float, lng: float):
    return {"cercanos": [
        {"id": "felipe", "nombre": "Felipe", "promo": "10% C$B", "distancia": "20m"},
        {"id": "panaderia_pm", "nombre": "Panadería PM", "promo": "10% C$B", "distancia": "35m"},
        {"id": "lomitos_lo_mas", "nombre": "Lomitos lo-más", "promo": "10% C$B", "distancia": "80m"},
    ]}

@app.post("/pago/procesar")
def pagar(req: PagoRequest):
    es_adherido = req.comercio_id in COMERCIOS_ADHERIDOS
    monto = req.monto_original
    comision = round(monto * 0.017, 2)
    csb = round(monto * (0.10 if es_adherido else 0.05), 2)
    return {"status": "aprobado", "transaccion": {
        "id": str(uuid.uuid4()),
        "monto_detectado": monto,
        "es_adherido": es_adherido,
        "comision_1_7_cobrada": comision,
        "csb_cliente_nuevo": csb,
        "mensaje_exito": f"Compra exitosa, pagaste ${monto:,.0f}",
        "timestamp": datetime.utcnow().isoformat()
    }}
