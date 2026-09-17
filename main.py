
"""
MaxShop - Descuentos de Locos - Backend Inteligente V2 FANATIZADO
Stack: FastAPI + Supabase + Firebase + Mercado Pago
Actualización: Dual CashBack + Comisión 1.7% en pago + Mínimos 5%
Autor: Max Diaz
"""
import os, time, hmac, hashlib, uuid
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import jwt
import qrcode
from io import BytesIO
import base64

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://tu-proyecto.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "tu-anon-key")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN", "TEST-...")
MP_COMMISSION_ACCOUNT = os.getenv("MP_COMMISSION_EMAIL", "max.diaz@mercadopago.com")
JWT_SECRET = os.getenv("JWT_SECRET", "maxshop-super-secret-2026")
QR_SECRET = os.getenv("QR_SECRET", "qr-hmac-maxshop")
COMMISSION_RATE_INSTITUCION = float(os.getenv("COMMISSION_RATE", "0.15"))
COMISION_TRANSACCION = 0.017
MIN_DESCUENTO = 5
MIN_CASHBACK = 5

app = FastAPI(title="MaxShop API V2", version="2.1.0", description="Descuentos de Locos - Dual CashBack + 1.7%")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)

class User(BaseModel):
    id: str
    role: str
    email: str
    cashback_balance: float = 0.0

class Comercio(BaseModel):
    id: str
    nombre: str
    lat: float
    lng: float
    categoria: str
    descuento_max: int
    banco_tarjetas: List[str] = []
    banner_url: Optional[str] = None
    activo: bool = True

class Promo(BaseModel):
    id: str
    comercio_id: str
    titulo: str
    descuento: int
    cashback_pct: int = 5
    descripcion: str
    vigencia_hasta: datetime
    banco: Optional[str] = None

class QRComercioRequest(BaseModel):
    comercio_id: str
    caja_id: Optional[str] = "caja_1"

class PagoViaAppRequest(BaseModel):
    user_id: str
    comercio_id: str
    qr_comercio: str
    monto_original: float
    metodo_pago_token: str  # token de tarjeta del user guardado en MP Customer

def validar_minimos(descuento: int, cashback: int):
    if descuento < MIN_DESCUENTO:
        raise HTTPException(400, f"Descuento mínimo {MIN_DESCUENTO}% (tu fee publicidad) - recibido {descuento}%")
    if cashback < MIN_CASHBACK:
        raise HTTPException(400, f"CashBack mínimo {MIN_CASHBACK}% obligatorio - recibido {cashback}%")

def generar_qr_comercio(comercio_id: str) -> dict:
    payload = {"comercio_id": comercio_id, "jti": str(uuid.uuid4()), "exp": datetime.utcnow() + timedelta(minutes=10), "iat": datetime.utcnow(), "tipo": "comercio_cobro"}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    firma = hmac.new(QR_SECRET.encode(), token.encode(), hashlib.sha256).hexdigest()[:16]
    qr_data = f"MAXSHOP-COMERCIO:{token}.{firma}"
    qr = qrcode.make(qr_data)
    buf = BytesIO(); qr.save(buf, format="PNG"); b64 = base64.b64encode(buf.getvalue()).decode()
    return {"qr_data": qr_data, "qr_base64": b64, "expires_in": 600}

def validar_qr_comercio(qr_data: str):
    try:
        if not qr_data.startswith("MAXSHOP-COMERCIO:"): raise Exception("No es QR comercio")
        clean = qr_data.replace("MAXSHOP-COMERCIO:","")
        token, firma = clean.rsplit(".",1)
        firma_esp = hmac.new(QR_SECRET.encode(), token.encode(), hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(firma, firma_esp): raise HTTPException(401, "Firma inválida")
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        if decoded.get("tipo") != "comercio_cobro": raise Exception("Tipo QR incorrecto")
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "QR comercio expirado")
    except Exception as e:
        raise HTTPException(401, f"QR comercio inválido: {e}")

def generar_qr_usuario(user_id: str) -> dict:
    payload = {"uid": user_id, "jti": str(uuid.uuid4()), "exp": datetime.utcnow() + timedelta(seconds=30), "iat": datetime.utcnow()}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    firma = hmac.new(QR_SECRET.encode(), token.encode(), hashlib.sha256).hexdigest()[:16]
    qr_data = f"{token}.{firma}"
    qr = qrcode.make(qr_data); buf = BytesIO(); qr.save(buf, format="PNG"); b64 = base64.b64encode(buf.getvalue()).decode()
    return {"qr_data": qr_data, "qr_base64": b64, "expires_in": 30}

@app.get("/")
def root():
    return {"msg": "MaxShop V2 - Dual CashBack + 1.7% activo", "reglas": {"min_descuento": MIN_DESCUENTO, "min_cashback": MIN_CASHBACK, "comision_transaccion": "1.7%", "dual_cashback": True}}

@app.post("/comercio/qr/generar")
def comercio_qr_generar(req: QRComercioRequest):
    return generar_qr_comercio(req.comercio_id)

@app.post("/pago/procesar-via-app")
def pago_procesar_via_app(req: PagoViaAppRequest):
    """
    NUEVO FLUJO V2 FANATIZADO:
    1. Cliente escanea QR del COMERCIO (no al revés)
    2. Cliente paga desde la app con tarjeta asociada (token MP)
    3. Transacción:
       - Monto original: $10.000
       - Descuento comercio (ej 20%): -$2.000 -> subtotal $8.000
       - CashBack usuario 5%: $400 (se acredita en C$B, no se descuenta ahora)
       - CashBack comercio 5%: $400 (se acredita en C$B comercio, tu gancho para sumar comercios)
       - Comisión tuya 1.7% REAL sobre $8.000 = $136 -> va directo a tu MP
       - Neto para comercio: $8.000 - $136 = $7.864 + $400 C$B
    """
    comercio_data = validar_qr_comercio(req.qr_comercio)
    comercio_id = comercio_data["comercio_id"]
    # Mock promo - en prod query supabase
    descuento = 20  # debe ser >=5
    cashback_pct = 7  # debe ser >=5, variable por día
    validar_minimos(descuento, cashback_pct)

    monto_descontado = req.monto_original * (descuento/100)
    subtotal_a_pagar = req.monto_original - monto_descontado

    cashback_usuario = subtotal_a_pagar * (cashback_pct/100)
    cashback_comercio = cashback_usuario  # DUAL - mismo monto

    comision_max_real = round(subtotal_a_pagar * COMISION_TRANSACCION, 2)
    neto_comercio = subtotal_a_pagar - comision_max_real

    # AQUÍ VA LA INTEGRACIÓN REAL MP:
    # 1. Cobras subtotal_a_pagar al cliente usando su card token (MP Customer)
    # payment = mp_client.payment().create({
    #   "transaction_amount": subtotal_a_pagar,
    #   "token": req.metodo_pago_token,
    #   "description": f"MaxShop - Comercio {comercio_id}",
    #   "payment_method_id": "visa",
    #   "payer": {"id": customer_id},
    #   "application_fee": comision_max_real,  # ESTO VA A TU CUENTA MP AUTOMÁTICAMENTE
    #   "binary_mode": True
    # })
    # El application_fee es la clave - MP lo splitea solo a tu cuenta

    trans = {
        "id": str(uuid.uuid4()),
        "user_id": req.user_id,
        "comercio_id": comercio_id,
        "monto_original": req.monto_original,
        "descuento_pct": descuento,
        "monto_descontado": monto_descontado,
        "subtotal_pagado": subtotal_a_pagar,
        "cashback_pct": cashback_pct,
        "cashback_usuario": round(cashback_usuario,2),
        "cashback_comercio": round(cashback_comercio,2),
        "comision_max_1_7_pct": comision_max_real,
        "neto_comercio_pesos": round(neto_comercio,2),
        "metodo": "pago_desde_app_MP",
        "timestamp": datetime.utcnow().isoformat(),
        "explicacion": f"Cliente pagó ${subtotal_a_pagar}. Vos te quedás ${comision_max_real} (1.7% real en MP). Comercio recibe ${neto_comercio} + ${cashback_comercio} C$B. Usuario recibe ${cashback_usuario} C$B"
    }

    # supabase.table("transacciones").insert(trans).execute()
    # supabase.rpc("acreditar_cashback_dual", {"uid": req.user_id, "cid": comercio_id, "monto": cashback_usuario})

    return {"ok": True, "transaccion": trans}

@app.get("/comercios/mapa")
def comercios_mapa(lat: float = -28.469, lng: float = -65.785, radio_km: float = 10, q: Optional[str] = None):
    comercios = [
        {"id":"1","nombre":"Jumbo Catamarca","lat":-28.469,"lng":-65.785,"categoria":"Supermercado","descuento":35,"cashback":7,"banco":"Galicia","minimo_cumple": True},
        {"id":"2","nombre":"Frávega","lat":-28.47,"lng":-65.78,"categoria":"Electro","descuento":25,"cashback":5,"banco":"Santander"},
        {"id":"3","nombre":"Adidas Alto del Solar","lat":-28.468,"lng":-65.79,"categoria":"Deporte","descuento":30,"cashback":10,"banco":"Todos"},
    ]
    if q: comercios = [c for c in comercios if q.lower() in c["nombre"].lower()]
    return {"comercios": comercios, "reglas": f"Todos cumplen mínimo {MIN_DESCUENTO}% off + {MIN_CASHBACK}% C$B"}

@app.post("/instituciones/cobro-recurrente")
def cobro_recurrente(institucion_id: str, socio_id: str, monto_cuota: float, email_socio: str, whatsapp: str):
    comision_max = round(monto_cuota * COMMISSION_RATE_INSTITUCION, 2)
    monto_institucion = round(monto_cuota - comision_max, 2)
    return {"ok": True, "link_pago": f"https://mpago.la/maxshop-{uuid.uuid4().hex[:8]}", "split": {"total": monto_cuota, "institucion": monto_institucion, "comision_maxshop": comision_max}, "mensajeria": {"whatsapp": whatsapp, "email": email_socio}}

@app.get("/admin/resumen")
def admin_resumen(role: str = Header(None)):
    if role != "admin": raise HTTPException(403, "Solo admin Max")
    return {"comisiones_transacciones_1_7": 18450.7, "comisiones_instituciones_15": 45230.5, "cashback_dual_emitido": 178400, "regla": "5% min + dual cashback + 1.7% real"}
