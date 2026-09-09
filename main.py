import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from passlib.context import CryptContext
import mercadopago
from pathlib import Path

app = FastAPI(title="MaxShop Enterprise - Fintech", version="10.0")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
mp_sdk = mercadopago.SDK(MP_ACCESS_TOKEN) if MP_ACCESS_TOKEN else None

class ComercioModel(BaseModel):
    nombre_completo: str; correo: str; whatsapp: str; nombre_fantasias: str; rubro: str
    direccion: str; localidad: str; cuit_cuil: str; porcentaje_descuento: float = 20.0
    dia_promocion: str = "Todos los días"; logo_url: str = ""; fotos_url: str = ""

class UsuarioRegistroModel(BaseModel):
    nombre_completo: str; dni: str; direccion: str; localidad: str; whatsapp: str; correo: EmailStr; password: str
class UsuarioLoginModel(BaseModel):
    correo: EmailStr; password: str
class ConsumoQRModel(BaseModel):
    correo_usuario: str; nombre_comercio: str; monto_compra: float

def hash_password(p: str) -> str: return pwd_context.hash(p)
def verify_password(p: str, h: str) -> bool: return pwd_context.verify(p, h)
def log_accion(correo: str, tipo: str, detalle: str):
    if not supabase: return
    try: supabase.table("acciones_log").insert({"correo": correo, "tipo": tipo, "detalle": detalle}).execute()
    except: pass

def crear_preferencia(correo: str, tipo: str):
    if not mp_sdk: raise HTTPException(500, "Falta MP_ACCESS_TOKEN en Render")
    title = "MaxShop - Recarga Expres +$10k" if tipo=="RECARGA" else "MaxShop - Plan Pro Mensual"
    price = 500 if tipo=="RECARGA" else 5000
    base_url = os.getenv("RENDER_EXTERNAL_URL", "https://tu-app.onrender.com")
    pref = {"items": [{"title": title, "quantity": 1, "unit_price": float(price), "currency_id": "ARS"}],
            "payer": {"email": correo}, "external_reference": f"{correo}|{tipo}",
            "back_urls": {"success": f"{base_url}?pago=ok","failure": f"{base_url}?pago=fail","pending": f"{base_url}?pago=pending"},
            "auto_return": "approved", "notification_url": f"{base_url}/api/webhooks/mercadopago"}
    result = mp_sdk.preference().create(pref)
    if result["status"] not in [200,201]: raise HTTPException(400, f"MP Error {result}")
    return result["response"]["init_point"]
    from fastapi import UploadFile, File, Form
import requests
import uuid

@app.post("/api/solicitudes/prestamo-seguro")
async def solicitud_prestamo(
    tipo: str = Form(...),
    nombre: str = Form(...),
    whatsapp: str = Form(...),
    dni: str = Form(...),
    fotos: list[UploadFile] = File(default=[])
):
    if not supabase:
        raise HTTPException(500, "Sin BD")

    urls = []
    for foto in fotos:
        if foto.filename:
            file_content = await foto.read()
            file_name = f"{uuid.uuid4()}_{foto.filename}"
            try:
                supabase.storage.from_("prestamos-requisitos").upload(file_name, file_content, {"content-type": foto.content_type})
                public_url = supabase.storage.from_("prestamos-requisitos").get_public_url(file_name)
                urls.append(public_url)
            except Exception as e:
                print(f"Error subiendo {file_name}: {e}")

    # Guarda en DB
    supabase.table("solicitudes_prestamos").insert({
        "tipo": tipo,
        "nombre_completo": nombre,
        "whatsapp": whatsapp,
        "dni": dni,
        "fotos_urls": urls,
        "estado": "nuevo"
    }).execute()

    log_accion(whatsapp, "SOLICITUD_PRESTAMO", f"{tipo} de {nombre} DNI {dni}")

    # --- AVISO A TU WHATSAPP CON CALLMEBOT + IA ---
    CALLMEBOT_PHONE = os.getenv("CALLMEBOT_PHONE", "5493834000000") # tu numero con 549
    CALLMEBOT_APIKEY = os.getenv("CALLMEBOT_APIKEY")

    if CALLMEBOT_APIKEY:
        mensaje = f"🚨 *MaxShop Enterprise* - Nueva Solicitud%0A%0A"
        mensaje += f"*Tipo:* {tipo}%0A"
        mensaje += f"*Nombre:* {nombre}%0A"
        mensaje += f"*DNI:* {dni}%0A"
        mensaje += f"*WhatsApp Cliente:* {whatsapp}%0A"
        mensaje += f"*Fotos:* {len(urls)} adjuntas%0A"
        if urls:
            mensaje += f"*Link Foto 1:* {urls[0]}%0A"
        mensaje += f"%0A_Responde con IA en 10 seg._"

        try:
            url_callmebot = f"https://api.callmebot.com/whatsapp.php?phone={CALLMEBOT_PHONE}&text={mensaje}&apikey={CALLMEBOT_APIKEY}"
            requests.get(url_callmebot, timeout=10)
        except Exception as e:
            print(f"Error CallMeBot: {e}")

    return {"success": True, "fotos_subidas": len(urls), "urls": urls}

@app.get("/api/comercios")
def get_comercios():
    if not supabase: return {"success": True, "data": []}
    r = supabase.table("comercios").select("*").order("id", desc=True).execute()
    return {"success": True, "data": r.data}

@app.get("/api/usuario/{correo}")
def get_usuario(correo: str):
    if not supabase: raise HTTPException(500, "Sin BD")
    r = supabase.table("usuarios").select("*").eq("correo", correo).execute()
    if r.data: return {"success": True, "data": r.data[0]}
    return {"success": False}

@app.post("/api/registro")
def registro(u: UsuarioRegistroModel):
    if not supabase: raise HTTPException(500, "Sin BD")
    ex = supabase.table("usuarios").select("id").eq("correo", u.correo).execute()
    if ex.data: raise HTTPException(400, "Correo ya registrado")
    d = u.model_dump(); d["password_hash"]=hash_password(d.pop("password")); d["es_pro"]=False; d["credito_descuento_disponible"]=50000
    supabase.table("usuarios").insert(d).execute()
    log_accion(u.correo,"REGISTRO","Alta $50k")
    return {"success": True}

@app.post("/api/login")
def login(c: UsuarioLoginModel):
    if not supabase: raise HTTPException(500, "Sin BD")
    r = supabase.table("usuarios").select("*").eq("correo", c.correo).execute()
    if not r.data or not verify_password(c.password, r.data[0].get("password_hash","")): raise HTTPException(401,"Credenciales invalidas")
    return {"success": True, "usuario": r.data[0]}

@app.post("/api/registrar-comercio")
def reg_com(c: ComercioModel):
    if not supabase: raise HTTPException(500, "Sin BD")
    supabase.table("comercios").insert(c.model_dump()).execute()
    log_accion(c.correo,"COMERCIO",c.nombre_fantasias)
    return {"success": True}

@app.post("/api/pagos/crear-preferencia")
def crear_pago(p: dict):
    return {"success": True, "init_point": crear_preferencia(p.get("correo"), p.get("tipo"))}

@app.post("/api/webhooks/mercadopago")
async def webhook_mp(request: Request):
    body = await request.json()
    print(body)
    return {"ok": True}

@app.post("/api/pagos/acreditar-manual")
def acreditar(p: dict):
    correo=p.get("correo"); tipo=p.get("tipo")
    if tipo=="RECARGA":
        u=supabase.table("usuarios").select("credito_descuento_disponible").eq("correo",correo).execute()
        actual=float(u.data[0].get("credito_descuento_disponible",0)) if u.data else 0
        supabase.table("usuarios").update({"credito_descuento_disponible": actual+10000}).eq("correo",correo).execute()
    else: supabase.table("usuarios").update({"es_pro": True}).eq("correo",correo).execute()
    return {"success": True}

@app.post("/api/consumir-credito")
def consumir(consumo: ConsumoQRModel):
    if not supabase: raise HTTPException(500,"Sin BD")
    cr=supabase.table("comercios").select("porcentaje_descuento").eq("nombre_fantasias",consumo.nombre_comercio).execute()
    pct=float(cr.data[0].get("porcentaje_descuento",20.0)) if cr.data else 20.0
    ur=supabase.table("usuarios").select("*").eq("correo",consumo.correo_usuario).execute()
    if not ur.data: raise HTTPException(404,"Usuario no encontrado")
    user=ur.data[0]; es_pro=user.get("es_pro",False)
    pct_ap=pct if es_pro else pct*0.5
    ahorro=consumo.monto_compra*(pct_ap/100.0)
    cred=float(user.get("credito_descuento_disponible",0))
    if not es_pro and cred<ahorro: raise HTTPException(400,"Credito insuficiente")
    if not es_pro: supabase.table("usuarios").update({"credito_descuento_disponible": cred-ahorro}).eq("correo",consumo.correo_usuario).execute()
    return {"success": True, "ahorro_aplicado": ahorro}

@app.get("/api/admin/datos")
def admin():
    rc = supabase.table("comercios").select("*").order("id", desc=True).execute()
    ru = supabase.table("usuarios").select("*").order("id", desc=True).execute()
    ra = supabase.table("acciones_log").select("*").order("id", desc=True).limit(100).execute()
    usuarios_norm = []
    for u in (ru.data or []):
        u['es_pro'] = u.get('es_pro') or u.get('suscripcion_activa') or False
        u['credito_descuento_disponible'] = u.get('credito_descuento_disponible') or u.get('credito_descuento_total') or 0
        usuarios_norm.append(u)
    return {"success": True, "comercios": rc.data, "usuarios": usuarios_norm, "acciones": ra.data}

@app.get("/", response_class=HTMLResponse)
def ui():
    p=Path("templates/index.html")
    if p.exists(): return p.read_text(encoding="utf-8")
    return HTMLResponse("<h1>API v10 OK - Sube templates/index.html</h1>")
