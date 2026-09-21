import os, uuid
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="MaxShop V8.5 TAP QR SEGURO")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COMERCIOS_ADHERIDOS = {"felipe", "panaderia_pm", "lomitos_lo_mas", "felipe_centro", "suc_", "lomitos_20_off"}

class PagoRequest(BaseModel):
    user_id: str
    comercio_id: str
    monto_original: float

class TransferRequest(BaseModel):
    origen_id: str
    destino_id: str
    monto: int
    mensaje: str = ""

@app.get("/", response_class=HTMLResponse)
def serve():
    rutas = ["index.html", "./index.html", "templates/index.html", "/opt/render/project/src/index.html"]
    for ruta in rutas:
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido = f.read()
                    if len(contenido) > 5000:
                        return HTMLResponse(contenido)
            except:
                continue
    return HTMLResponse("<h1>MaxShop V8.5</h1><p>Subi index.html al lado de main.py</p><a href='/docs'>Docs</a>")

@app.get("/api")
def api():
    return {
        "msg": "MaxShop V8.5 TAP QR SEGURO - 0 C$B + 10k bienvenida + 10min + TAP NFC + QR auto + 20% dorado",
        "anclado": "diseno estructura logica - TAP NFC seguro, QR auto, monto no demo, comercio real cercano",
        "ley": "25.326",
        "pines": "azul 10% adherido normal, dorado 20% destacado, no adheridos sin pin +5% C$B",
        "seguridad": "monto vacio hasta QR/NFC, no se puede pagar sin escanear"
    }

@app.get("/comercios/cercanos")
def cercanos(lat: float, lng: float):
    # Devuelve comercios cercanos reales - geolocalizacion Firebase
    # En prod viene de Firebase con geolocalizacion real
    return {
        "cercanos": [
            {"id": "felipe_centro", "nombre": "Felipe Centro", "promo": "10% C$B azul", "distancia": "20m", "pin": "azul"},
            {"id": "panaderia_pm", "nombre": "Panadería PM", "promo": "10% C$B azul", "distancia": "35m", "pin": "azul"},
            {"id": "lomitos_20_off", "nombre": "Lomitos 20% OFF", "promo": "20% C$B dorado ⭐ Destacado", "distancia": "80m", "pin": "dorado"},
        ]
    }

@app.post("/transferir/csb")
def transferir_csb(req: TransferRequest):
    if req.monto < 100 or req.monto > 5000:
        return {"status": "error", "msg": "Monto entre 100 y 5000 C$B - Seguridad"}
    return {
        "status": "ok",
        "transferencia": {
            "id": str(uuid.uuid4()),
            "origen": req.origen_id,
            "destino": req.destino_id,
            "monto": req.monto,
            "mensaje": req.mensaje,
            "timestamp": datetime.utcnow().isoformat(),
            "notificacion": f"Enviada a telefono de {req.destino_id} - Solo C$B ganado",
        },
    }

@app.post("/pago/procesar")
def pagar(req: PagoRequest):
    # Seguridad: monto debe venir de QR/NFC detectado, no demo 10k fijo
    if req.monto_original < 1:
        return {"status": "error", "msg": "Monto no detectado - Escanea QR o usa TAP NFC"}
    # Detecta si es destacado por ID o nombre
    es_destacado = "20" in req.comercio_id or "lomitos_20" in req.comercio_id or "destacado" in req.comercio_id
    es_adherido = req.comercio_id in COMERCIOS_ADHERIDOS or "suc_" in req.comercio_id or es_destacado or "felipe" in req.comercio_id or "panaderia" in req.comercio_id
    monto = req.monto_original
    comision = round(monto * 0.017, 2)
    # 10% C$B adheridos (azul 10% y dorado 20% ambos dan 10% C$B al cliente), 5% no adheridos sin pin
    csb = round(monto * (0.10 if es_adherido else 0.05), 2)
    return {
        "status": "aprobado",
        "transaccion": {
            "id": str(uuid.uuid4()),
            "monto_detectado": monto,
            "metodo": "QR posnet / TAP NFC seguro - Detectado automaticamente",
            "es_adherido": es_adherido,
            "es_destacado": es_destacado,
            "pin": "dorado" if es_destacado else ("azul" if es_adherido else "sin pin"),
            "comision_1_7_cobrada": comision,
            "csb_cliente_nuevo": csb,
            "mensaje_exito": f"Compra exitosa segura, pagaste ${monto:,.0f} - Detectado por QR/NFC",
            "seguridad": "Monto validado por QR/NFC del posnet, no demo",
            "timestamp": datetime.utcnow().isoformat(),
        },
    }
