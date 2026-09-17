"""
MaxShop - Descuentos de Locos - Backend Inteligente
Stack: FastAPI + Supabase + Firebase + Mercado Pago
Autor: Max Diaz - Arquitectura lista para Render.com
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

# CONFIG - poner en .env en producción
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://tu-proyecto.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "tu-anon-key")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN", "TEST-...")
MP_COMMISSION_ACCOUNT = os.getenv("MP_COMMISSION_EMAIL", "max.diaz@mercadopago.com")
JWT_SECRET = os.getenv("JWT_SECRET", "maxshop-super-secret-2026")
QR_SECRET = os.getenv("QR_SECRET", "qr-hmac-maxshop")
COMMISSION_RATE = float(os.getenv("COMMISSION_RATE", "0.15")) # 15% tuyo

app = FastAPI(title="MaxShop API", version="2.0.0", description="Descuentos de Locos - Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELOS ---
class User(BaseModel):
    id: str
    role: str # user, comercio, institucion, admin
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
    descuento: int # %
    cashback_pct: int = 5
    descripcion: str
    vigencia_hasta: datetime
    banco: Optional[str] = None

class QRRequest(BaseModel):
    user_id: str
    comercio_id: Optional[str] = None

class PagoSocioRequest(BaseModel):
    institucion_id: str
    socio_id: str
    monto_cuota: float
    email_socio: str
    whatsapp: str

class Transaccion(BaseModel):
    id: str
    user_id: str
    comercio_id: str
    monto_original: float
    monto_final: float
    cashback_generado: float
    qr_code: str
    timestamp: datetime

# --- MOCK DB (reemplazar por supabase-py) ---
# En prod: from supabase import create_client; supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- UTILS SEGURIDAD QR DINÁMICO ---
def generar_qr_dinamico(user_id: str) -> dict:
    payload = {
        "uid": user_id,
        "jti": str(uuid.uuid4()),
        "exp": datetime.utcnow() + timedelta(seconds=30),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    # Firma HMAC extra
    firma = hmac.new(QR_SECRET.encode(), token.encode(), hashlib.sha256).hexdigest()[:16]
    qr_data = f"{token}.{firma}"
    # Generar imagen base64 (para app)
    qr = qrcode.make(qr_data)
    buf = BytesIO()
    qr.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return {"qr_data": qr_data, "qr_base64": b64, "expires_in": 30}

def validar_qr(qr_data: str) -> dict:
    try:
        token, firma = qr_data.rsplit(".",1)
        firma_esperada = hmac.new(QR_SECRET.encode(), token.encode(), hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(firma, firma_esperada):
            raise HTTPException(401, "QR Firma inválida")
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "QR expirado - generar nuevo")
    except Exception as e:
        raise HTTPException(401, f"QR inválido: {e}")

# --- ENDPOINTS CORE ---

@app.get("/")
def root():
    return {"msg": "MaxShop API - Descuentos de Locos - Activa", "colors": {"primary": "#11084C", "accent": "#FF2E2E"}}

@app.post("/qr/generar")
def qr_generar(req: QRRequest):
    # Solo usuarios validados
    return generar_qr_dinamico(req.user_id)

@app.post("/qr/validar-y-cobrar")
def qr_validar(qr_data: str, comercio_id: str, monto: float):
    data = validar_qr(qr_data)
    user_id = data["uid"]
    # Lógica descuento: buscar promo activa comercio
    descuento = 25 # mock - en prod query Supabase
    cashback_pct = 5
    monto_final = monto * (1 - descuento/100)
    cashback = monto_final * (cashback_pct/100)
    # Registrar transacción en Supabase
    trans = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "comercio_id": comercio_id,
        "monto_original": monto,
        "monto_final": monto_final,
        "cashback_generado": cashback,
        "timestamp": datetime.utcnow().isoformat()
    }
    # Aquí: supabase.table("transacciones").insert(trans).execute()
    # y supabase.rpc("incrementar_cashback", {"uid": user_id, "monto": cashback})
    return {"ok": True, "transaccion": trans, "mensaje": f"Descuento {descuento}% aplicado + ${cashback:.0f} C$B acreditado"}

@app.get("/comercios/mapa")
def comercios_mapa(lat: float = -28.469, lng: float = -65.785, radio_km: float = 10, q: Optional[str] = None):
    # En prod: PostGIS query ST_DWithin
    comercios_mock = [
        {"id":"1","nombre":"Jumbo Catamarca","lat":-28.469,"lng":-65.785,"categoria":"Supermercado","descuento":35,"banco":"Galicia","banner":"https://..."},
        {"id":"2","nombre":"Frávega","lat":-28.47,"lng":-65.78,"categoria":"Electro","descuento":30,"banco":"Santander"},
        {"id":"3","nombre":"Adidas Alto del Solar","lat":-28.468,"lng":-65.79,"categoria":"Deporte","descuento":30,"banco":"Todos"},
    ]
    if q:
        comercios_mock = [c for c in comercios_mock if q.lower() in c["nombre"].lower()]
    return {"comercios": comercios_mock, "total": len(comercios_mock)}

@app.get("/promos/banners")
def banners_activos():
    # Banner del estilo que compartiste - gente comprando
    return {
        "banners": [
            {"id":"b1","titulo":"35% JUMBO + 5% C$B","img":"banner_gente_comprando.jpg","comercio_id":"1","cta":"Ver en mapa"},
            {"id":"b2","titulo":"30% ADIDAS con Galicia","img":"banner_adidas.jpg","comercio_id":"3"}
        ]
    }

@app.post("/instituciones/cobro-recurrente")
def cobro_recurrente(req: PagoSocioRequest):
    """
    Lógica clave: Split automático Mercado Pago
    Cliente paga $10.000 -> $8.500 institución + $1.500 Max (15%)
    """
    monto_total = req.monto_cuota
    comision_max = round(monto_total * COMMISSION_RATE, 2)
    monto_institucion = round(monto_total - comision_max, 2)

    # Crear preferencia MP con split (Marketplace)
    # En prod usar mercadopago SDK:
    # preference_data = {
    #   "items": [{"title": f"Cuota socio {req.socio_id}", "quantity":1, "unit_price": monto_total}],
    #   "marketplace_fee": comision_max,
    #   "notification_url": "https://api.maxshop.com.ar/webhooks/mp"
    # }
    # mp_client.preference().create(preference_data)

    # Disparo mensajería (mock - en prod: WhatsApp Cloud API + Supabase Edge Function)
    mensaje = f"Hola! Tu cuota de ${monto_total} fue procesada. {monto_institucion} para institución, comprobante enviado."

    return {
        "ok": True,
        "link_pago": f"https://mpago.la/maxshop-{uuid.uuid4().hex[:8]}",
        "split": {"total": monto_total, "institucion": monto_institucion, "comision_maxshop": comision_max, "destino_comision": MP_COMMISSION_ACCOUNT},
        "mensajeria": {"whatsapp": req.whatsapp, "email": req.email_socio, "estado": "encolado"},
        "mensaje": mensaje
    }

@app.post("/webhooks/mp")
def webhook_mp(body: dict):
    # Validar firma MP, actualizar estado en Supabase, disparar push Firebase
    # supabase.table("pagos").update({"status": body["status"]}).eq("id", body["id"]).execute()
    # firebase_admin.messaging.send(...)
    return {"received": True}

@app.get("/admin/resumen")
def admin_resumen(role: str = Header(None)):
    if role != "admin":
        raise HTTPException(403, "Solo admin Max")
    return {
        "comisiones_hoy": 45230.5,
        "transacciones": 124,
        "cashback_emitido": 89200,
        "instituciones_activas": 12,
        "comercios_adh": 87,
        "mapa_calor": "supabase view"
    }

# --- Para Render: uvicorn main:app --host 0.0.0.0 --port $PORT
