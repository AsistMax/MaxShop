from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
from supabase import create_client, Client

app = FastAPI(title="AsistMax-cobros", version="1.0")

# Permitir conexiones externas
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conectar archivos estáticos si existe la carpeta 'static'
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Conexión con Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    supabase = None

class TransaccionRequest(BaseModel):
    monto_bruto: float
    comercio_id: str
    cliente_id: str

# 1. RUTA PRINCIPAL: Muestra la interfaz gráfica (Billetera)
@app.get("/", response_class=HTMLResponse)
def mostrar_interfaz():
    # Si subiste el index.html dentro de la carpeta static/
    if os.path.exists("static/index.html"):
        return FileResponse("static/index.html")
    # Si subiste el index.html en la raíz del proyecto
    elif os.path.exists("index.html"):
        return FileResponse("index.html")
    else:
        return "<h1>AsistMax API Online</h1><p>Sube el archivo index.html para ver la billetera.</p>"

# 2. RUTAS DE API (Backend)
@app.get("/api/promociones")
def obtener_promociones():
    if not supabase:
        return {
            "success": True,
            "promociones": [
                {"id": 1, "comercio": "Comercio Adherido A", "beneficio": "20% OFF en caja"},
                {"id": 2, "comercio": "Red AsistMax", "beneficio": "Beneficio exclusivo digital"}
            ]
        }
    try:
        response = supabase.table("promociones").select("*").eq("activa", True).execute()
        return {"success": True, "promociones": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/procesar-cobro")
def procesar_cobro(datos: TransaccionRequest):
    if not supabase:
        raise HTTPException(status_code=500, detail="Base de datos no configurada.")
    try:
        nueva_transaccion = {
            "monto_bruto": datos.monto_bruto,
            "comercio_id": datos.comercio_id,
            "cliente_id": datos.cliente_id,
            "estado": "pendiente"
        }
        resultado = supabase.table("transacciones").insert(nueva_transaccion).execute()
        return {"success": True, "mensaje": "Transacción registrada", "data": resultado.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
