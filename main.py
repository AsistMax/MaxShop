import os
import random
import hashlib
from datetime import datetime
import bcrypt
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="MaxShop Billetera v2.0 - SuperApp")
templates = Jinja2Templates(directory="templates")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ADMIN_KEY = os.getenv("ADMIN_KEY", "maxshop2024")
BASE_URL = os.getenv("BASE_URL", "https://maxshop-api.onrender.com")
MP_TOKEN = os.getenv("MP_ACCESS_TOKEN", "")

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase conectado - Billetera activa")
    except Exception as e:
        print(f"Error Supabase: {e}")

def gen_codigo(correo: str):
    base = f"{correo}{random.randint(1000,9999)}{datetime.utcnow().isoformat()}"
    return hashlib.md5(base.encode()).hexdigest()[:6].upper()

def hash_password(pw: str):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def check_password(pw: str, hashed: str):
    try:
        return bcrypt.checkpw(pw.encode(), hashed.encode())
    except:
        # compatibilidad con passwords viejos en texto plano
        return pw == hashed

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

# ===== BILLETERA - NUEVOS ENDPOINTS =====
@app.get("/api/wallet/saldo/{correo}")
async def wallet_saldo(correo: str):
    try:
        correo = correo.lower().strip()
        res = supabase.table("wallets").select("*").eq("correo_usuario", correo).execute()
        if res.data:
            return {"success": True, "wallet": res.data[0]}
        # crear si no existe
        u = supabase.table("usuarios").select("credito_descuento_disponible").eq("correo", correo).execute()
        credito = float(u.data[0].get("credito_descuento_disponible") or 0) if u.data else 0
        ins = supabase.table("wallets").insert({"correo_usuario": correo, "saldo_cashback": credito, "saldo_pesos": 0}).execute()
        return {"success": True, "wallet": ins.data[0]}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/wallet/pagar-qr")
async def wallet_pagar_qr(request: Request):
    """El corazon de la billetera: paga con QR, genera cashback"""
    try:
        body = await request.json()
        correo = body.get("correo_usuario","").lower().strip()
        comercio_nombre = body.get("comercio_nombre","")
        monto_compra = float(body.get("monto_compra") or 0)
        
        # Obtener wallet y usuario
        w = supabase.table("wallets").select("*").eq("correo_usuario", correo).execute()
        u = supabase.table("usuarios").select("*").eq("correo", correo).execute()
        if not w.data or not u.data:
            return JSONResponse({"error":"Usuario no encontrado"}, status_code=404)
        
        wallet = w.data[0]
        usuario = u.data[0]
        es_pro = usuario.get("es_pro") or usuario.get("credito_ilimitado")
        
        # Buscar comercio para obtener % descuento y cashback
        com = supabase.table("comercios").select("*").ilike("nombre_fantasias", f"%{comercio_nombre}%").execute()
        porc_desc = float(com.data[0].get("porcentaje_descuento") or 10) if com.data else 10
        porc_cashback = float(com.data[0].get("cashback_porcentaje") or 5) if com.data else 5
        
        # Si es PRO, minimo 25% OFF
        if es_pro and porc_desc < 25:
            porc_desc = 25
            porc_cashback = 7
        
        ahorro = monto_compra * (porc_desc / 100)
        cashback_generado = monto_compra * (porc_cashback / 100)
        
        # Descontar ahorro del saldo cashback si no es ilimitado
        nuevo_saldo = float(wallet.get("saldo_cashback") or 0)
        if not es_pro:
            nuevo_saldo = max(0, nuevo_saldo - ahorro)
        nuevo_saldo += cashback_generado
        
        # Actualizar wallet
        supabase.table("wallets").update({"saldo_cashback": nuevo_saldo, "updated_at": datetime.utcnow().isoformat()}).eq("correo_usuario", correo).execute()
        # Actualizar usuarios por compatibilidad
        supabase.table("usuarios").update({"credito_descuento_disponible": nuevo_saldo}).eq("correo", correo).execute()
        
        # Log transaccion
        supabase.table("transacciones_wallet").insert({
            "correo_usuario": correo,
            "tipo": "pago_qr",
            "monto": ahorro,
            "monto_compra": monto_compra,
            "comercio_nombre": comercio_nombre,
            "cashback_generado": cashback_generado
        }).execute()
        
        try:
            supabase.table("acciones_log").insert({
                "correo_usuario": correo,
                "nombre_comercio": comercio_nombre,
                "monto_compra": monto_compra,
                "ahorro_aplicado": ahorro,
                "porcentaje_aplicado": porc_desc
            }).execute()
        except:
            pass
        
        return {
            "success": True,
            "ahorro_aplicado": ahorro,
            "porcentaje_descuento": porc_desc,
            "cashback_generado": cashback_generado,
            "nuevo_saldo": nuevo_saldo,
            "mensaje": f"Pagaste ${monto_compra} - Ahorraste ${ahorro} - Ganaste ${cashback_generado} cashback"
        }
    except Exception as e:
        print("ERROR PAGAR QR:", e)
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/map/comercios")
async def map_comercios():
    """Devuelve comercios con lat/lng para los puntitos del mapa"""
    try:
        if not supabase:
            return {"data": []}
        res = supabase.table("comercios").select("*").execute()
        data = []
        for c in (res.data or []):
            # Si no tiene lat/lng, asignar centro Catamarca con jitter para demo
            lat = c.get("latitud")
            lng = c.get("longitud")
            if not lat or not lng:
                lat = -28.4695 + random.uniform(-0.02, 0.02)
                lng = -65.7795 + random.uniform(-0.02, 0.02)
            data.append({
                "id": c.get("id"),
                "nombre": c.get("nombre_fantasias"),
                "rubro": c.get("rubro"),
                "direccion": c.get("direccion"),
                "descuento": c.get("porcentaje_descuento"),
                "cashback": c.get("cashback_porcentaje") or 5,
                "lat": lat,
                "lng": lng,
                "logo": c.get("logo_url"),
                "imagen": c.get("imagen_url")
            })
        return {"data": data}
    except Exception as e:
        return {"data": []}

# ===== ENDPOINTS EXISTENTES MEJORADOS =====
@app.get("/api/comercios")
async def get_comercios():
    try:
        if not supabase:
            return {"data": []}
        res = supabase.table("comercios").select("*").order("id", desc=True).execute()
        return {"data": res.data or []}
    except Exception as e:
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
        hashed = hash_password(body.get("password") or "123456")
        
        nuevo_usuario = {
            "nombre_completo": body.get("nombre_completo"),
            "dni": body.get("dni"),
            "direccion": body.get("direccion"),
            "localidad": body.get("localidad"),
            "whatsapp": body.get("whatsapp"),
            "correo": correo,
            "password": hashed,
            "credito_descuento_disponible": 20000,
            "codigo_referido": codigo,
            "codigo_referido_usado": body.get("codigo_referido_usado") or None,
            "maxcoins": 0,
            "racha_dias": 0,
            "es_pro": False,
            "credito_ilimitado": False
        }
        
        if supabase:
            ins = supabase.table("usuarios").insert(nuevo_usuario).execute()
            usuario = ins.data[0] if ins.data else nuevo_usuario
            # crear wallet
            try:
                supabase.table("wallets").insert({"correo_usuario": correo, "saldo_cashback": 20000, "saldo_pesos": 0}).execute()
            except:
                pass
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
        
        res = supabase.table("usuarios").select("*").eq("correo", correo).execute()
        if not res.data:
            return JSONResponse({"success": False, "error":"Correo o clave incorrectos"}, status_code=401)
        
        usuario = res.data[0]
        stored = usuario.get("password") or ""
        if not check_password(password, stored):
            # intentar si es texto plano viejo y migrar
            if password != stored:
                return JSONResponse({"success": False, "error":"Correo o clave incorrectos"}, status_code=401)
            # migrar a hash
            try:
                supabase.table("usuarios").update({"password": hash_password(password)}).eq("correo", correo).execute()
            except:
                pass
        
        if not usuario.get("codigo_referido"):
            nuevo_codigo = gen_codigo(correo)
            try:
                supabase.table("usuarios").update({"codigo_referido": nuevo_codigo}).eq("correo", correo).execute()
                usuario["codigo_referido"] = nuevo_codigo
            except:
                usuario["codigo_referido"] = nuevo_codigo
        
        # asegurar wallet
        try:
            w = supabase.table("wallets").select("*").eq("correo_usuario", correo).execute()
            if not w.data:
                supabase.table("wallets").insert({"correo_usuario": correo, "saldo_cashback": usuario.get("credito_descuento_disponible") or 0}).execute()
        except:
            pass
        
        return {"success": True, "usuario": usuario}
    except Exception as e:
        print("ERROR LOGIN:", e)
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)

@app.post("/api/ruleta/girar")
async def girar_ruleta(request: Request):
    try:
        body = await request.json()
        correo = body.get("correo","").lower().strip()
        res = supabase.table("usuarios").select("*").eq("correo", correo).execute()
        if not res.data:
            return JSONResponse({"error":"Usuario no encontrado"}, status_code=404)
        usuario = res.data[0]
        ultima = usuario.get("ultima_ruleta")
        if ultima:
            try:
                ult = datetime.fromisoformat(str(ultima).replace("Z","").split(".")[0])
                if ult.date() == datetime.utcnow().date() and not (usuario.get("es_pro")):
                    return JSONResponse({"error":"Ya giraste hoy"}, status_code=400)
            except:
                pass
        
        # Nueva ruleta billetera: da cashback
        premio = random.choice([300, 500, 800, 1000, 1500, 2500])
        bonus_racha = 0
        racha = usuario.get("racha_dias") or 0
        if racha >= 6:
            bonus_racha = 3000
            racha = 0
        else:
            racha += 1
        
        # actualizar wallet
        w = supabase.table("wallets").select("*").eq("correo_usuario", correo).execute()
        saldo_actual = float(w.data[0].get("saldo_cashback") or 0) if w.data else 0
        nuevo_saldo = saldo_actual + premio + bonus_racha
        
        supabase.table("wallets").update({"saldo_cashback": nuevo_saldo}).eq("correo_usuario", correo).execute()
        supabase.table("usuarios").update({
            "credito_descuento_disponible": nuevo_saldo,
            "racha_dias": racha,
            "ultima_ruleta": datetime.utcnow().isoformat(),
            "maxcoins": (usuario.get("maxcoins") or 0) + 10
        }).eq("correo", correo).execute()
        
        supabase.table("transacciones_wallet").insert({
            "correo_usuario": correo,
            "tipo": "ruleta",
            "monto": premio + bonus_racha,
            "comercio_nombre": "Ruleta Diaria"
        }).execute()
        
        return {"success": True, "premio": premio + bonus_racha, "racha": racha, "nuevo_saldo": nuevo_saldo}
    except Exception as e:
        print("ERROR RULETA:", e)
        return JSONResponse({"error": str(e)}, status_code=500)

@app.post("/api/crear-pago-pro")
async def crear_pago_pro(request: Request):
    try:
        import mercadopago
        sdk = mercadopago.SDK(MP_TOKEN) if MP_TOKEN else None
        if not sdk:
            return JSONResponse({"error":"MP no configurado - usa alias Asistmax365 por ahora"}, status_code=500)
        body = await request.json()
        pref = {
            "items": [{"title": "MaxShop PRO Billetera $5000", "quantity": 1, "unit_price": 5000}],
            "payer": {"email": body.get("correo")},
            "back_urls": {"success": f"{BASE_URL}/?pago=pro_ok", "failure": f"{BASE_URL}/?pago=error", "pending": f"{BASE_URL}/"},
            "auto_return": "approved",
            "metadata": {"correo": body.get("correo"), "tipo": "pro_billetera"}
        }
        result = sdk.preference().create(pref)
        return {"init_point": result["response"]["init_point"]}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Resto de endpoints originales...
@app.post("/api/crear-pago-recarga")
async def crear_pago_recarga(request: Request):
    try:
        import mercadopago
        sdk = mercadopago.SDK(MP_TOKEN) if MP_TOKEN else None
        if not sdk:
            return JSONResponse({"error":"MP no configurado"}, status_code=500)
        body = await request.json()
        pref = {
            "items": [{"title": "Recarga Giros MaxShop $500", "quantity": 1, "unit_price": 500}],
            "payer": {"email": body.get("correo")},
            "back_urls": {"success": f"{BASE_URL}/?pago=ruleta_ok", "failure": f"{BASE_URL}/?pago=error", "pending": f"{BASE_URL}/"},
            "auto_return": "approved",
            "metadata": {"correo": body.get("correo"), "tipo": "ruleta_500"}
        }
        result = sdk.preference().create(pref)
        return {"init_point": result["response"]["init_point"]}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@app.get("/api/admin/datos")
async def admin_datos(key: str):
    if key != ADMIN_KEY:
        return JSONResponse({"success": False, "error":"No autorizado"}, status_code=401)
    try:
        comercios = supabase.table("comercios").select("*").order("id", desc=True).execute().data or []
        usuarios = supabase.table("usuarios").select("*").order("id", desc=True).execute().data or []
        wallets = supabase.table("wallets").select("*").order("saldo_cashback", desc=True).limit(100).execute().data or []
        trans = supabase.table("transacciones_wallet").select("*").order("fecha", desc=True).limit(200).execute().data or []
        return {"success": True, "comercios": comercios, "usuarios": usuarios, "wallets": wallets, "transacciones": trans}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)
