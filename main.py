from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os, uuid, random
from datetime import datetime, date

app = FastAPI(title="MaxShop V2.1 Final")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
templates = Jinja2Templates(directory="templates")
ADMIN_KEY = os.getenv("ADMIN_KEY", "MaxShop2026!Admin")
CREDITO_INICIAL = 20000

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

def gen_codigo(nombre, dni):
    base = (nombre[:4] if nombre else "USER").upper().replace(" ","")
    return f"{base}{dni[-3:] if dni else str(random.randint(100,999))}{random.choice('XYZ')}{random.randint(10,99)}"

@app.post("/api/registro")
async def registro(req: Request):
    try:
        sb = get_supabase()
        d = await req.json()
        ex = sb.table("usuarios").select("id").eq("correo", d['correo']).execute()
        if ex.data: return JSONResponse({"success": False, "error":"Correo ya existe", "code":"EXISTE"},400)
        codigo = gen_codigo(d.get('nombre_completo',''), d.get('dni',''))
        nuevo = {"nombre_completo": d.get('nombre_completo',''), "dni": d.get('dni',''), "direccion": d.get('direccion',''), "localidad": d.get('localidad',''), "whatsapp": d.get('whatsapp',''), "correo": d['correo'], "password": d['password'], "es_pro": False, "credito_descuento_disponible": CREDITO_INICIAL, "credito_descuento_total": CREDITO_INICIAL, "credito_ilimitado": False, "suscripcion_activa": False, "fecha_registro": datetime.now().isoformat(), "codigo_referido": codigo, "maxcoins": 0, "racha_dias": 0, "ultima_ruleta": None}
        sb.table("usuarios").insert(nuevo).execute()
        if d.get('codigo_referido_usado'):
            try:
                inv = sb.table("usuarios").select("*").eq("codigo_referido", d['codigo_referido_usado']).single().execute()
                if inv.data and inv.data['correo']!= d['correo']:
                    sb.table("referidos").insert({"codigo_mio": d['codigo_referido_usado'], "correo_invitado": d['correo'], "correo_invitador": inv.data['correo'], "validado": False, "fecha": datetime.now().isoformat()}).execute()
            except: pass
        try: sb.table("notificaciones").insert({"correo_destino": d['correo'], "titulo": "¡Bienvenido a MaxShop! 🎉", "mensaje": f"Hola! Tenés {CREDITO_INICIAL} crédito gratis. Gira la ruleta diaria, junta 100 MaxCoins (10 compras) = 1 giro extra. ¡Tu código referido es {codigo}!", "fecha": datetime.now().isoformat(), "leida": False}).execute()
        except: pass
        return {"success": True, "usuario": nuevo}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)},500)

@app.post("/api/registro-pro-existente")
async def registro_pro_existente(req: Request):
    try:
        sb = get_supabase()
        d = await req.json()
        u = sb.table("usuarios").select("*").eq("correo", d['correo']).single().execute()
        if not u.data:
            codigo = gen_codigo(d.get('nombre_completo',''), d.get('dni',''))
            nuevo = {"nombre_completo": d.get('nombre_completo',''), "dni": d.get('dni',''), "direccion": d.get('direccion',''), "localidad": d.get('localidad',''), "whatsapp": d.get('whatsapp',''), "correo": d['correo'], "password": d['password'], "es_pro": False, "credito_descuento_disponible": CREDITO_INICIAL, "credito_descuento_total": CREDITO_INICIAL, "credito_ilimitado": False, "suscripcion_activa": False, "fecha_registro": datetime.now().isoformat(), "codigo_referido": codigo, "maxcoins": 0, "racha_dias": 0, "ultima_ruleta": None}
            sb.table("usuarios").insert(nuevo).execute()
        return {"success": True}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)},500)

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
    if not r.data: return JSONResponse({"success": False, "error":"Credenciales"},401)
    return {"success": True, "comercio": r.data}

@app.post("/api/registrar-comercio")
async def reg_com(req: Request):
    sb = get_supabase(); d = await req.json()
    pct = float(d.get('porcentaje_descuento') or 5)
    if pct < 5: return JSONResponse({"success": False, "error":"Minimo 5%"},400)
    d['fecha_alta'] = datetime.now().isoformat(); d['bloqueado_edicion'] = True
    r = sb.table("comercios").insert(d).execute()
    return {"success": True, "data": r.data}

@app.post("/api/crear-pago-recarga")
async def crear_pago_recarga(req: Request):
    d = await req.json(); mp = get_mp()
    if not mp: return JSONResponse({"success": False, "error":"Falta MP_ACCESS_TOKEN"},500)
    pref = {"items": [{"title":"Girar Ruleta MaxShop $500 - Premios 1500 a 8000 credito","quantity":1,"unit_price":500,"currency_id":"ARS"}],"payer": {"email": d['correo']},"external_reference": f"ruleta_paga_{d['correo']}_{uuid.uuid4()}","back_urls": {"success": f"{os.getenv('BASE_URL','')}/?pago=ruleta_ok","failure": f"{os.getenv('BASE_URL','')}/?pago=fail","pending": f"{os.getenv('BASE_URL','')}/?pago=pending"},"auto_return": "approved"}
    res = mp.preference().create(pref)
    return {"success": True, "init_point": res["response"]["init_point"]}

@app.post("/api/crear-pago-pro")
async def crear_pago_pro(req: Request):
    d = await req.json(); mp = get_mp()
    if not mp: return JSONResponse({"success": False, "error":"Falta MP_ACCESS_TOKEN"},500)
    pref = {"items": [{"title":"MaxShop PRO 5000 - Credito ilimitado","quantity":1,"unit_price":5000,"currency_id":"ARS"}],"payer": {"email": d['correo']},"external_reference": f"pro_{d['correo']}_{uuid.uuid4()}","back_urls": {"success": f"{os.getenv('BASE_URL','')}/?pro=ok","failure": f"{os.getenv('BASE_URL','')}/?pro=fail","pending": f"{os.getenv('BASE_URL','')}/?pro=pending"},"auto_return": "approved"}
    res = mp.preference().create(pref)
    return {"success": True, "init_point": res["response"]["init_point"]}

@app.post("/api/consumir-credito")
async def consumir(req: Request):
    sb = get_supabase(); d = await req.json()
    usu = sb.table("usuarios").select("*").eq("correo", d['correo_usuario']).single().execute()
    com = sb.table("comercios").select("*").eq("nombre_fantasias", d['nombre_comercio']).single().execute()
    if not usu.data or not com.data: return JSONResponse({"success": False, "error":"No encontrado"},404)
    monto = float(d['monto_compra']); pct_com = float(com.data.get('porcentaje_descuento') or 5)
    es_pro = usu.data.get('es_pro') or usu.data.get('credito_ilimitado')
    pct_real = pct_com if es_pro else pct_com*0.5; ahorro = monto*(pct_real/100)
    if es_pro and usu.data.get('credito_ilimitado'): nuevo = "ILIMITADO"
    else:
        disp = float(usu.data.get('credito_descuento_disponible') or 0)
        if ahorro>disp: ahorro=disp
        nuevo = disp-ahorro
        sb.table("usuarios").update({"credito_descuento_disponible": nuevo, "maxcoins": int(usu.data.get('maxcoins') or 0)+10}).eq("correo", d['correo_usuario']).execute()
    try: sb.table("acciones_log").insert({"correo_usuario": d['correo_usuario'], "nombre_comercio": d['nombre_comercio'], "monto_compra": monto, "ahorro_aplicado": ahorro, "porcentaje_aplicado": pct_real, "fecha": datetime.now().isoformat()}).execute()
    except: pass
    try:
        ref = sb.table("referidos").select("*").eq("correo_invitado", d['correo_usuario']).eq("validado", False).execute()
        if ref.data:
            for r in ref.data:
                sb.table("referidos").update({"validado": True}).eq("id", r['id']).execute()
                inv = sb.table("usuarios").select("*").eq("correo", r['correo_invitador']).single().execute()
                if inv.data and not inv.data.get('credito_ilimitado'):
                    sb.table("usuarios").update({"credito_descuento_disponible": float(inv.data.get('credito_descuento_disponible') or 0)+10000, "maxcoins": int(inv.data.get('maxcoins') or 0)+50}).eq("correo", r['correo_invitador']).execute()
                sb.table("notificaciones").insert({"correo_destino": r['correo_invitador'], "titulo": "¡Referido validado! 🎉", "mensaje": f"Tu invitado {d['correo_usuario']} hizo su primera compra. Ganaste 10000 crédito + 50 MaxCoins!", "fecha": datetime.now().isoformat(), "leida": False}).execute()
    except: pass
    return {"success": True, "ahorro_aplicado": ahorro, "porcentaje_aplicado": pct_real, "nuevo_credito": nuevo, "es_pro": bool(es_pro), "maxcoins_ganados": 10}

@app.post("/api/qr-scan")
async def qr_scan(req: Request):
    sb = get_supabase(); d = await req.json()
    try: sb.table("qr_scans").insert({"comercio_id": d.get('comercio_id'),"nombre_comercio": d.get('nombre_comercio'),"correo_usuario": d.get('correo_usuario'),"fecha": datetime.now().isoformat()}).execute()
    except: pass
    return {"success": True}

@app.post("/api/ruleta/girar")
async def ruleta(req: Request):
    sb = get_supabase(); d = await req.json()
    usu = sb.table("usuarios").select("*").eq("correo", d['correo']).single().execute()
    if not usu.data: return JSONResponse({"success": False, "error":"Usuario no encontrado"},404)
    hoy = str(date.today())
    ultima = usu.data.get('ultima_ruleta')
    if ultima and str(ultima)[:10] == hoy:
        return JSONResponse({"success": False, "error":"Ya giraste hoy, vuelve mañana. O canjea 100 MaxCoins por 1 giro extra"},400)
    premios = [500][800][1000][1500][2000][3000]
    premio = random.choice(premios)
    es_pro = usu.data.get('credito_ilimitado') or usu.data.get('es_pro')
    racha = int(usu.data.get('racha_dias') or 0) + 1
    try:
        from datetime import timedelta
        ayer = str(date.today() - timedelta(days=1))
        if not (ultima and str(ultima)[:10] == ayer):
            if ultima and str(ultima)[:10]!= hoy: racha = 1
    except: racha = 1
    if not es_pro:
        sb.table("usuarios").update({"credito_descuento_disponible": float(usu.data.get('credito_descuento_disponible') or 0)+premio, "ultima_ruleta": datetime.now().isoformat(), "racha_dias": racha, "maxcoins": int(usu.data.get('maxcoins') or 0)+5}).eq("correo", d['correo']).execute()
    else:
        sb.table("usuarios").update({"ultima_ruleta": datetime.now().isoformat(), "racha_dias": racha, "maxcoins": int(usu.data.get('maxcoins') or 0)+5}).eq("correo", d['correo']).execute()
    bonus = 3000 if racha % 7 == 0 else 0
    if bonus and not es_pro:
        sb.table("usuarios").update({"credito_descuento_disponible": float(usu.data.get('credito_descuento_disponible') or 0)+premio+bonus}).eq("correo", d['correo']).execute()
    return {"success": True, "premio": premio, "racha": racha, "bonus_racha": bonus, "tipo": "gratis"}

@app.post("/api/ruleta/canjear")
async def canjear(req: Request):
    sb = get_supabase(); d = await req.json()
    usu = sb.table("usuarios").select("*").eq("correo", d['correo']).single().execute()
    if not usu.data: return JSONResponse({"success": False, "error":"Usuario no encontrado"},404)
    mc = int(usu.data.get('maxcoins') or 0)
    if mc < 100: return JSONResponse({"success": False, "error":"Necesitas 100 MaxCoins = 10 compras. Tenés "+str(mc)},400)
    premio = random.choice([1000][1500][2000][2500][3000][4000])
    es_pro = usu.data.get('credito_ilimitado') or usu.data.get('es_pro')
    if not es_pro:
        sb.table("usuarios").update({"credito_descuento_disponible": float(usu.data.get('credito_descuento_disponible') or 0)+premio, "maxcoins": mc-100}).eq("correo", d['correo']).execute()
    else:
        sb.table("usuarios").update({"maxcoins": mc-100}).eq("correo", d['correo']).execute()
    return {"success": True, "premio": premio, "tipo": "canje"}

@app.post("/api/ruleta/girar-paga")
async def girar_paga(req: Request):
    sb = get_supabase(); d = await req.json()
    usu = sb.table("usuarios").select("*").eq("correo", d['correo']).single().execute()
    if not usu.data: return JSONResponse({"success": False, "error":"Usuario no encontrado"},404)
    premio = random.choice([1500][2000][3000][4000][5000][8000])
    es_pro = usu.data.get('credito_ilimitado') or usu.data.get('es_pro')
    if not es_pro:
        sb.table("usuarios").update({"credito_descuento_disponible": float(usu.data.get('credito_descuento_disponible') or 0)+premio}).eq("correo", d['correo']).execute()
    return {"success": True, "premio": premio, "tipo": "paga_500"}

@app.get("/api/notificaciones/{correo}")
def get_notifs(correo: str):
    sb = get_supabase()
    try:
        r = sb.table("notificaciones").select("*").or_(f"correo_destino.eq.{correo},correo_destino.is.null").order("fecha", desc=True).limit(50).execute()
        return {"success": True, "data": r.data or []}
    except: return {"success": True, "data": []}

@app.post("/api/notificaciones/leer/{id}")
def leer_notif(id: int):
    try: get_supabase().table("notificaciones").update({"leida": True}).eq("id", id).execute()
    except: pass
    return {"success": True}

@app.post("/api/admin/broadcast")
async def broadcast(req: Request):
    d = await req.json()
    if d.get('admin_key')!= ADMIN_KEY: return JSONResponse({"success": False},401)
    sb = get_supabase()
    titulo = d.get('titulo','Noticia MaxShop'); mensaje = d.get('mensaje',''); imagen = d.get('imagen_url',''); destino = d.get('destino','todos')
    try:
        if destino == 'todos':
            sb.table("notificaciones").insert({"correo_destino": None, "titulo": titulo, "mensaje": mensaje, "imagen_url": imagen, "fecha": datetime.now().isoformat(), "leida": False}).execute()
        else:
            ru = sb.table("usuarios").select("correo,es_pro,credito_ilimitado").execute()
            for u in ru.data or []:
                es_pro = u.get('es_pro') or u.get('credito_ilimitado')
                if destino == 'pro' and not es_pro: continue
                if destino == 'gratis' and es_pro: continue
                sb.table("notificaciones").insert({"correo_destino": u['correo'], "titulo": titulo, "mensaje": mensaje, "imagen_url": imagen, "fecha": datetime.now().isoformat(), "leida": False}).execute()
        return {"success": True}
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)},500)

@app.post("/api/admin/login")
async def admin_login(req: Request):
    d = await req.json()
    if d.get('key')!= ADMIN_KEY: return JSONResponse({"success": False},401)
    return {"success": True}

@app.get("/api/admin/datos")
def admin_datos(key: str = ""):
    if key!= ADMIN_KEY: return JSONResponse({"success": False},401)
    sb = get_supabase()
    rc = sb.table("comercios").select("*").order("id", desc=True).execute()
    ru = sb.table("usuarios").select("*").order("id", desc=True).execute()
    try: ra = sb.table("acciones_log").select("*").order("id", desc=True).limit(1000).execute(); acc = ra.data or []
    except: acc=[]
    try: rr = sb.table("referidos").select("*").order("id", desc=True).limit(500).execute(); refs = rr.data or []
    except: refs=[]
    total_ahorro = sum([float(a.get('ahorro_aplicado') or 0) for a in acc])
    return {"success": True, "comercios": rc.data or [], "usuarios": ru.data or [], "acciones": acc, "referidos": refs, "total_ahorro": total_ahorro}
