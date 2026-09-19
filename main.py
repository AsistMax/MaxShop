import os, uuid
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="MaxShop V7.8 ANCLADO")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COMERCIOS_ADHERIDOS = {"felipe", "panaderia_pm", "lomitos_lo_mas"}

class PagoRequest(BaseModel):
    user_id: str
    comercio_id: str
    monto_original: float

@app.get("/", response_class=HTMLResponse)
def serve():
    # Busca index.html en la raiz (donde esta main.py)
    rutas = [
        "index.html",
        "./index.html",
        "templates/index.html",
        "/opt/render/project/src/index.html",
    ]
    for ruta in rutas:
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    contenido = f.read()
                    if len(contenido) > 5000:
                        return HTMLResponse(contenido)
            except:
                continue
    return HTMLResponse(
        "<h1>MaxShop V7.8</h1><p>Subi index.html al lado de main.py en la raiz del repo.</p><a href='/docs'>Docs</a>"
    )

@app.get("/api")
def api():
    return {
        "msg": "MaxShop V7.8 ANCLADO - 0 C$B + 10k bienvenida + 10min timeout",
        "anclado": "diseno estructura logica",
        "ley": "25.326",
    }

@app.get("/comercios/cercanos")
def cercanos(lat: float, lng: float):
    return {
        "cercanos": [
            {"id": "felipe", "nombre": "Felipe", "promo": "10% C$B", "distancia": "20m"},
            {"id": "panaderia_pm", "nombre": "Panaderia PM", "promo": "10% C$B", "distancia": "35m"},
            {"id": "lomitos_lo_mas", "nombre": "Lomitos lo-mas", "promo": "10% C$B", "distancia": "80m"},
        ]
    }

@app.post("/pago/procesar")
def pagar(req: PagoRequest):
    es_adherido = req.comercio_id in COMERCIOS_ADHERIDOS
    monto = req.monto_original
    comision = round(monto * 0.017, 2)
    csb = round(monto * (0.10 if es_adherido else 0.05), 2)
    return {
        "status": "aprobado",
        "transaccion": {
            "id": str(uuid.uuid4()),
            "monto_detectado": monto,
            "es_adherido": es_adherido,
            "comision_1_7_cobrada": comision,
            "csb_cliente_nuevo": csb,
            "mensaje_exito": f"Compra exitosa, pagaste ${monto:,.0f}",
            "timestamp": datetime.utcnow().isoformat(),
        },
    }
