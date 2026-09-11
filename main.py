import os, random, hashlib, json
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import mercadopago
from supabase import create_client
from datetime import datetime, timedelta

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MP_TOKEN = os.getenv("MP_ACCESS_TOKEN")
ADMIN_KEY = os.getenv("ADMIN_KEY", "maxshop2024")
BASE_URL = os.getenv("BASE_URL", "https://tu-app.onrender.com")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
mp = mercadopago.SDK(MP_TOKEN) if MP_TOKEN else None

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/comercios")
async def get_comercios():
    try:
        res = supabase.table("comercios").select("*").execute()
        return {"data": res.data}
    except Exception as e:
        return {"data": [], "error": str(e)}

def gen_codigo(correo):
    return hashlib.md5((correo + str(random.random())).encode()).hexdigest()[:6].upper()

@app.post("/api/registro")
async def registro(req: Request):
    try:
        body = await req.json()
        correo = body.get("correo","").lower().strip()
        if not correo: return JSONResponse({"error":"Correo requerido"}, status_code=400)
        # existe?
        ex = supabase.table("usuarios").select("*").eq("correo", correo).execute()
        if ex.data:
            return JSONResponse({"error":"Ya existe", "code":"EXISTE"}, status_code=400)
        codigo = gen_codigo(correo)
        data = {
            "nombre_completo": body.get("nombre_completo"),
            "dni": body.get("dni"),
            "direccion": body.get("direccion"),
            "localidad": body.get("localidad"),
            "whatsapp": body.get("whatsapp"),
            "correo": correo,
            "password": body.get("password"),
            "credito_descuento_disponible": 20000,
            "codigo_referido": codigo,
            "codigo_referido_usado": body.get("codigo_referido_usado"),
            "maxcoins": 0,
            "racha_dias": 0,
            "es_pro": False,
            "credito_ilimitado": False
        }
        # referido
        ref_usado = body.get("codigo_referido_usado")
        if ref_usado:
            try:
                supabase.table("referidos").insert({"correo_invitador": ref_usado, "correo_invitado": correo, "validado": False}).execute()
            except: pass
        ins = supabase.table("usuarios").insert(data).execute()
        usuario = ins.data[0] if ins.data else data
        return {"usuario": usuario, "success": True}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/login")
async def login(req: Request):
    body = await req.json()
    correo = body.get("correo","").lower().strip()
    password = body.get("password")
    try:
        res = supabase.table("usuarios").select("*").eq("correo", correo).eq("password", password).execute()
        if not res.data:
            return JSONResponse({"success": False, "error":"Credenciales incorrectas"}, status_code=401)
        usuario = res.data[0]
        # Si no tiene codigo, se lo generamos ahora mismo
        if not usuario.get("codigo_referido"):
            nuevo = gen_codigo(correo)
            try:
                supabase.table("usuarios").update({"codigo_referido": nuevo}).eq("correo", correo).execute()
                usuario["codigo_referido"] = nuevo
            except:
                usuario["codigo_referido"] = nuevo
        return {"success": True, "usuario": usuario}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

# --- RULETA FIX DEFINITIVO ---
def calcular_racha(usuario):
    ultima = usuario.get("ultima_ruleta")
    racha = usuario.get("racha_dias") or 0
    if not ultima:
        return 1
    try:
        ult = datetime.fromisoformat(ultima.replace("Z",""))
        ahora = datetime.utcnow()
        diff = (ahora.date() - ult.date()).days
        if diff == 1:
            return racha + 1
        elif diff == 0:
            return racha
        else:
            return 1
    except:
        return racha + 1 if racha else 1

@app.post("/api/ruleta/girar")
async def girar_ruleta(req: Request):
    try:
        body = await req.json()
        correo = body.get("correo","").lower().strip()
        res = supabase.table("usuarios").select("*").eq("correo", correo).execute()
        if not res.data:
            return JSONResponse({"error":"Usuario no encontrado"}, status_code=404)
        usuario = res.data[0]

        # Check si ya giro hoy
        ultima = usuario.get("ultima_ruleta")
        if ultima:
            try:
                ult = datetime.fromisoformat(ultima.replace("Z",""))
                if ult.date() == datetime.utcnow().date():
                    return JSONResponse({"error":"Ya giraste hoy, vuelve mañana. Junta 100 MaxCoins para giro extra"}, status_code=400)
            except: pass

        premio = random.choice([500, 800, 1000, 1500, 2000, 3000])
        racha = calcular_racha(usuario)
        bonus = 3000 if racha >= 7 else 0
        if racha >= 7:
            racha = 0 # resetea despues del bonus

        nuevo_credito = float(usuario.get("credito_descuento_disponible") or 0)
        if not usuario.get("es_pro") and not usuario.get("credito_ilimitado"):
            nuevo_credito += premio + bonus

        update_data = {
            "credito_descuento_disponible": nuevo_credito,
            "racha_dias": racha,
            "ultima_ruleta": datetime.utcnow().isoformat(),
            "maxcoins": (usuario.get("maxcoins") or 0) + 5
        }
        supabase.table("usuarios").update(update_data).eq("correo", correo).execute()
        return {"premio": premio, "racha": racha, "bonus_racha": bonus, "success": True}
    except Exception as e:
        print("ERROR RULETA:", str(e))
        return JSONResponse({"error": f"Error ruleta: {str(e)}"}, status_code=500)

@app.post("/api/ruleta/canjear")
async def canjear_ruleta(req: Request):
    try:
        body = await req.json()
        correo = body.get("correo","").lower().strip()
        res = supabase.table("usuarios").select("*").eq("correo", correo).execute()
        if not res.data:
            return JSONResponse({"error":"Usuario no encontrado"}, status_code=404)
        usuario = res.data[0]
        mc = usuario.get("maxcoins") or 0
        if mc < 100:
            return JSONResponse({"error": f"Necesitas 100 MaxCoins, tenes {mc}. 10 compras = 100 = 1 giro"}, status_code=400)
        premio = random.choice([500, 1000, 1500, 2000])
        nuevo_credito = float(usuario.get("credito_descuento_disponible") or 0)
        if not usuario.get("es_pro") and not usuario.get("credito_ilimitado"):
            nuevo_credito += premio
        supabase.table("usuarios").update({
            "credito_descuento_disponible": nuevo_credito,
            "maxcoins": mc - 100
        }).eq("correo", correo).execute()
        return {"premio": premio, "success": True}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/ruleta/girar-paga")
async def girar_paga(req: Request):
    try:
        body = await req.json()
        correo = body.get("correo","").lower().strip()
        res = supabase.table("usuarios").select("*").eq("correo", correo).execute()
        if not res.data:
            return JSONResponse({"error":"Usuario no encontrado"}, status_code=404)
        usuario = res.data[0]
        premio = random.choice([1500, 2000, 3000, 5000, 8000])
        nuevo_credito = float(usuario.get("credito_descuento_disponible") or 0) + premio
        # Si es PRO, igual sumamos por si vuelve a gratis, pero no afecta
        supabase.table("usuarios").update({"credito_descuento_disponible": nuevo_credito}).eq("correo", correo).execute()
        return {"premio": premio, "success": True}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# --- PAGOS MP RULETA $500 ---
@app.post("/api/crear-pago-recarga")
async def crear_pago_recarga(req: Request):
    body = await req.json()
    correo = body.get("correo")
    if not mp:
        return JSONResponse({"error":"MP no configurado"}, status_code=500)
    pref = {
        "items": [{"title": "Ruleta MaxShop $500 - Premios 1500 a 8000", "quantity": 1, "unit_price": 500}],
        "back_urls": {"success": f"{BASE_URL}/?pago=ruleta_ok", "failure": f"{BASE_URL}/?pago=error", "pending": f"{BASE_URL}/?pago=pendiente"},
        "auto_return": "approved",
        "metadata": {"correo": correo, "tipo": "ruleta_500"}
    }
    result = mp.preference().create(pref)
    return {"init_point": result["response"]["init_point"]}

@app.post("/api/crear-pago-pro")
async def crear_pago_pro(req: Request):
    body = await req.json()
    correo = body.get("correo")
    if not mp:
        return JSONResponse({"error":"MP no configurado"}, status_code=500)
    pref = {
        "items": [{"title": "MaxShop PRO Ilimitado $5000", "quantity": 1, "unit_price": 5000}],
        "back_urls": {"success": f"{BASE_URL}/?pago=pro_ok", "failure": f"{BASE_URL}/?pago=error"},
        "auto_return": "approved",
        "metadata": {"correo": correo, "tipo": "pro"}
    }
    result = mp.preference().create(pref)
    return {"init_point": result["response"]["init_point"]}

# --- OTROS ENDPOINTS BASICOS (los que ya tenias) ---
@app.post("/api/consumir-credito")
async def consumir_credito(req: Request):
    body = await req.json()
    correo = body.get("correo_usuario","").lower()
    monto = float(body.get("monto_compra") or 0)
    res = supabase.table("usuarios").select("*").eq("correo", correo).execute()
    if not res.data: return JSONResponse({"error":"Usuario no"}, status_code=404)
    usuario = res.data[0]
    # Logica simple 10% ahorro gratis
    ahorro = monto * 0.10
    if usuario.get("es_pro") or usuario.get("credito_ilimitado"):
        ahorro = monto * 0.20
    nuevo = float(usuario.get("credito_descuento_disponible") or 0)
    if not usuario.get("es_pro") and not usuario.get("credito_ilimitado"):
        nuevo = max(0, nuevo - ahorro)
        supabase.table("usuarios").update({"credito_descuento_disponible": nuevo, "maxcoins": (usuario.get("maxcoins") or 0)+10}).eq("correo", correo).execute()
    else:
        supabase.table("usuarios").update({"maxcoins": (usuario.get("maxcoins") or 0)+10}).eq("correo", correo).execute()
    # Validar referido en primera compra
    try:
        count = supabase.table("acciones").select("id").eq("correo_usuario", correo).execute()
        if len(count.data) == 0: # primera compra
            # buscar si tiene invitador
            ref = supabase.table("referidos").select("*").eq("correo_invitado", correo).eq("validado", False).execute()
            if ref.data:
                invitador = ref.data[0]["correo_invitador"]
                # buscar invitador por codigo
                inv = supabase.table("usuarios").select("*").eq("codigo_referido", invitador).execute()
                if inv.data:
                    inv_user = inv.data[0]
                    supabase.table("usuarios").update({"credito_descuento_disponible": float(inv_user.get("credito_descuento_disponible") or 0)+10000, "maxcoins": (inv_user.get("maxcoins") or 0)+50}).eq("correo", inv_user["correo"]).execute()
                    supabase.table("referidos").update({"validado": True}).eq("id", ref.data[0]["id"]).execute()
    except: pass
    try:
        supabase.table("acciones").insert({"correo_usuario": correo, "nombre_comercio": body.get("nombre_comercio"), "monto_compra": monto, "ahorro_aplicado": ahorro}).execute()
    except: pass
    return {"success": True, "ahorro_aplicado": ahorro, "nuevo_credito": nuevo if not usuario.get("es_pro") else "ILIMITADO"}

@app.post("/api/qr-scan")
async def qr_scan(req: Request):
    return {"success": True}

@app.get("/api/notificaciones/{correo}")
async def get_notifs(correo: str):
    try:
        res = supabase.table("notificaciones").select("*").eq("destino", "todos").order("fecha", desc=True).limit(20).execute()
        return {"data": res.data}
    except:
        return {"data": []}

@app.post("/api/notificaciones/leer/{id}")
async def leer_notif(id: int):
    return {"success": True}

@app.post("/api/admin/login")
async def admin_login(req: Request):
    body = await req.json()
    if body.get("key") == ADMIN_KEY:
        return {"success": True}
    return JSONResponse({"success": False}, status_code=401)

@app.get("/api/admin/datos")
async def admin_datos(key: str):
    if key!= ADMIN_KEY:
        return JSONResponse({"success": False}, status_code=401)
    comercios = supabase.table("comercios").select("*").execute().data
    usuarios = supabase.table("usuarios").select("*").execute().data
    acciones = supabase.table("acciones").select("*").order("fecha", desc=True).limit(100).execute().data if True else []
    try:
        referidos = supabase.table("referidos").select("*").order("fecha", desc=True).execute().data
    except:
        referidos = []
    return {"success": True, "comercios": comercios, "usuarios": usuarios, "acciones": acciones, "referidos": referidos, "total_ahorro": sum([float(a.get("ahorro_aplicado") or 0) for a in acciones])}

@app.post("/api/registrar-comercio")
async def reg_comercio(req: Request):
    body = await req.json()
    ins = supabase.table("comercios").insert(body).execute()
    return {"success": True, "data": ins.data}

@app.post("/api/login-comercio")
async def login_comercio(req: Request):
    body = await req.json()
    res = supabase.table("comercios").select("*").eq("correo", body.get("correo")).eq("password", body.get("password")).execute()
    if res.data:
        return {"success": True, "comercio": res.data[0]}
    return JSONResponse({"success": False, "error":"No encontrado"}, status_code=401)

@app.post("/api/upload")
async def upload(req: Request):
    # tu logica de upload ya la tenes, deja la que tenias o usa supabase storage
    return {"success": False, "error":"usa Drive por ahora"}

@app.post("/api/admin/broadcast")
async def broadcast(req: Request):
    body = await req.json()
    if body.get("admin_key")!= ADMIN_KEY:
        return JSONResponse({"success": False}, status_code=401)
    supabase.table("notificaciones").insert({"titulo": body.get("titulo"), "mensaje": body.get("mensaje"), "imagen_url": body.get("imagen_url"), "destino": body.get("destino", "todos"), "fecha": datetime.utcnow().isoformat()}).execute()
    return {"success": True}
