from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
import os

app = FastAPI(title="MaxShop Enterprise")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
templates = Jinja2Templates(directory="templates")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/comercios")
def get_comercios():
    r = supabase.table("comercios").select("*").order("id", desc=True).execute()
    return {"success": True, "data": r.data}

@app.get("/api/usuario/{correo}")
def get_usuario(correo: str):
    r = supabase.table("usuarios").select("*").eq("correo", correo).single().execute()
    if not r.data:
        return JSONResponse({"success": False}, status_code=404)
    u = r.data
    u['es_pro'] = u.get('es_pro') or u.get('suscripcion_activa') or False
    u['credito_descuento_disponible'] = u.get('credito_descuento_disponible') or u.get('credito_descuento_total') or 0
    return {"success": True, "data": u}

@app.post("/api/registro")
async def registro(request: Request):
    data = await request.json()
    existe = supabase.table("usuarios").select("*").eq("correo", data['correo']).execute()
    if existe.data:
        return JSONResponse({"success": False, "error": "Ya existe"}, status_code=400)
    nuevo = {
        "nombre_completo": data['nombre_completo'],
        "dni": data['dni'],
        "direccion": data['direccion'],
        "localidad": data['localidad'],
        "whatsapp": data['whatsapp'],
        "correo": data['correo'],
        "password": data['password'],
        "es_pro": False,
        "credito_descuento_disponible": 50000,
        "credito_descuento_total": 50000,
        "suscripcion_activa": False
    }
    r = supabase.table("usuarios").insert(nuevo).execute()
    return {"success": True, "usuario": r.data[0] if r.data else nuevo}

@app.post("/api/login")
async def login(request: Request):
    data = await request.json()
    r = supabase.table("usuarios").select("*").eq("correo", data['correo']).eq("password", data['password']).single().execute()
    if not r.data:
        return JSONResponse({"success": False}, status_code=401)
    return {"success": True, "usuario": r.data}

@app.post("/api/registrar-comercio")
async def registrar_comercio(request: Request):
    data = await request.json()
    r = supabase.table("comercios").insert(data).execute()
    return {"success": True, "data": r.data}

@app.post("/api/consumir-credito")
async def consumir(request: Request):
    data = await request.json()
    usu = supabase.table("usuarios").select("*").eq("correo", data['correo_usuario']).single().execute()
    com = supabase.table("comercios").select("*").eq("nombre_fantasias", data['nombre_comercio']).single().execute()
    if not usu.data or not com.data:
        return JSONResponse({"success": False}, status_code=404)
    monto = float(data['monto_compra'])
    pct_base = float(com.data['porcentaje_descuento'])
    is_pro = usu.data.get('es_pro') or usu.data.get('suscripcion_activa')
    pct = pct_base if is_pro else pct_base * 0.5
    ahorro = monto * (pct / 100)
    disponible = float(usu.data.get('credito_descuento_disponible') or usu.data.get('credito_descuento_total') or 0)
    if ahorro > disponible:
        ahorro = disponible
    nuevo_cred = disponible - ahorro
    supabase.table("usuarios").update({"credito_descuento_disponible": nuevo_cred, "credito_descuento_total": nuevo_cred}).eq("correo", data['correo_usuario']).execute()
    try:
        supabase.table("acciones_log").insert({"correo_usuario": data['correo_usuario'], "nombre_comercio": data['nombre_comercio'], "monto_compra": monto, "ahorro_aplicado": ahorro}).execute()
    except:
        pass
    return {"success": True, "ahorro_aplicado": ahorro, "nuevo_credito": nuevo_cred}

@app.post("/api/pagos/crear-preferencia")
async def crear_pref(request: Request):
    data = await request.json()
    return {"success": True, "init_point": f"https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=DEMO-{data['tipo']}"}

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
