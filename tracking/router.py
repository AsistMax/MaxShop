from fastapi import APIRouter
from pydantic import BaseModel
import os

router = APIRouter(prefix="/tracking", tags=["tracking-real"])

try:
    from supabase import create_client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_KEY")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
except:
    supabase = None

class Ping(BaseModel):
    envio_id: str
    cadete_id: str
    lat: float
    lng: float

class Estado(BaseModel):
    envio_id: str
    estado: str
    cadete_id: str = "anon"
    lat: float = None
    lng: float = None

@router.post("/ping")
def ping(p: Ping):
    if not supabase:
        return {"ok": False, "error": "supabase no configurado"}
    supabase.table("tracking_envios").insert(p.model_dump()).execute()
    return {"ok": True, "bot": "24/7 control total"}

@router.post("/estado")
def estado(e: Estado):
    if not supabase:
        return {"ok": False}
    supabase.table("estados_envio").insert({
        "envio_id": e.envio_id,
        "estado": e.estado,
        "cadete_id": e.cadete_id,
        "lat": e.lat,
        "lng": e.lng
    }).execute()
    if e.estado == "completado":
        print(f"SPLIT COBRAR: {e.envio_id}")
    return {"ok": True}

@router.get("/ruta/{envio_id}")
def ruta(envio_id: str):
    if not supabase:
        return {"puntos": [], "estados": []}
    puntos = supabase.table("tracking_envios").select("*").eq("envio_id", envio_id).order("created_at").execute()
    estados = supabase.table("estados_envio").select("*").eq("envio_id", envio_id).order("created_at").execute()
    return {"puntos": puntos.data, "estados": estados.data}
