import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="MaxShop V7")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

COMERCIOS_ADHERIDOS = {"felipe", "panaderia_pm", "lomitos_lo_mas"}

class PagoRequest(BaseModel):
    user_id: str
    comercio_id: str
    monto_original: float

@app.get("/", response_class=HTMLResponse)
def serve():
    try:
        with open(os.path.join(os.path.dirname(__file__), "index.html"), "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except:
        return HTMLResponse("<h1>MaxShop V7</h1><a href='/docs'>Docs</a>")

@app.get("/comercios/cercanos")
def cercanos(lat: float, lng: float):
    return {"cercanos": [
        {"id": "felipe", "nombre": "Felipe", "adherido": True, "promo": "10% C$B", "distancia": "20m"},
        {"id": "panaderia_pm", "nombre": "Panadería PM", "adherido": True, "promo": "10% C$B", "distancia": "35m"},
        {"id": "lomitos_lo_mas", "nombre": "Lomitos lo-más", "adherido": True, "promo": "10% C$B", "distancia": "80m"},
    ]}

@app.post("/pago/procesar")
def pagar(req: PagoRequest):
    import uuid, datetime
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
        "timestamp": datetime.datetime.utcnow().isoformat()
    }}
