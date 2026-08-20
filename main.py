from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from supabase import create_client, Client

app = FastAPI(title="AsistMax-cobros API", version="1.0")

# Permitir que la interfaz web se comunique con este servidor (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Conexión a Supabase usando las credenciales seguras de Render
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    # Nota: En desarrollo local puedes poner tus credenciales directas aquí si gustas, 
    # pero en Render siempre deben ir en las "Environment Variables".
    supabase = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class TransaccionRequest(BaseModel):
    monto_bruto: float
    comercio_id: str
    cliente_id: str

@app.get("/")
def leer_raiz():
    return {
        "status": "online", 
        "servicio": "AsistMax-cobros API", 
        "mensaje": "Servidor funcionando al 100% y listo para operar."
    }

# Endpoint para que la app consulte las promociones activas desde Supabase
@app.get("/api/promociones")
def obtener_promociones():
    if not supabase:
        # Respuesta simulada por si aún no configuraste las variables en local
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

# Endpoint para registrar el inicio de un pago / cobro
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
        
        return {
            "success": True, 
            "mensaje": "Transacción registrada con éxito en el sistema",
            "data": resultado.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
