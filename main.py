from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os, uuid
from datetime import datetime

app = FastAPI(title="MaxShop Descuento de Locos")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
templates = Jinja2Templates(directory="templates")

ADMIN_KEY = os.getenv("ADMIN_KEY", "MaxShop2026!Admin")
RUBROS = ["gastronomia","indumentaria","supermercado","farmacia","ferreteria","estetica","gimnasio","tecnologia","hogar","construccion","automotriz","libreria","jugueteria","calzado","servicios","salud","mascotas","otros"]

_supabase = None
def get_supabase():
    global _supabase
    if _supabase: return _supabase
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SECRET_KEY")
        if not url or not key: return None
        _supabase = create_client(url, key)
        return _supabase
    except: return None

def get_mp():
    try:
        import mercadopago
        token = os.getenv("MP_ACCESS_TOKEN")
        if not token: return None
        return mercadopago.SDK(token)
    except: return None

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {})

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    sb = get_supabase()
    if not sb: return JSONResponse({"success": False, "error":"No supabase"},500)
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    name = f"{uuid.uuid4()}.{ext}"
    content = await file.read()
    try:
        sb.storage.from_("comercios").upload(name, content, {"content-type": file.content_type or "image/jpeg"})
        url = sb.storage.from_("comercios").get_public_url(name)
        return {"success": True, "url": url}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)},500)

@app.get("/api/comercios")
def comercios():
    sb = get_supabase()
    if not sb: return {"success":True,"data":[]}
    r = sb.table("comercios").select("*").order("id", desc=True).execute()
    return {"success": True, "data": r.data or []}

@app.post("/api/registro")
async def registro(req: Request):
    sb = get_supabase(); d = await req.json()
    ex = sb.table("usuarios").select("id").eq("correo", d['correo']).execute()
    if ex.data: return JSONResponse({"success": False, "error":"Correo ya existe"},400)
    nuevo = {
        "nombre_completo": d['nombre_completo'], "dni": d['dni'], "direccion": d['direccion'],
        "localidad": d['localidad'], "whatsapp": d['whatsapp'], "correo": d['correo'], "password": d['password'],
        "es_pro": False, "credito_descuento_disponible": 50000, "credito_descuento_total": 50000,
        "suscripcion_activa": False, "credito_ilimitado": False, "fecha_registro": datetime.now().isoformat()
    }
    sb.table("usuarios").insert(nuevo).execute()
    return {"success": True}

@app.post("/api/login")
async def login(req: Request):
    sb = get_supabase(); d = await req.json()
    r = sb.table("usuarios").select("*").eq("correo", d['correo']).eq("password", d['password']).single().execute()
    if not r.data: return JSONResponse({"success": False, "error":"Credenciales"},401)
    return {"success": True, "usuario": r.data}

@app.post("/api/login-comercio")
async def login_comercio(req: Request):
    sb = get_supabase(); d = await req.json()
    r = sb.table("comercios").select("*").eq("correo", d['correo']).eq("password", d['password']).single().execute()
    if not r.data: return JSONResponse({"success": False, "error":"Credenciales comercio incorrectas"},401)
    return {"success": True, "comercio": r.data}

@app.post("/api/registrar-comercio")
async def reg_com(req: Request):
    sb = get_supabase(); d = await req.json()
    pct = float(d.get('porcentaje_descuento') or 5)
    if pct < 5: return JSONResponse({"success": False, "error":"Minimo 5 por ciento obligatorio por clausula"},400)
    d['porcentaje_diario_fijo'] = 5
    d['bloqueado_edicion'] = True
    d['fecha_alta'] = datetime.now().isoformat()
    if not d.get('correo') or not d.get('password'):
        return JSONResponse({"success": False, "error":"El comercio debe tener correo y contraseña para su panel privado"},400)
    r = sb.table("comercios").insert(d).execute()
    return {"success": True, "data": r.data}

@app.post("/api/crear-pago-recarga")
async def crear_pago_recarga(req: Request):
    d = await req.json()
    mp = get_mp()
    if not mp:
        sb = get_supabase()
        u = sb.table("usuarios").select("*").eq("correo", d['correo']).single().execute()
        if u.data and not u.data.get('credito_ilimitado'):
            nuevo = float(u.data.get('credito_descuento_disponible') or 0) + 10000
            total = float(u.data.get('credito_descuento_total') or 0) + 10000
            sb.table("usuarios").update({"credito_descuento_disponible": nuevo, "credito_descuento_total": total}).eq("correo", d['correo']).execute()
            return {"success": True, "demo": True, "nuevo_credito": nuevo, "init_point": None}
        return {"success": False}
    pref = {
        "items": [{"title":"Recarga MaxShop 500 pesos por 10000 de credito","quantity":1,"unit_price":500,"currency_id":"ARS"}],
        "payer": {"email": d['correo']},
        "external_reference": f"recarga_{d['correo']}_{uuid.uuid4()}",
        "back_urls": {"success": f"{os.getenv('BASE_URL','')}/?pago=ok", "failure": f"{os.getenv('BASE_URL','')}/?pago=fail"},
        "auto_return": "approved"
    }
    res = mp.preference().create(pref)
    return {"success": True, "init_point": res["response"]["init_point"]}

@app.post("/api/crear-pago-pro")
async def crear_pago_pro(req: Request):
    d = await req.json()
    mp = get_mp()
    if not mp:
        sb = get_supabase()
        sb.table("usuarios").update({"es_pro": True, "suscripcion_activa": True, "credito_ilimitado": True, "credito_descuento_disponible": 999999999}).eq("correo", d['correo']).execute()
        return {"success": True, "demo": True, "init_point": None}
    pref = {
        "items": [{"title":"MaxShop PRO 5000 pesos - Credito ilimitado y 100 por ciento descuentos","quantity":1,"unit_price":5000,"currency_id":"ARS"}],
        "payer": {"email": d['correo']},
        "external_reference": f"pro_{d['correo']}_{uuid.uuid4()}",
        "back_urls": {"success": f"{os.getenv('BASE_URL','')}/?pro=ok", "failure": f"{os.getenv('BASE_URL','')}/?pro=fail"},
        "auto_return": "approved"
    }
    res = mp.preference().create(pref)
    return {"success": True, "init_point": res["response"]["init_point"]}

@app.post("/api/consumir-credito")
async def consumir(req: Request):
    sb = get_supabase(); d = await req.json()
    usu = sb.table("usuarios").select("*").eq("correo", d['correo_usuario']).single().execute()
    com = sb.table("comercios").select("*").eq("nombre_fantasias", d['nombre_comercio']).single().execute()
    if not usu.data or not com.data: return JSONResponse({"success": False, "error":"No encontrado"},404)
    monto = float(d['monto_compra'])
    pct_com = float(com.data.get('porcentaje_descuento') or 5)
    es_pro = usu.data.get('es_pro') or usu.data.get('credito_ilimitado')
    pct_real = pct_com if es_pro else pct_com*0.5
    ahorro = monto*(pct_real/100)
    if es_pro and usu.data.get('credito_ilimitado'):
        nuevo = "ILIMITADO"
    else:
        disp = float(usu.data.get('credito_descuento_disponible') or 0)
        if ahorro>disp: ahorro=disp
        nuevo = disp-ahorro
        sb.table("usuarios").update({"credito_descuento_disponible": nuevo}).eq("correo", d['correo_usuario']).execute()
    try: sb.table("acciones_log").insert({"correo_usuario": d['correo_usuario'], "nombre_comercio": d['nombre_comercio'], "monto_compra": monto, "ahorro_aplicado": ahorro, "porcentaje_aplicado": pct_real, "fecha": datetime.now().isoformat()}).execute()
    except: pass
    return {"success": True, "ahorro_aplicado": ahorro, "porcentaje_aplicado": pct_real, "nuevo_credito": nuevo, "es_pro": bool(es_pro)}

@app.post("/api/qr-scan")
async def qr_scan(req: Request):
    sb = get_supabase(); d = await req.json()
    try:
        sb.table("qr_scans").insert({
            "comercio_id": d.get('comercio_id'),
            "nombre_comercio": d.get('nombre_comercio'),
            "correo_usuario": d.get('correo_usuario'),
            "fecha": datetime.now().isoformat()
        }).execute()
    except: pass
    return {"success": True}

@app.post("/api/admin/login")
async def admin_login(req: Request):
    d = await req.json()
    if d.get('key')!= ADMIN_KEY:
        return JSONResponse({"success": False, "error":"Clave admin incorrecta"},401)
    return {"success": True}

@app.get("/api/admin/datos")
def admin_datos(key: str = ""):
    if key!= ADMIN_KEY:
        return JSONResponse({"success": False, "error":"No autorizado"},401)
    sb = get_supabase()
    rc = sb.table("comercios").select("*").order("id", desc=True).execute()
    ru = sb.table("usuarios").select("*").order("id", desc=True).execute()
    try: ra = sb.table("acciones_log").select("*").order("id", desc=True).limit(500).execute(); acc = ra.data or []
    except: acc=[]
    try: rs = sb.table("qr_scans").select("*").order("id", desc=True).limit(500).execute(); scans = rs.data or []
    except: scans=[]
    total_ahorro = sum([float(a.get('ahorro_aplicado') or 0) for a in acc])
    ventas_por_comercio = {}
    for a in acc:
        nombre = a.get('nombre_comercio')
        ventas_por_comercio[nombre] = ventas_por_comercio.get(nombre, 0) + float(a.get('monto_compra') or 0)
    return {"success": True, "comercios": rc.data or [], "usuarios": ru.data or [], "acciones": acc, "scans": scans, "total_ahorro": total_ahorro, "ventas_por_comercio": ventas_por_comercio}

@app.post("/api/admin/editar-comercio")
async def editar_comercio(req: Request):
    d = await req.json()
    if d.get('admin_key')!= ADMIN_KEY:
        return JSONResponse({"success": False, "error":"No autorizado"},401)
    sb = get_supabase()
    cid = d.get('id')
    update_data = {k: v for k, v in d.items() if k in ['porcentaje_descuento','descripcion','bloqueado_edicion','direccion','telefono']}
    sb.table("comercios").update(update_data).eq("id", cid).execute()
    return {"success": True}

@app.delete("/api/admin/comercio/{id}")
def del_com(id: int, key: str = ""):
    if key!= ADMIN_KEY: return JSONResponse({"success": False},401)
    sb = get_supabase(); sb.table("comercios").delete().eq("id", id).execute(); return {"success": True}
@app.delete("/api/admin/usuario/{correo}")
def del_usu(correo: str, key: str = ""):
    if key!= ADMIN_KEY: return JSONResponse({"success": False},401)
    sb = get_supabase(); sb.table("usuarios").delete().eq("correo", correo).execute(); return {"success": True}
