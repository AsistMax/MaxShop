from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
import os, uuid

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=True)
templates = Jinja2Templates(directory="templates")
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1]
    name = f"{uuid.uuid4()}.{ext}"
    content = await file.read()
    supabase.storage.from_("comercios").upload(name, content, {"content-type": file.content_type})
    url = supabase.storage.from_("comercios").get_public_url(name)
    return {"url": url}

@app.get("/api/comercios")
def get_comercios():
    r = supabase.table("comercios").select("*").order("id", desc=True).execute()
    return {"success": True, "data": r.data}

@app.get("/api/usuario/{correo}")
def get_usuario(correo: str):
    r = supabase.table("usuarios").select("*").eq("correo", correo).single().execute()
    if not r.data: return JSONResponse({"success": False}, status_code=404)
    u=r.data; u['es_pro']=u.get('es_pro') or u.get('suscripcion_activa') or False
    u['credito_descuento_disponible']=u.get('credito_descuento_disponible') or u.get('credito_descuento_total') or 0
    return {"success": True, "data": u}

@app.post("/api/registro")
async def registro(req: Request):
    d=await req.json()
    ex=supabase.table("usuarios").select("*").eq("correo", d['correo']).execute()
    if ex.data: return JSONResponse({"success": False, "error": "Ya existe"}, status_code=400)
    nuevo={"nombre_completo":d['nombre_completo'],"dni":d['dni'],"direccion":d['direccion'],"localidad":d['localidad'],"whatsapp":d['whatsapp'],"correo":d['correo'],"password":d['password'],"es_pro":False,"credito_descuento_disponible":50000,"credito_descuento_total":50000,"suscripcion_activa":False}
    r=supabase.table("usuarios").insert(nuevo).execute()
    return {"success": True}

@app.post("/api/login")
async def login(req: Request):
    d=await req.json()
    r=supabase.table("usuarios").select("*").eq("correo", d['correo']).eq("password", d['password']).single().execute()
    if not r.data: return JSONResponse({"success": False}, status_code=401)
    return {"success": True, "usuario": r.data}

@app.post("/api/registrar-comercio")
async def reg_com(req: Request):
    d=await req.json()
    r=supabase.table("comercios").insert(d).execute()
    return {"success": True}

@app.post("/api/consumir-credito")
async def consumir(req: Request):
    d=await req.json()
    usu=supabase.table("usuarios").select("*").eq("correo", d['correo_usuario']).single().execute()
    com=supabase.table("comercios").select("*").eq("nombre_fantasias", d['nombre_comercio']).single().execute()
    monto=float(d['monto_compra']); pct=float(com.data['porcentaje_descuento'])
    is_pro=usu.data.get('es_pro') or usu.data.get('suscripcion_activa')
    if not is_pro: pct=pct*0.5
    ahorro=monto*(pct/100); disp=float(usu.data.get('credito_descuento_disponible') or usu.data.get('credito_descuento_total') or 0)
    if ahorro>disp: ahorro=disp
    nuevo=disp-ahorro
    supabase.table("usuarios").update({"credito_descuento_disponible":nuevo,"credito_descuento_total":nuevo}).eq("correo", d['correo_usuario']).execute()
    try: supabase.table("acciones_log").insert({"correo_usuario":d['correo_usuario'],"nombre_comercio":d['nombre_comercio'],"monto_compra":monto,"ahorro_aplicado":ahorro}).execute()
    except: pass
    return {"success": True, "ahorro_aplicado": ahorro, "nuevo_credito": nuevo}

@app.get("/api/admin/datos")
def admin():
    rc=supabase.table("comercios").select("*").order("id", desc=True).execute()
    ru=supabase.table("usuarios").select("*").order("id", desc=True).execute()
    ra=supabase.table("acciones_log").select("*").order("id", desc=True).limit(100).execute()
    users=[]
    for u in (ru.data or []):
        u['es_pro']=u.get('es_pro') or u.get('suscripcion_activa') or False
        u['credito_descuento_disponible']=u.get('credito_descuento_disponible') or u.get('credito_descuento_total') or 0
        users.append(u)
    return {"success": True, "comercios": rc.data, "usuarios": users, "acciones": ra.data}
