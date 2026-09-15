import os
import uuid
import json
import smtplib
import requests
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from supabase import create_client
import secrets
import hashlib

app = FastAPI(title="MaxShop v3.0 FINAL DEFINITIVA")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ENV
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MERCADOPAGO_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
SMTP_CORREO = os.getenv("SMTP_CORREO")
SMTP_PASS = os.getenv("SMTP_PASS")
CALLMEBOT_APIKEY = os.getenv("CALLMEBOT_APIKEY")
PHONE = os.getenv("PHONE")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# CONFIGURACION GLOBAL - EDITABLE DESDE ADMIN
CONFIG_DEFAULT = {
    "comision_default": 2.5,
    "comisiones_por_provincia": {
        "Catamarca": 2.5, "Tucuman": 2.5, "La_Rioja": 2.5, "Santiago_del_Estero": 2.5,
        "Cordoba": 2.5, "Mendoza": 2.5, "Buenos_Aires": 2.5, "CABA": 2.5
    },
    "cashback_porcentaje": 1.2,
    "cashback_tope_uso_porcentaje": 30,
    "bienvenida_monto": 1500,
    "bienvenida_tope_por_compra": 300,
    "tope_bloqueo_comercio": 2000,
    "descuento_default": 10
}

def get_config():
    try:
        res = supabase.table("configuracion").select("*").limit(1).execute()
        if res.data:
            return res.data[0]
        return CONFIG_DEFAULT
    except:
        return CONFIG_DEFAULT

def generar_comprobante():
    return f"MAX-{uuid.uuid4().hex[:6].upper()}-{datetime.now().strftime('%d%m%Y%H%M')}"

def enviar_email(destinatario, asunto, cuerpo_html):
    if not SMTP_CORREO or not SMTP_PASS:
        return False
    try:
        msg = MIMEText(cuerpo_html, 'html')
        msg['Subject'] = asunto
        msg['From'] = SMTP_CORREO
        msg['To'] = destinatario
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SMTP_CORREO, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def enviar_whatsapp(numero, mensaje):
    if not CALLMEBOT_APIKEY:
        return False
    try:
        url = f"https://api.callmebot.com/whatsapp.php?phone={numero}&text={mensaje}&apikey={CALLMEBOT_APIKEY}"
        requests.get(url, timeout=10)
        return True
    except:
        return False

# MODELOS
class RegistroUsuario(BaseModel):
    nombre: str
    correo: str
    password: str
    whatsapp: str = ""

class LoginUsuario(BaseModel):
    correo: str
    password: str

class PagoQR(BaseModel):
    usuario_id: int
    comercio_id: int
    monto_venta: float
    tipo_pago: str # efectivo, mp
    usar_cashback: float = 0

class RegistroComercio(BaseModel):
    nombre: str
    correo: str
    password: str
    direccion: str
    whatsapp: str
    rubro: str
    provincia: str = "Catamarca"
    alias_mp: str = ""

class RegistroInstitucion(BaseModel):
    nombre: str
    tipo: str
    direccion: str
    responsable_nombre: str
    whatsapp: str
    correo: str
    password: str
    plan_tipo: str = "basico"

class RegistroSocio(BaseModel):
    institucion_id: int
    nombre_completo: str
    dni: str
    correo: str = ""
    whatsapp: str = ""
    categoria: str = ""
    cuota_monto: float

class RegistroVendedor(BaseModel):
    nombre_completo: str
    dni: str
    cuit: str = ""
    provincia: str
    whatsapp: str
    correo: str
    password: str

# ENDPOINTS USUARIOS
@app.post("/api/usuarios/registro")
def registro_usuario(data: RegistroUsuario):
    cfg = get_config()
    hashed = hashlib.sha256(data.password.encode()).hexdigest()
    try:
        ex = supabase.table("usuarios").select("*").eq("correo", data.correo).execute()
        if ex.data:
            raise HTTPException(status_code=400, detail="Correo ya registrado")
        res = supabase.table("usuarios").insert({
            "nombre": data.nombre,
            "correo": data.correo,
            "password": hashed,
            "whatsapp": data.whatsapp,
            "cashback_saldo": cfg.get("bienvenida_monto", 1500),
            "fecha_alta": datetime.now().isoformat()
        }).execute()
        user = res.data[0]
        supabase.table("wallets").insert({
            "correo_usuario": data.correo,
            "usuario_id": user["id"],
            "saldo_cashback": cfg.get("bienvenida_monto", 1500),
            "saldo_pesos": 0
        }).execute()
        enviar_email(data.correo, "¡Bienvenido a MaxShop! 🎉", f"<h2>Hola {data.nombre}!</h2><p>Te regalamos <b>${cfg.get('bienvenida_monto',1500)} de cashback</b> para usar en comercios adheridos.</p><p>Podés usar hasta $300 por compra (tope 30%).</p>")
        return {"ok": True, "usuario": user, "bienvenida": cfg.get("bienvenida_monto",1500)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/usuarios/login")
def login_usuario(data: LoginUsuario):
    hashed = hashlib.sha256(data.password.encode()).hexdigest()
    res = supabase.table("usuarios").select("*").eq("correo", data.correo).eq("password", hashed).execute()
    if not res.data:
        raise HTTPException(status_code=401, detail="Credenciales invalidas")
    return {"ok": True, "usuario": res.data[0]}

# ENDPOINTS COMERCIOS
@app.post("/api/comercios/registro")
def registro_comercio(data: RegistroComercio):
    hashed = hashlib.sha256(data.password.encode()).hexdigest()
    ex = supabase.table("comercios").select("*").eq("correo", data.correo).execute()
    if ex.data:
        raise HTTPException(status_code=400, detail="Comercio ya registrado")
    res = supabase.table("comercios").insert({
        "nombre": data.nombre,
        "correo": data.correo,
        "password": hashed,
        "direccion": data.direccion,
        "whatsapp": data.whatsapp,
        "rubro": data.rubro,
        "provincia": data.provincia,
        "alias_mp": data.alias_mp,
        "saldo_pendiente_comision": 0,
        "tope_bloqueo": get_config().get("tope_bloqueo_comercio", 2000),
        "activo": True,
        "fecha_alta": datetime.now().isoformat()
    }).execute()
    comercio = res.data[0]
    enviar_email(data.correo, "Comercio registrado en MaxShop", f"<p>Hola {data.nombre}, tu comercio fue registrado. Comisión 2.5% nacional, sin abono. Tu saldo pendiente inicia en $0. ¡A vender!</p>")
    return {"ok": True, "comercio": comercio}

@app.post("/api/comercios/upload")
async def upload_comercio_archivos(comercio_id: int = Form(...), logo: UploadFile = File(None), banner: UploadFile = File(None), imagen1: UploadFile = File(None), imagen2: UploadFile = File(None), imagen3: UploadFile = File(None)):
    urls = {}
    for key, f in [("logo_url", logo), ("banner_url", banner), ("imagen1_url", imagen1), ("imagen2_url", imagen2), ("imagen3_url", imagen3)]:
        if f:
            urls[key] = f"uploads/{comercio_id}_{key}_{f.filename}"
    if urls:
        supabase.table("comercios").update(urls).eq("id", comercio_id).execute()
    return {"ok": True, "urls": urls}

@app.get("/api/comercios/listar")
def listar_comercios():
    res = supabase.table("comercios").select("*").eq("activo", True).execute()
    return res.data

# WALLET - PAGO QR CON SALDO PENDIENTE UBER + COMPROBANTES
@app.post("/api/wallet/pagar-qr")
def pagar_qr(data: PagoQR):
    cfg = get_config()
    user_res = supabase.table("usuarios").select("*").eq("id", data.usuario_id).execute()
    com_res = supabase.table("comercios").select("*").eq("id", data.comercio_id).execute()
    if not user_res.data or not com_res.data:
        raise HTTPException(status_code=404, detail="Usuario o comercio no encontrado")
    usuario = user_res.data[0]
    comercio = com_res.data[0]
    if comercio.get("saldo_pendiente_comision",0) >= comercio.get("tope_bloqueo",2000):
        raise HTTPException(status_code=403, detail=f"Comercio bloqueado por deuda ${comercio['saldo_pendiente_comision']}. Debe pagar para reactivar QR.")
    wallet_res = supabase.table("wallets").select("*").eq("usuario_id", data.usuario_id).execute()
    wallet = wallet_res.data[0] if wallet_res.data else {"saldo_cashback":0}
    tope_cashback = data.monto_venta * cfg.get("cashback_tope_uso_porcentaje",30) / 100
    cashback_a_usar = min(data.usar_cashback, wallet.get("saldo_cashback",0), tope_cashback)
    comision_pct = cfg.get("comision_default",2.5)
    prov = comercio.get("provincia","Catamarca")
    if "comisiones_por_provincia" in cfg and prov in cfg["comisiones_por_provincia"]:
        comision_pct = cfg["comisiones_por_provincia"][prov]
    comision_generada = data.monto_venta * comision_pct / 100
    cashback_generado = data.monto_venta * cfg.get("cashback_porcentaje",1.2) / 100
    monto_pagado = data.monto_venta - cashback_a_usar
    comprobante = generar_comprobante()
    ahora = datetime.now()
    if data.tipo_pago == "efectivo":
        nueva_deuda = comercio.get("saldo_pendiente_comision",0) + comision_generada
        supabase.table("comercios").update({"saldo_pendiente_comision": nueva_deuda}).eq("id", data.comercio_id).execute()
        supabase.table("comisiones_comercios").insert({
            "comercio_id": data.comercio_id,
            "usuario_id": data.usuario_id,
            "monto_venta": data.monto_venta,
            "monto_pagado_efectivo": monto_pagado,
            "monto_pagado_mp": 0,
            "comision_generada": comision_generada,
            "comision_pendiente": comision_generada,
            "tipo_pago": "efectivo",
            "estado": "pendiente",
            "fecha_venta": ahora.isoformat(),
            "comprobante_numero": comprobante,
            "detalle": f"Venta ${data.monto_venta} a {usuario['nombre']} - Efectivo - Comisión pendiente"
        }).execute()
        nuevo_cashback = wallet.get("saldo_cashback",0) - cashback_a_usar + cashback_generado
        supabase.table("wallets").update({"saldo_cashback": nuevo_cashback}).eq("usuario_id", data.usuario_id).execute()
        supabase.table("transacciones_wallet").insert({
            "usuario_id": data.usuario_id,
            "comercio_id": data.comercio_id,
            "correo_usuario": usuario["correo"],
            "comercio_nombre": comercio["nombre"],
            "monto": monto_pagado,
            "tipo": "pago_qr_efectivo",
            "fecha": ahora.isoformat()
        }).execute()
        enviar_email(comercio["correo"], f"Comprobante pendiente {comprobante}", f"<p>Venta ${data.monto_venta} - Comisión ${comision_generada} pendiente. Fecha {ahora.strftime('%d/%m/%Y %H:%M')} - ID {comprobante}</p>")
        return {"ok": True, "tipo": "efectivo", "comprobante": comprobante, "fecha": ahora.strftime("%d/%m/%Y %H:%M"), "comision_pendiente": comision_generada, "saldo_pendiente_total": nueva_deuda}
    else:
        deuda_previa = comercio.get("saldo_pendiente_comision",0)
        total_a_cobrar_para_vos = comision_generada + deuda_previa
        monto_para_comercio = monto_pagado - total_a_cobrar_para_vos
        supabase.table("comercios").update({"saldo_pendiente_comision": 0, "total_comisiones_pagadas": comercio.get("total_comisiones_pagadas",0) + total_a_cobrar_para_vos}).eq("id", data.comercio_id).execute()
        if deuda_previa > 0:
            supabase.table("comisiones_comercios").update({"estado": "pagado", "fecha_pago": ahora.isoformat()}).eq("comercio_id", data.comercio_id).eq("estado", "pendiente").execute()
        supabase.table("comisiones_comercios").insert({
            "comercio_id": data.comercio_id,
            "usuario_id": data.usuario_id,
            "monto_venta": data.monto_venta,
            "monto_pagado_efectivo": 0,
            "monto_pagado_mp": monto_pagado,
            "comision_generada": comision_generada,
            "comision_pendiente": 0,
            "tipo_pago": "mp",
            "estado": "pagado",
            "fecha_venta": ahora.isoformat(),
            "fecha_pago": ahora.isoformat(),
            "comprobante_numero": comprobante,
            "detalle": f"Venta ${data.monto_venta} MP - Comisión ${comision_generada} + deuda ${deuda_previa} = ${total_a_cobrar_para_vos} transferido"
        }).execute()
        nuevo_cashback = wallet.get("saldo_cashback",0) - cashback_a_usar + cashback_generado
        supabase.table("wallets").update({"saldo_cashback": nuevo_cashback}).eq("usuario_id", data.usuario_id).execute()
        enviar_email(comercio["correo"], f"Comprobante PAGADO {comprobante} ✅", f"<p>Venta ${data.monto_venta} - Comisión ${comision_generada} + deuda ${deuda_previa} = ${total_a_cobrar_para_vos} - Fecha {ahora.strftime('%d/%m/%Y %H:%M')} - PAGADO</p>")
        return {"ok": True, "tipo": "mp", "comprobante": comprobante, "fecha": ahora.strftime("%d/%m/%Y %H:%M"), "total_transferido_a_maxshop": total_a_cobrar_para_vos, "monto_para_comercio": monto_para_comercio}

@app.get("/api/comercio/comisiones/{comercio_id}")
def comisiones_comercio(comercio_id: int):
    res = supabase.table("comisiones_comercios").select("*").eq("comercio_id", comercio_id).order("fecha_venta", desc=True).execute()
    comercio = supabase.table("comercios").select("saldo_pendiente_comision, total_comisiones_pagadas, tope_bloqueo").eq("id", comercio_id).execute()
    return {"comisiones": res.data, "resumen": comercio.data[0] if comercio.data else {}}

@app.get("/api/wallet/{usuario_id}")
def get_wallet(usuario_id: int):
    res = supabase.table("wallets").select("*").eq("usuario_id", usuario_id).execute()
    return res.data[0] if res.data else {}

# INSTITUCIONES - COBRO SOCIOS
@app.post("/api/instituciones/registro")
def registro_institucion(data: RegistroInstitucion):
    hashed = hashlib.sha256(data.password.encode()).hexdigest()
    res = supabase.table("instituciones").insert({"nombre": data.nombre, "tipo": data.tipo, "direccion": data.direccion, "responsable_nombre": data.responsable_nombre, "whatsapp": data.whatsapp, "correo": data.correo, "password": hashed, "plan_tipo": data.plan_tipo, "activa": True, "fecha_alta": datetime.now().isoformat()}).execute()
    return {"ok": True, "institucion": res.data[0]}

@app.post("/api/socios/registro")
def registro_socio(data: RegistroSocio):
    res = supabase.table("socios_institucion").insert({"institucion_id": data.institucion_id, "nombre_completo": data.nombre_completo, "dni": data.dni, "correo": data.correo, "whatsapp": data.whatsapp, "categoria": data.categoria, "cuota_monto": data.cuota_monto, "estado": "al_dia", "fecha_alta": datetime.now().isoformat()}).execute()
    if data.whatsapp: enviar_whatsapp(data.whatsapp, f"Hola {data.nombre_completo}, fuiste registrado - Cuota ${data.cuota_monto}")
    if data.correo: enviar_email(data.correo, "Registro socio", f"<p>Hola {data.nombre_completo}, cuota ${data.cuota_monto}</p>")
    return {"ok": True, "socio": res.data[0]}

@app.post("/api/socios/cobrar-cuota/{socio_id}")
def cobrar_cuota(socio_id: int):
    socio = supabase.table("socios_institucion").select("*").eq("id", socio_id).execute()
    s = socio.data[0]
    cfg = get_config()
    comision = s["cuota_monto"] * cfg.get("comision_default",2.5) / 100
    supabase.table("socios_institucion").update({"ultimo_pago": datetime.now().isoformat(), "estado": "al_dia"}).eq("id", socio_id).execute()
    comprobante = generar_comprobante()
    supabase.table("comisiones_comercios").insert({"comercio_id": s["institucion_id"], "usuario_id": socio_id, "monto_venta": s["cuota_monto"], "comision_generada": comision, "comision_pendiente": comision, "tipo_pago": "cuota_socio", "estado": "pendiente", "fecha_venta": datetime.now().isoformat(), "comprobante_numero": comprobante, "detalle": f"Cuota socio {s['nombre_completo']} ${s['cuota_monto']} - Comisión ${comision}"}).execute()
    if s.get("correo"): enviar_email(s["correo"], f"Comprobante cuota {comprobante}", f"<p>Pagaste ${s['cuota_monto']} - {comprobante} - {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>")
    if s.get("whatsapp"): enviar_whatsapp(s["whatsapp"], f"Cuota ${s['cuota_monto']} pagada - Comprobante {comprobante} - {datetime.now().strftime('%d/%m/%Y %H:%M')} ✅")
    return {"ok": True, "comprobante": comprobante, "comision": comision}

# MENSAJERIA
class MensajeMasivo(BaseModel):
    institucion_id: int
    mensaje: str
    tipo: str = "whatsapp"

@app.post("/api/mensajeria/masivo")
def mensaje_masivo(data: MensajeMasivo):
    socios = supabase.table("socios_institucion").select("*").eq("institucion_id", data.institucion_id).execute()
    enviados = 0
    for s in socios.data:
        if data.tipo in ["whatsapp","ambos"] and s.get("whatsapp"): enviar_whatsapp(s["whatsapp"], data.mensaje); enviados+=1
        if data.tipo in ["email","ambos"] and s.get("correo"): enviar_email(s["correo"], "Mensaje institución", f"<p>{data.mensaje}</p>"); enviados+=1
    return {"ok": True, "enviados": enviados}

@app.post("/api/mensajeria/morosos/{institucion_id}")
def mensaje_morosos(institucion_id: int):
    morosos = supabase.table("socios_institucion").select("*").eq("institucion_id", institucion_id).eq("estado", "moroso").execute()
    enviados=0
    for s in morosos.data:
        msg = f"Hola {s['nombre_completo']}, tu cuota de ${s['cuota_monto']} está vencida. Pagá acá."
        if s.get("whatsapp"): enviar_whatsapp(s["whatsapp"], msg); enviados+=1
        if s.get("correo"): enviar_email(s["correo"], "Cuota vencida", f"<p>{msg}</p>"); enviados+=1
    return {"ok": True, "morosos": len(morosos.data), "enviados": enviados}

# VENDEDORES REGIONALES
@app.post("/api/vendedores/registro")
def registro_vendedor(data: RegistroVendedor):
    hashed = hashlib.sha256(data.password.encode()).hexdigest()
    codigo = f"VENDEDOR_{data.provincia.upper()}_{secrets.token_hex(3).upper()}"
    res = supabase.table("vendedores_regionales").insert({"nombre_completo": data.nombre_completo, "dni": data.dni, "cuit": data.cuit, "provincia": data.provincia, "whatsapp": data.whatsapp, "correo": data.correo, "password": hashed, "codigo_unico": codigo, "estado": "pendiente", "terminos_aceptados": True, "fecha_aceptacion_terminos": datetime.now().isoformat(), "fecha_alta": datetime.now().isoformat()}).execute()
    return {"ok": True, "vendedor": res.data[0], "codigo": codigo}

@app.get("/api/vendedores/listar")
def listar_vendedores():
    res = supabase.table("vendedores_regionales").select("*").execute()
    return res.data

@app.post("/api/vendedores/aprobar/{vendedor_id}")
def aprobar_vendedor(vendedor_id: int):
    res = supabase.table("vendedores_regionales").update({"estado":"aprobado"}).eq("id", vendedor_id).execute()
    v = res.data[0]
    enviar_email(v["correo"], "Vendedor aprobado ✅", f"<p>Felicidades {v['nombre_completo']}, fuiste aprobado para vender en {v['provincia']}. Tu código: {v['codigo_unico']}</p>")
    return {"ok": True, "vendedor": v}

@app.get("/api/admin/resumen")
def admin_resumen():
    comercios = supabase.table("comercios").select("id", count="exact").execute()
    usuarios = supabase.table("usuarios").select("id", count="exact").execute()
    comisiones = supabase.table("comisiones_comercios").select("comision_generada, estado").execute()
    total_pendiente = sum([c["comision_generada"] for c in comisiones.data if c["estado"]=="pendiente"])
    total_pagado = sum([c["comision_generada"] for c in comisiones.data if c["estado"]=="pagado"])
    return {"comercios": comercios.count, "usuarios": usuarios.count, "total_comisiones_pendientes": total_pendiente, "total_comisiones_pagadas": total_pagado, "config": get_config()}

@app.get("/api/configuracion")
def get_configuracion():
    return get_config()

app.mount("/", StaticFiles(directory=".", html=True), name="static")
