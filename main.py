import os, hmac, hashlib, uuid, base64
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import jwt
try:
    import qrcode
    QR_AVAILABLE=True
except:
    QR_AVAILABLE=False
    qrcode=None
from io import BytesIO

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
JWT_SECRET = os.getenv("JWT_SECRET", "maxshop-super-secret-2026")
QR_SECRET = os.getenv("QR_SECRET", "qr-hmac-maxshop")
MIN_DESCUENTO = 5
MIN_CASHBACK = 5
COMISION = 0.017

app = FastAPI(title="MaxShop V2")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class QRComercioRequest(BaseModel):
    comercio_id: str
    caja_id: Optional[str] = "caja_1"

class PagoViaAppRequest(BaseModel):
    user_id: str
    comercio_id: str
    qr_comercio: str
    monto_original: float
    metodo_pago_token: str = "demo"

def generar_qr_comercio(comercio_id: str):
    payload = {"comercio_id": comercio_id, "jti": str(uuid.uuid4()), "exp": datetime.utcnow() + timedelta(minutes=10), "iat": datetime.utcnow(), "tipo": "comercio_cobro"}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    firma = hmac.new(QR_SECRET.encode(), token.encode(), hashlib.sha256).hexdigest()[:16]
    qr_data = f"MAXSHOP-COMERCIO:{token}.{firma}"
    b64 = ""
    if QR_AVAILABLE:
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
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "QR expirado")
    except Exception as e:
        raise HTTPException(401, f"QR inválido: {e}")

@app.get("/api")
def api_status():
    return {"msg": "MaxShop V2 - Dual CashBack + 1.7% activo", "reglas": {"min_descuento": MIN_DESCUENTO, "min_cashback": MIN_CASHBACK, "comision_transaccion": "1.7%", "dual_cashback": True}}

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    else:
        return HTMLResponse(content=f"""
        <html><head><meta http-equiv='refresh' content='2;url=/docs'></head>
        <body style='font-family:sans-serif;background:#11084C;color:white;padding:40px'>
        <h1>MaxShop V2 Activo</h1>
        <p>API funcionando. Sube index.html al repo para ver la pagina completa.</p>
        <p>Reglas: {MIN_DESCUENTO}% min + {MIN_CASHBACK}% dual + 1.7%</p>
        <a href='/docs' style='color:#FF2E2E'>Ir a /docs</a> | <a href='/api' style='color:#FF2E2E'>Ver JSON API</a>
        </body></html>
        """, status_code=200)

@app.post("/comercio/qr/generar")
def comercio_qr(req: QRComercioRequest):
    return generar_qr_comercio(req.comercio_id)

@app.post("/pago/procesar-via-app")
def pago_via_app(req: PagoViaAppRequest):
    comercio_data = validar_qr_comercio(req.qr_comercio)
    comercio_id = comercio_data["comercio_id"]
    descuento = 20
    cashback_pct = 7
    if descuento < MIN_DESCUENTO or cashback_pct < MIN_CASHBACK:
        raise HTTPException(400, "Minimo 5% obligatorio")
    monto_desc = req.monto_original * (descuento/100)
    subtotal = req.monto_original - monto_desc
    cb_user = subtotal * (cashback_pct/100)
    cb_com = cb_user
    comision = round(subtotal * COMISION, 2)
    neto = subtotal - comision
    trans = {
        "id": str(uuid.uuid4()),
        "user_id": req.user_id, "comercio_id": comercio_id,
        "monto_original": req.monto_original, "descuento_pct": descuento,
        "monto_descontado": monto_desc, "subtotal_pagado": subtotal,
        "cashback_pct": cashback_pct, "cashback_usuario": round(cb_user,2),
        "cashback_comercio": round(cb_com,2), "comision_max_1_7_pct": comision,
        "neto_comercio_pesos": round(neto,2), "timestamp": datetime.utcnow().isoformat(),
        "explicacion": f"Cliente pago ${subtotal}. Vos ${comision} (1.7% MP). Comercio ${neto} + {cb_com} C$B. Usuario {cb_user} C$B"
    }
    return {"ok": True, "transaccion": trans}

@app.get("/comercios/mapa")
def comercios_mapa(lat: float = -28.469, lng: float = -65.785, radio_km: float = 10, q: Optional[str] = None):
    comercios = [
        {"id":"1","nombre":"Jumbo Catamarca","lat":-28.469,"lng":-65.785,"categoria":"Supermercado","descuento":35,"cashback":7,"banco":"Galicia"},
        {"id":"2","nombre":"Frávega","lat":-28.47,"lng":-65.78,"categoria":"Electro","descuento":25,"cashback":5,"banco":"Santander"},
        {"id":"3","nombre":"Adidas Alto del Solar","lat":-28.468,"lng":-65.79,"categoria":"Deporte","descuento":30,"cashback":10,"banco":"Todos"},
    ]
    if q: comercios = [c for c in comercios if q.lower() in c["nombre"].lower()]
    return {"comercios": comercios}

@app.post("/instituciones/cobro-recurrente")
def cobro(institucion_id: str, socio_id: str, monto_cuota: float, email_socio: str = "", whatsapp: str = ""):
    com = round(monto_cuota * 0.15, 2)
    inst = round(monto_cuota - com, 2)
    return {"ok": True, "link_pago": f"https://mpago.la/maxshop-{uuid.uuid4().hex[:8]}", "split": {"total": monto_cuota, "institucion": inst, "comision_maxshop": com}}
