import os
import random
import hashlib
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
from supabase import create_client, Client
import mercadopago

app = FastAPI()

# --- CONFIG ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MP_TOKEN = os.getenv("MP_ACCESS_TOKEN", "")
ADMIN_KEY = os.getenv("ADMIN_KEY", "maxshop2024")
BASE_URL = os.getenv("BASE_URL", "https://maxshop.onrender.com")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Faltan SUPABASE_URL o SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    sdk = mercadopago.SDK(MP_TOKEN) if MP_TOKEN else None
except:
    sdk = None

templates = Jinja2Templates(directory="templates")

def gen_codigo(correo: str):
    base = f"{correo}{random.randint(1000,9999)}{datetime.utcnow().isoformat()}"
    return hashlib.md5(base.encode()).hexdigest()[:6].upper()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/comercios")
async def get_comercios():
    try:
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
        existe = supabase.table("usuarios").select("correo").eq("correo", correo).execute()
        if existe.data:
            return JSONResponse({"error":"Ya existe cuenta con ese correo", "code":"EXISTE"}, status_code=400)
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
        # guardar referido pendiente
        if body.get("codigo_referido_usado"):
            try:
                supabase.table("referidos").insert({
                    "correo_invitador": body.get("codigo_referido_usado").upper().strip(),
                    "correo_invitado": correo,
                    "validado": False
                }).execute()
            except Exception as er:
                print("Error referido:", er)
        ins = supabase.table("usuarios").insert(nuevo_usuario).execute()
        usuario = ins.data[0] if ins.data else nuevo_usuario
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
        res = supabase.table("usuarios").select("*").eq("correo", correo).eq("password", password).execute()
        if not res.data:
            return JSONResponse({"success": False, "error":"Correo o clave incorrectos"}, status_code=401)
        usuario = res.data[0]
        if not usuario.get("codigo_referido"):
            nuevo_codigo = gen_codigo(correo)
            try:
                supabase.table("usuarios").update({"codigo_referido": nuevo_codigo}).eq("correo", correo).execute()
                usuario["codigo_referido"] = nuevo_codigo
            except:
                usuario["codigo_referido"] = nuevo_codigo
        return {"success": True, "usuario": usuario}
    except Exception as e:
        print("ERROR LOGIN:", e)
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

def calcular_racha(usuario):
    ultima = usuario.get("ultima_ruleta")
    racha_actual = usuario.get("racha_dias") or 0
    if not ultima:
        return 1
    try:
        ult = datetime.fromisoformat(str(ultima).replace("Z","").split(".")[0])
        ahora = datetime.utcnow()
        diff = (ahora.date() - ult.date()).days
        if diff == 1:
            return racha_actual + 1
        elif diff == 0:
            return racha_actual
        else:
            return 1
    except Exception as e:
        print("Error racha:", e)
        return 1

@app.post("/api/ruleta/girar")
async def girar_ruleta(request: Request):
    try:
        body = await request.json()
        correo = body.get("correo","").lower().strip()
        print(f"Girando ruleta para {correo}")
        res = supabase.table("usuarios").select("*").eq("correo", correo).execute()
        if not res.data:
            return JSONResponse({"error":"Usuario no encontrado"}, status_code=404)
        usuario = res.data[0]
        # validar si ya giro hoy
        ultima = usuario.get("ultima_ruleta")
        if ultima:
            try:
                ult = datetime.fromisoformat(str(ultima).replace("Z","").split(".")[0])
                if ult.date() == datetime.utcnow().date():
                    return JSONResponse({"error":"Ya giraste hoy. Vuelve mañana o junta 100 MaxCoins (10 compras) para giro extra"}, status_code=400)
            except:
                pass
        premio = random.choice([500, 800, 1000, 1500, 2000, 3000])
        racha = calcular_racha(usuario)
        bonus = 3000 if racha >= 7 else 0
        if racha >= 7:
            racha_final = 0
        else:
            racha_final = racha
        credito_actual = float(usuario.get("credito_descuento_disponible") or 0)
        es_pro = usuario.get("es_pro") or usuario.get("credito_ilimitado")
        if not es_pro:
            credito_actual = credito_actual + premio + bonus
        maxcoins_actual = (usuario.get("maxcoins") or 0) + 5
        supabase.table("usuarios").update({
            "credito_descuento_disponible": credito_actual,
            "racha_dias": racha_final,
            "ultima_ruleta": datetime.utcnow().isoformat(),
            "maxcoins": maxcoins_actual
        }).eq("correo", correo).execute()
        return {"success": True, "premio": premio, "racha": racha_final if racha < 7 else 7, "bonus_racha": bonus}
    except Exception as e:
        print("ERROR EN /api/ruleta/girar:", str(e))
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/ruleta/canjear")
async def canjear_ruleta(request: Request):
    try:
        body = await request.json()
        correo = body.get("correo","").lower().strip()
        res = supabase.table("usuarios").select("*").eq("correo", correo).execute()
        if not res.data:
            return JSONResponse({"error":"Usuario no encontrado"}, status_code=404)
        usuario = res.data[0]
        mc = usuario.get("maxcoins") or 0
        if mc < 100:
            return JSONResponse({"error": f"Necesitas 100 MaxCoins. Tenes {mc}. 10 compras = 100 MaxCoins = 1 giro"}, status_code=400)
        premio = random.choice([500, 1000, 1500, 2000])
        credito_actual = float(usuario.get("credito_descuento_disponible") or 0)
        if not (usuario.get("es_pro") or usuario.get("credito_ilimitado")):
            credito_actual += premio
        supabase.table("usuarios").update({
            "credito_descuento_disponible": credito_actual,
            "maxcoins": mc - 100
        }).eq("correo", correo).execute()
        return {"success": True, "premio": premio}
    except Exception as e:
        print("ERROR CANJEAR:", e)
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/ruleta/girar-paga")
async def girar_paga(request: Request):
    try:
        body = await request.json()
        correo = body.get("correo","").lower().strip()
        res = supabase.table("usuarios").select("*").eq("correo", correo).execute()
        if not res.data:
            return JSONResponse({"error":"Usuario no encontrado"}, status_code=404)
        usuario = res.data[0]
        premio = random.choice([1500, 2000, 3000, 5000, 8000])
        credito_actual = float(usuario.get("credito_descuento_disponible") or 0) + premio
        supabase.table("usuarios").update({
            "credito_descuento_disponible": credito_actual
        }).eq("correo", correo).execute()
        return {"success": True, "premio": premio}
    except Exception as e:
        print("ERROR GIRAR PAGA:", e)
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/crear-pago-recarga")
async def crear_pago_recarga(request: Request):
    try:
        body = await request.json()
        correo = body.get("correo","")
        if not sdk:
            return JSONResponse({"error":"Mercado Pago no configurado"}, status_code=500)
        preference_data = {
            "items": [{"title": "Ruleta MaxShop $500 - Premios 1500 a 8000", "quantity": 1, "unit_price": 500}],
            "payer": {"email": correo},
            "back_urls": {
                "success": f"{BASE_URL}/?pago=ruleta_ok",
                "failure": f"{BASE_URL}/?pago=error",
                "pending": f"{BASE_URL}/?pago=pendiente"
            },
            "auto_return": "approved",
            "metadata": {"correo": correo, "tipo": "ruleta_500"}
        }
        result = sdk.preference().create(preference_data)
        init_point = result["response"].get("init_point")
        if not init_point:
            return JSONResponse({"error": str(result)}, status_code=500)
        return {"init_point": init_point}
    except Exception as e:
        print("ERROR PAGO RECARGA:", e)
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/crear-pago-pro")
async def crear_pago_pro(request: Request):
    try:
        body = await request.json()
        correo = body.get("correo","")
        if not sdk:
            return JSONResponse({"error":"MP no configurado"}, status_code=500)
        preference_data = {
            "items": [{"title": "MaxShop PRO $5000 Ilimitado", "quantity": 1, "unit_price": 5000}],
            "payer": {"email": correo},
            "back_urls": {
                "success": f"{BASE_URL}/?pago=pro_ok",
                "failure": f"{BASE_URL}/?pago=error",
                "pending": f"{BASE_URL}/?pago=pendiente"
            },
            "auto_return": "approved",
            "metadata": {"correo": correo, "tipo": "pro"}
        }
        result = sdk.preference().create(preference_data)
        return {"init_point": result["response"]["init_point"]}
    except Exception as e:
        print("ERROR PAGO PRO:", e)
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/consumir-credito")
async def consumir_credito(request: Request):
    try:
        body = await request.json()
        correo = body.get("correo_usuario","").lower().strip()
        nombre_comercio = body.get("nombre_comercio","")
        monto = float(body.get("monto_compra") or 0)
        res = supabase.table("usuarios").select("*").eq("correo", correo).execute()
        if not res.data:
            return JSONResponse({"error":"Usuario no encontrado"}, status_code=404)
        usuario = res.data[0]
        es_pro = usuario.get("es_pro") or usuario.get("credito_ilimitado")
        if es_pro:
            ahorro = monto * 0.20
            nuevo_credito = usuario.get("credito_descuento_disponible") or 0
        else:
            ahorro = monto * 0.10
            nuevo_credito = float(usuario.get("credito_descuento_disponible") or 0) - ahorro
            if nuevo_credito < 0:
                nuevo_credito = 0
        # sumar maxcoins
        maxcoins = (usuario.get("maxcoins") or 0) + 10
        supabase.table("usuarios").update({
            "credito_descuento_disponible": nuevo_credito,
            "maxcoins": maxcoins
        }).eq("correo", correo).execute()
        # guardar accion
        try:
            supabase.table("acciones").insert({
                "correo_usuario": correo,
                "nombre_comercio": nombre_comercio,
                "monto_compra": monto,
                "ahorro_aplicado": ahorro,
                "fecha": datetime.utcnow().isoformat()
            }).execute()
        except Exception as e:
            print("Error guardando accion:", e)
        # validar referido primera compra
        try:
            acciones_previas = supabase.table("acciones").select("id", count="exact").eq("correo_usuario", correo).execute()
            es_primera = (acciones_previas.count or 0) <= 1
            if es_primera:
                ref = supabase.table("referidos").select("*").eq("correo_invitado", correo).eq("validado", False).execute()
                if ref.data:
                    codigo_invitador = ref.data[0].get("correo_invitador")
                    inv = supabase.table("usuarios").select("*").eq("codigo_referido", codigo_invitador).execute()
                    if inv.data:
                        inv_user = inv.data[0]
                        supabase.table("usuarios").update({
                            "credito_descuento_disponible": float(inv_user.get("credito_descuento_disponible") or 0) + 10000,
                            "maxcoins": (inv_user.get("maxcoins") or 0) + 50
                        }).eq("correo", inv_user["correo"]).execute()
                        supabase.table("referidos").update({"validado": True}).eq("id", ref.data[0]["id"]).execute()
        except Exception as e:
            print("Error referido validacion:", e)
        return {"success": True, "ahorro_aplicado": ahorro, "nuevo_credito": nuevo_credito if not es_pro else "ILIMITADO"}
    except Exception as e:
        print("ERROR CONSUMIR:", e)
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/qr-scan")
async def qr_scan(request: Request):
    return {"success": True}

@app.get("/api/notificaciones/{correo}")
async def get_notificaciones(correo: str):
    try:
        res = supabase.table("notificaciones").select("*").order("fecha", desc=True).limit(20).execute()
        return {"data": res.data or []}
    except:
        return {"data": []}

@app.post("/api/notificaciones/leer/{id}")
async def leer_notif(id: int):
    return {"success": True}

@app.post("/api/registrar-comercio")
async def registrar_comercio(request: Request):
    try:
        body = await request.json()
        ins = supabase.table("comercios").insert(body).execute()
        return {"success": True, "data": ins.data}
    except Exception as e:
        print("ERROR COMERCIO:", e)
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/login-comercio")
async def login_comercio(request: Request):
    try:
        body = await request.json()
        res = supabase.table("comercios").select("*").eq("correo", body.get("correo")).eq("password", body.get("password")).execute()
        if res.data:
            return {"success": True, "comercio": res.data[0]}
        return JSONResponse({"success": False, "error":"Correo o clave comercio incorrectos"}, status_code=401)
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.post("/api/upload")
async def upload_file(request: Request):
    # Si no usas storage, devolvemos error controlado para que no crashee deploy
    return JSONResponse({"success": False, "error":"Upload no configurado, usa URL directa"}, status_code=400)

@app.post("/api/admin/login")
async def admin_login(request: Request):
    body = await request.json()
    if body.get("key") == ADMIN_KEY:
        return {"success": True}
    return JSONResponse({"success": False, "error":"Clave incorrecta"}, status_code=401)

@app.get("/api/admin/datos")
async def admin_datos(key: str):
    if key!= ADMIN_KEY:
        return JSONResponse({"success": False, "error":"No autorizado"}, status_code=401)
    try:
        comercios = supabase.table("comercios").select("*").order("id", desc=True).execute().data or []
        usuarios = supabase.table("usuarios").select("*").order("id", desc=True).execute().data or []
        try:
            acciones = supabase.table("acciones").select("*").order("fecha", desc=True).limit(200).execute().data or []
        except:
            acciones = []
        try:
            referidos = supabase.table("referidos").select("*").order("fecha", desc=True).limit(200).execute().data or []
        except:
            referidos = []
        total = sum([float(a.get("ahorro_aplicado") or 0) for a in acciones])
        return {"success": True, "comercios": comercios, "usuarios": usuarios, "acciones": acciones, "referidos": referidos, "total_ahorro": total}
    except Exception as e:
        print("ERROR ADMIN DATOS:", e)
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.post("/api/admin/broadcast")
async def admin_broadcast(request: Request):
    try:
        body = await request.json()
        if body.get("admin_key")!= ADMIN_KEY:
            return JSONResponse({"success": False, "error":"No autorizado"}, status_code=401)
        supabase.table("notificaciones").insert({
            "titulo": body.get("titulo"),
            "mensaje": body.get("mensaje"),
            "imagen_url": body.get("imagen_url"),
            "destino": body.get("destino","todos"),
            "fecha": datetime.utcnow().isoformat()
        }).execute()
        return {"success": True}
    except Exception as e:
        print("ERROR BROADCAST:", e)
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
