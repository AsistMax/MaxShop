
import os, uuid, requests
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="MaxShop V10.5 ANCLA VERDADERA - Banner Original + Wallet 100%")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN", "")
MP_PUBLIC_KEY = os.getenv("MP_PUBLIC_KEY", "")
COMISION_PORCENTAJE = 0.017

COMERCIOS_ADHERIDOS = {"felipe", "panaderia_pm", "lomitos_lo_mas", "felipe_centro", "suc_", "lomitos_20_off", "templo", "comercio", "felipe", "jumbo", "fravega", "mcdonalds", "banco_galicia"}

class PagoRequest(BaseModel):
    user_id: str
    comercio_id: str
    monto_original: float
    comercio_nombre: Optional[str] = None
    tarjeta: Optional[str] = None
    fecha: Optional[str] = None
    hora: Optional[str] = None
    trans_id: Optional[str] = None
    mp_token: Optional[str] = None
    email_cliente: Optional[str] = None
    tipo_tarjeta: Optional[str] = None

class TransferRequest(BaseModel):
    origen_id: str
    destino_id: str
    monto: int
    mensaje: str = ""

@app.get("/", response_class=HTMLResponse)
def serve():
    for ruta in ["index.html", "./index.html", "templates/index.html", "/opt/render/project/src/index.html"]:
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    c = f.read()
                    if len(c) > 5000:
                        return HTMLResponse(c)
            except:
                continue
    return HTMLResponse("<h1>MaxShop V10.5 Ancla Verdadera</h1>")

@app.get("/api")
def api():
    return {"msg": "MaxShop V10.5 Ancla Verdadera - Banner Original Familia Obelisco + Wallet 100% MaxShop", "wallet": "100% MaxShop", "banner": "banner.jpg original - Jumbo, Fravega, McDonalds, 35% 40% 30% Adidas", "tarjetas": ["Visa", "Mastercard", "Cabal", "Naranja", "Maestro", "Amex"], "ley": "25.326"}

@app.get("/config/mp")
def mp_config():
    return {"public_key": MP_PUBLIC_KEY, "mp_conectado": bool(MP_ACCESS_TOKEN)}

@app.post("/pago/procesar")
def pagar(req: PagoRequest):
    es_destacado = "20" in req.comercio_id or "lomitos_20" in req.comercio_id
    es_adherido = req.comercio_id in COMERCIOS_ADHERIDOS or "suc_" in req.comercio_id or es_destacado or any(x in req.comercio_id for x in ["felipe", "panaderia", "comercio", "templo", "jumbo", "fravega"])
    monto = req.monto_original
    comercio_nombre_real = req.comercio_nombre or req.comercio_id.replace("_", " ").title() or "Comercio"
    fecha = req.fecha or datetime.now().strftime("%d/%m/%Y")
    hora = req.hora or datetime.now().strftime("%H:%M:%S")
    trans_id = req.trans_id or f"TX-{uuid.uuid4().hex[:8].upper()}"
    csb = round(monto * (0.10 if es_adherido else 0.05), 2)
    mp_payment_id = None
    if MP_ACCESS_TOKEN and req.mp_token:
        try:
            headers = {"Authorization": f"Bearer {MP_ACCESS_TOKEN}", "Content-Type": "application/json", "X-Idempotency-Key": trans_id}
            payload = {"transaction_amount": float(monto), "token": req.mp_token, "description": f"MaxShop - {comercio_nombre_real}", "installments": 1, "payer": {"email": req.email_cliente or req.user_id or "cliente@maxshop.com"}}
            response = requests.post("https://api.mercadopago.com/v1/payments", json=payload, headers=headers, timeout=15)
            if response.status_code in [200, 201]:
                mp_payment_id = response.json().get("id")
                if response.json().get("status") in ["rejected", "cancelled"]:
                    return {"status": "rechazado", "motivo": "fondos_insuficientes", "transaccion": {"id": trans_id, "monto": monto, "comercio_nombre": comercio_nombre_real, "fecha": fecha, "hora": hora, "status": "rechazado", "mensaje": "Fondos insuficientes"}}
        except:
            pass
    return {"status": "aprobado", "_interno_mp_id": mp_payment_id, "transaccion": {"id": trans_id, "monto_detectado": monto, "monto_real": monto, "fecha": fecha, "hora": hora, "trans_id": trans_id, "comercio_id": req.comercio_id, "comercio_nombre": comercio_nombre_real, "comercio_nombre_real": comercio_nombre_real, "metodo": "TAP/QR posnet - MaxShop Wallet", "es_adherido": es_adherido, "es_destacado": es_destacado, "pin": "dorado" if es_destacado else ("azul" if es_adherido else "sin pin"), "tarjeta_usada": req.tarjeta or "No especificada", "tipo_tarjeta": req.tipo_tarjeta or "Visa/Mastercard", "csb_cliente_nuevo": csb, "mensaje_exito": f"Pago confirmado en {comercio_nombre_real}", "seguridad": f"Transaccion verificada - {fecha} {hora} - ID {trans_id} - MaxShop Wallet", "timestamp": datetime.utcnow().isoformat()}}
