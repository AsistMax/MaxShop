import os, uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import jwt

JWT_SECRET = os.getenv("JWT_SECRET", "maxshop-super-secret-2026")
COMISION = 0.017
CSB_ADHERIDO_CLIENTE = 0.10
CSB_NO_ADHERIDO_CLIENTE = 0.05
CSB_COMERCIO = 0.05

app = FastAPI(title="MaxShop V5")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

COMERCIOS_ADHERIDOS = {"felipe", "panaderia_pm", "lomitos_lo_mas", "comercio_123"}

class PagoRequest(BaseModel):
    user_id: str
    comercio_id: str
    monto_original: float
    card_token: str = "card_token_demo"
    qr_posnet_data: Optional[str] = None

class WebhookPago(BaseModel):
    status: str
    amount: float
    comercio_id: str
    user_id: str
    transaction_id: str

def validar_qr_posnet(qr_data: str):
    try:
        if qr_data and qr_data.startswith("MAXSHOP"):
            clean = qr_data.split(":")[-1].rsplit(".",1)[0] if "." in qr_data else ""
            if clean:
                decoded = jwt.decode(clean, JWT_SECRET, algorithms=["HS256"])
                return decoded
        return {"monto": None, "comercio_id": "detectado_por_gps"}
    except:
        return {"monto": None, "comercio_id": "detectado_por_gps"}

@app.get("/api")
def api_status():
    return {"msg": "MaxShop V5 TAP", "comision": "1.7% solo sobre servicio"}

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    return HTMLResponse("<h1>MaxShop V5 Activo</h1><a href='/docs'>Docs</a>", status_code=200)

@app.get("/comercios/cercanos")
def comercios_cercanos(lat: float, lng: float):
    return {
        "cercanos": [
            {"id": "felipe", "nombre": "Felipe", "adherido": True, "promo": "10% C$B", "distancia": "20m"},
            {"id": "panaderia_pm", "nombre": "Panadería PM", "adherido": True, "promo": "10% C$B", "distancia": "35m"},
            {"id": "lomitos_lo_mas", "nombre": "Lomitos lo-más", "adherido": True, "promo": "10% C$B", "distancia": "80m"},
        ],
        "tu_ubicacion": {"lat": lat, "lng": lng}
    }

@app.post("/pago/procesar")
def procesar_pago(req: PagoRequest):
    qr_info = validar_qr_posnet(req.qr_posnet_data or "")
    monto_detectado = qr_info.get("monto") or req.monto_original
    if monto_detectado <= 0:
        raise HTTPException(400, "Monto invalido")
    es_adherido = req.comercio_id in COMERCIOS_ADHERIDOS
    pago_principal_exitoso = True
    if not pago_principal_exitoso:
        raise HTTPException(402, "Pago rechazado por posnet")
    comision_1_7 = round(monto_detectado * COMISION, 2)
    if es_adherido:
        csb_cliente = round(monto_detectado * CSB_ADHERIDO_CLIENTE, 2)
        csb_comercio = round(monto_detectado * CSB_COMERCIO, 2)
        descuento_csb_usado = round(monto_detectado * 0.05, 2)
    else:
        csb_cliente = round(monto_detectado * CSB_NO_ADHERIDO_CLIENTE, 2)
        csb_comercio = 0
        descuento_csb_usado = 0
    transaccion = {
        "id": str(uuid.uuid4()),
        "user_id": req.user_id,
        "comercio_id": req.comercio_id,
        "es_adherido": es_adherido,
        "monto_detectado": monto_detectado,
        "monto_pagado_posnet": monto_detectado,
        "comision_1_7_cobrada": comision_1_7,
        "csb_descuento_usado": descuento_csb_usado,
        "csb_cliente_nuevo": csb_cliente,
        "csb_comercio": csb_comercio,
        "mensaje_exito": f"Compra exitosa, pagaste ${monto_detectado:,.0f}",
        "timestamp": datetime.utcnow().isoformat()
    }
    return {"status": "aprobado", "transaccion": transaccion}

@app.post("/webhook/pago-exitoso")
def webhook_pago_exitoso(data: WebhookPago):
    if data.status != "approved":
        raise HTTPException(400, "Pago no aprobado")
    es_adherido = data.comercio_id in COMERCIOS_ADHERIDOS
    comision = round(data.amount * COMISION, 2)
    return {
        "detectado": True,
        "monto": data.amount,
        "comercio_id": data.comercio_id,
        "es_adherido": es_adherido,
        "accion": f"Cobrar {comision} via tokenizada + acreditar C$B"
                }
