from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os, uuid

app = FastAPI(title="MaxShop")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
templates = Jinja2Templates(directory="templates")

_supabase = None
def get_supabase():
    global _supabase
    if _supabase:
        return _supabase
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = (
            os.getenv("SUPABASE_KEY") or
            os.getenv("SUPABASE_SERVICE_ROLE_KEY") or
            os.getenv("SUPABASE_SECRET_KEY") or
            os.getenv("SUPABASE_ANON_KEY")
        )
        if not url or not key:
            print("FALTAN ENV VARS SUPABASE")
            return None
        _supabase = create_client(url, key)
        print(f"Supabase conectado con key que empieza: {key[:10]}")
        return _supabase
    except Exception as e:
        print(f"Error conectando supabase: {e}")
        return None

@app.get("/health")
def health():
    sb = get_supabase()
    return {
        "status": "ok",
        "supabase_ok": sb is not None,
        "has_url": bool(os.getenv("SUPABASE_URL")),
        "has_key": bool(os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
    }

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    # ORDEN NUEVO CORRECTO PARA FASTAPI 2026
    try:
        return templates.TemplateResponse(request, "index.html", {})
    except Exception as e:
        return HTMLResponse(f"<h1>Error cargando template: {e}</h1><p>Verifica que exista templates/index.html</p>", status_code=500)

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    sb = get_supabase()
    if not sb:
        return JSONResponse({"success": False, "error": "Supabase no conectado"}, status_code=500)
    ext = file.filename.split(".")[-1] if "." in file.filename else "jpg"
    name = f"{uuid.uuid4()}.{ext}"
    content = await file.read()
    try:
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
        return {"success": True, "data": r.data or []}
    except Exception as e:
        return {"success": False, "data": [], "error": str(e)}

@app.get("/api/usuario/{correo}")
def get_usuario(correo: str):
    sb = get_supabase()
    try:
        r = sb.table("usuarios").select("*").eq("correo", correo).single().execute()
        if not r.data: return JSONResponse({"success": False}, status_code=404)
        u = r.data
        u['es_pro'] = u.get('es_pro') or u.get('suscripcion_activa') or False
        u['credito_descuento_disponible'] = u.get('credito_descuento_disponible') or u.get('credito_descuento_total') or 0
        return {"success": True, "data": u}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=404)

@app.post("/api/registro")
async def registro(req: Request):
    sb = get_supabase()
    d = await req.json()
    ex = sb.table("usuarios").select("*").eq("correo", d['correo']).execute()
    if ex.data:
        return JSONResponse({"success": False, "error": "Ya existe"}, status_code=400)
    nuevo = {
        "nombre_completo": d['nombre_completo'],
        "dni": d['dni'],
        "direccion": d['direccion'],
        "localidad": d['localidad'],
        "whatsapp": d['whatsapp'],
        "correo": d['correo'],
        "password": d['password'],
        "es_pro": False,
        "credito_descuento_disponible": 50000,
        "credito_descuento_total": 50000,
        "suscripcion_activa": False
    }
    sb.table("usuarios").insert(nuevo).execute()
    return {"success": True}

@app.post("/api/login")
async def login(req: Request):
    sb = get_supabase()
    d = await req.json()
    r = sb.table("usuarios").select("*").eq("correo", d['correo']).eq("password", d['password']).single().execute()
    if not r.data:
        return JSONResponse({"success": False, "error": "Credenciales"}, status_code=401)
    return {"success": True, "usuario": r.data}

@app.post("/api/registrar-comercio")
async def registrar_comercio(req: Request):
    sb = get_supabase()
    d = await req.json()
    r = sb.table("comercios").insert(d).execute()
    return {"success": True, "data": r.data}

@app.post("/api/consumir-credito")
async def consumir_credito(req: Request):
    sb = get_supabase()
    d = await req.json()
    usu = sb.table("usuarios").select("*").eq("correo", d['correo_usuario']).single().execute()
    com = sb.table("comercios").select("*").eq("nombre_fantasias", d['nombre_comercio']).single().execute()
    if not usu.data or not com.data:
        return JSONResponse({"success": False, "error": "No encontrado"}, status_code=404)
    monto = float(d['monto_compra'])
    pct = float(com.data.get('porcentaje_descuento') or 20)
    is_pro = usu.data.get('es_pro') or usu.data.get('suscripcion_activa')
    if not is_pro: pct = pct * 0.5
    ahorro = monto * (pct / 100)
    disp = float(usu.data.get('credito_descuento_disponible') or 0)
    if ahorro > disp: ahorro = disp
    nuevo = disp - ahorro
    sb.table("usuarios").update({"credito_descuento_disponible": nuevo, "credito_descuento_total": nuevo}).eq("correo", d['correo_usuario']).execute()
    try:
        sb.table("acciones_log").insert({
            "correo_usuario": d['correo_usuario'],
            "nombre_comercio": d['nombre_comercio'],
            "monto_compra": monto,
            "ahorro_aplicado": ahorro
        }).execute()
    except:
        pass
    return {"success": True, "ahorro_aplicado": ahorro, "nuevo_credito": nuevo}

@app.get("/api/admin/datos")
def admin_datos():
    sb = get_supabase()
    rc = sb.table("comercios").select("*").order("id", desc=True).execute()
    ru = sb.table("usuarios").select("*").order("id", desc=True).execute()
    try:
        ra = sb.table("acciones_log").select("*").order("id", desc=True).limit(100).execute()
        acciones = ra.data or []
    except:
        acciones = []
    usuarios = []
    for u in (ru.data or []):
        u['es_pro'] = u.get('es_pro') or u.get('suscripcion_activa') or False
        u['credito_descuento_disponible'] = u.get('credito_descuento_disponible') or u.get('credito_descuento_total') or 0
        usuarios.append(u)
    return {"success": True, "comercios": rc.data or [], "usuarios": usuarios, "acciones": acciones}
