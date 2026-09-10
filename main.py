from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os, uuid

app = FastAPI(title="MaxShop")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
templates = Jinja2Templates(directory="templates")

_supabase = None
def get_supabase():
    global _supabase
    if _supabase: return _supabase
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_ANON_KEY")
        if not url or not key: return None
        _supabase = create_client(url, key)
        return _supabase
    except: return None

RUBROS = ["gastronomia","indumentaria","supermercado","farmacia","ferreteria","estetica","gimnasio","tecnologia","hogar","construccion","automotriz","libreria","jugueteria","calzado","servicios","salud","mascotas","otros"]

@app.get("/health")
def health():
    sb = get_supabase()
    return {"status":"ok","supabase_ok":sb is not None}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request, "index.html", {"rubros": RUBROS})

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    sb = get_supabase()
    if not sb: return JSONResponse({"success": False, "error": "No supabase"}, status_code=500)
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    name = f"{uuid.uuid4()}.{ext}"
    content = await file.read()
    try:
        # Fix imagen Drive: subimos a bucket comercios
        sb.storage.from_("comercios").upload(name, content, {"content-type": file.content_type or "image/jpeg"})
        url = sb.storage.from_("comercios").get_public_url(name)
        return {"success": True, "url": url}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.get("/api/comercios")
def get_comercios():
    sb = get_supabase()
    if not sb: return {"success": True, "data": []}
    try:
        r = sb.table("comercios").select("*").order("id", desc=True).execute()
        return {"success": True, "data": r.data or [], "rubros": RUBROS}
    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}

@app.get("/api/usuario/{correo}")
def get_usuario(correo: str):
    sb = get_supabase()
    try:
        r = sb.table("usuarios").select("*").eq("correo", correo).single().execute()
        if not r.data: return JSONResponse({"success": False}, status_code=404)
        return {"success": True, "data": r.data}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=404)

@app.post("/api/registro")
async def registro(req: Request):
    sb = get_supabase(); d = await req.json()
    ex = sb.table("usuarios").select("id").eq("correo", d['correo']).execute()
    if ex.data: return JSONResponse({"success": False, "error": "Ya existe"}, status_code=400)
    nuevo = {
        "nombre_completo": d['nombre_completo'], "dni": d['dni'], "direccion": d['direccion'],
        "localidad": d['localidad'], "whatsapp": d['whatsapp'], "correo": d['correo'], "password": d['password'],
        "es_pro": False, "credito_descuento_disponible": 50000, "credito_descuento_total": 50000,
        "suscripcion_activa": False, "credito_ilimitado": False
    }
    sb.table("usuarios").insert(nuevo).execute()
    return {"success": True}

@app.post("/api/login")
async def login(req: Request):
    sb = get_supabase(); d = await req.json()
    r = sb.table("usuarios").select("*").eq("correo", d['correo']).eq("password", d['password']).single().execute()
    if not r.data: return JSONResponse({"success": False, "error": "Credenciales"}, status_code=401)
    return {"success": True, "usuario": r.data}

@app.post("/api/registrar-comercio")
async def registrar_comercio(req: Request):
    sb = get_supabase(); d = await req.json()
    # Validar 5% minimo
    pct = float(d.get('porcentaje_descuento') or 0)
    if pct < 5: return JSONResponse({"success": False, "error": "Minimo 5%"}, status_code=400)
    # rubro obligatorio de lista
    d['dias_descuento'] = d.get('dias_descuento') or ["lunes","martes","miercoles","jueves","viernes","sabado","domingo"]
    r = sb.table("comercios").insert(d).execute()
    return {"success": True, "data": r.data}

# RECARGA $500 -> $10.000 credito
@app.post("/api/recarga-rapida")
async def recarga_rapida(req: Request):
    sb = get_supabase(); d = await req.json()
    u = sb.table("usuarios").select("*").eq("correo", d['correo']).single().execute()
    if not u.data: return JSONResponse({"success": False}, status_code=404)
    if u.data.get('credito_ilimitado'): return {"success": True, "nuevo_credito": "ILIMITADO", "msg": "Ya sos PRO"}
    nuevo = float(u.data.get('credito_descuento_disponible') or 0) + 10000
    total = float(u.data.get('credito_descuento_total') or 0) + 10000
    sb.table("usuarios").update({"credito_descuento_disponible": nuevo, "credito_descuento_total": total}).eq("correo", d['correo']).execute()
    return {"success": True, "nuevo_credito": nuevo}

# PRO $5000 -> ilimitado y 100% descuento
@app.post("/api/activar-pro")
async def activar_pro(req: Request):
    sb = get_supabase(); d = await req.json()
    sb.table("usuarios").update({"es_pro": True, "suscripcion_activa": True, "credito_ilimitado": True, "credito_descuento_disponible": 999999999}).eq("correo", d['correo']).execute()
    return {"success": True, "msg": "PRO activado - credito ilimitado y 100% descuentos"}

@app.post("/api/consumir-credito")
async def consumir_credito(req: Request):
    sb = get_supabase(); d = await req.json()
    usu = sb.table("usuarios").select("*").eq("correo", d['correo_usuario']).single().execute()
    com = sb.table("comercios").select("*").eq("nombre_fantasias", d['nombre_comercio']).single().execute()
    if not usu.data or not com.data: return JSONResponse({"success": False, "error": "No encontrado"}, status_code=404)

    monto = float(d['monto_compra'])
    pct_comercio = float(com.data.get('porcentaje_descuento') or 5)
    es_pro = usu.data.get('es_pro') or usu.data.get('suscripcion_activa') or usu.data.get('credito_ilimitado')

    # LOGICA: PRO = 100% del % del comercio, GRATIS = 50%
    if es_pro:
        pct_real = pct_comercio
    else:
        pct_real = pct_comercio * 0.5

    ahorro = monto * (pct_real / 100)

    # Si es PRO ilimitado, no descuenta credito
    if es_pro and usu.data.get('credito_ilimitado'):
        nuevo_credito = "ILIMITADO"
    else:
        disp = float(usu.data.get('credito_descuento_disponible') or 0)
        if ahorro > disp: ahorro = disp
        nuevo_credito = disp - ahorro
        sb.table("usuarios").update({"credito_descuento_disponible": nuevo_credito}).eq("correo", d['correo_usuario']).execute()

    try:
        sb.table("acciones_log").insert({
            "correo_usuario": d['correo_usuario'], "nombre_comercio": d['nombre_comercio'],
            "monto_compra": monto, "ahorro_aplicado": ahorro, "porcentaje_aplicado": pct_real
        }).execute()
    except: pass

    return {"success": True, "ahorro_aplicado": ahorro, "porcentaje_aplicado": pct_real, "nuevo_credito": nuevo_credito, "es_pro": bool(es_pro)}

@app.get("/api/admin/datos")
def admin_datos():
    sb = get_supabase()
    rc = sb.table("comercios").select("*").order("id", desc=True).execute()
    ru = sb.table("usuarios").select("*").order("id", desc=True).execute()
    try:
        ra = sb.table("acciones_log").select("*").order("id", desc=True).limit(200).execute()
        acciones = ra.data or []
    except: acciones = []
    return {"success": True, "comercios": rc.data or [], "usuarios": ru.data or [], "acciones": acciones, "rubros": RUBROS}

@app.delete("/api/admin/comercio/{id}")
def del_comercio(id: int):
    sb = get_supabase(); sb.table("comercios").delete().eq("id", id).execute(); return {"success": True}

@app.delete("/api/admin/usuario/{correo}")
def del_usuario(correo: str):
    sb = get_supabase(); sb.table("usuarios").delete().eq("correo", correo).execute(); return {"success": True}
