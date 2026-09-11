import os
import random
import hashlib
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="MaxShop API")
templates = Jinja2Templates(directory="templates")

# Variables Render
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
ADMIN_KEY = os.getenv("ADMIN_KEY", "maxshop2024")
BASE_URL = os.getenv("BASE_URL", "https://maxshop-api.onrender.com")
MP_TOKEN = os.getenv("MP_ACCESS_TOKEN", "")

# Supabase client
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase conectado OK")
    except Exception as e:
        print(f"Error conectando Supabase: {e}")
else:
    print("FALTA SUPABASE_URL o SUPABASE_KEY en Environment")

def gen_codigo(correo: str):
    base = f"{correo}{random.randint(1000,9999)}{datetime.utcnow().isoformat()}"
    return hashlib.md5(base.encode()).hexdigest()[:6].upper()

def calcular_racha(usuario):
    ultima = usuario.get("ultima_ruleta")
    racha_actual = usuario.get("racha_dias") or 0
    if not ultima:
        return 1
    try:
        ult = datetime.fromisoformat(str(ultima).replace("Z","").split(".")[0])
        diff = (datetime.utcnow().date() - ult.date()).days
        if diff == 1:
            return racha_actual + 1
        elif diff == 0:
            return racha_actual
        else:
            return 1
    except:
        return 1

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/comercios")
async def get_comercios():
    try:
        if not supabase:
            return {"data": []}
        res = supabase.table("comercios").select("*").order("id", desc=True).execute()
        return {"data": res.data or []}
    except Exception as e:
        print("Error comercios:", e)
        return {"data": []}

@app.post("/api/registro")
async def registro(request: Request):
    try:
        body = await request.json()
        correo = body.get("correo","").lower().strip()
        if not correo:
            return JSONResponse({"error":"Correo requerido"}, status_code=400)
        if supabase:
            existe = supabase.table("usuarios").select("correo").eq("correo", correo).execute()
            if existe.data:
                return JSONResponse({"error":"Ya existe cuenta", "code":"EXISTE"}, status_code=400)
        codigo = gen_codigo(correo)
        nuevo_usuario = {
            "nombre_completo": body.get("nombre_completo"),
            "dni": body.get("dni"),
            "direccion": body.get("direccion"),
            "localidad": body.get("localidad"),
            "whatsapp": body.get("whatsapp"),
            "correo": correo,
            "password": body.get("password"),
            "credito_descuento_disponible": 20000,
            "codigo_referido": codigo,
            "codigo_referido_usado": body.get("codigo_referido_usado") or None,
            "maxcoins": 0,
            "racha_dias": 0,
            "es_pro": False,
            "credito_ilimitado": False
        }
        if supabase and body.get("codigo_referido_usado"):
            try:
                supabase.table("referidos").insert({
                    "correo_invitador": body.get("codigo_referido_usado").upper().strip(),
                    "correo_invitado": correo,
                    "validado": False
                }).execute()
            except Exception as er:
                print("Error referido:", er)
        if supabase:
            ins = supabase.table("usuarios").insert(nuevo_usuario).execute()
            usuario = ins.data[0] if ins.data else nuevo_usuario
        else:
            usuario = nuevo_usuario
        return {"success": True, "usuario": usuario}
    except Exception as e:
        print("ERROR REGISTRO:", e)
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/login")
async def login(request: Request):
    try:
        body = await request.json()
        correo = body.get("correo","").lower().strip()
        password = body.get("password","")
        if not supabase:
            return JSONResponse({"success": False, "error":"DB no conectada"}, status_code=500)
        res = supabase.table("usuarios").select("*").eq("correo", correo
