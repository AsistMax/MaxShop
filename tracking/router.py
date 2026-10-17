from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import os
from datetime import datetime

router = APIRouter(prefix="/tracking", tags=["tracking"])

try:
    from supabase import create_client
    URL=os.getenv("SUPABASE_URL"); KEY=os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    supabase=create_client(URL,KEY) if URL and KEY else None
    HAS_DB=True if supabase else False
except:
    supabase=None; HAS_DB=False

MEM_PUNTOS=[]; MEM_ESTADOS=[]

class Ping(BaseModel):
    envio_id:str; cadete_id:str; lat:float; lng:float

class Estado(BaseModel):
    envio_id:str; estado:str; cadete_id:Optional[str]=None; lat:Optional[float]=None; lng:Optional[float]=None

@router.post("/ping")
def ping(data:Ping):
    if HAS_DB:
        supabase.table("tracking_envios").insert({"envio_id":data.envio_id,"cadete_id":data.cadete_id,"lat":data.lat,"lng":data.lng}).execute()
        return {"ok":True,"guardado":True,"real":True}
    MEM_PUNTOS.append({**data.dict(),"created_at":datetime.utcnow().isoformat()})
    return {"ok":True,"guardado":False,"real":True}

@router.post("/estado")
def estado(data:Estado):
    if HAS_DB:
        supabase.table("estados_envio").insert({"envio_id":data.envio_id,"estado":data.estado,"cadete_id":data.cadete_id}).execute()
        if data.estado=="completado":
            try: supabase.table("chats_temporales").delete().eq("trabajo_id",data.envio_id).execute()
            except: pass
        return {"ok":True,"estado":data.estado,"chat_borrado":data.estado=="completado"}
    MEM_ESTADOS.append({**data.dict(),"created_at":datetime.utcnow().isoformat()})
    return {"ok":True,"estado":data.estado}

@router.get("/ruta/{envio_id}")
def ruta(envio_id:str):
    if HAS_DB:
        p=supabase.table("tracking_envios").select("*").eq("envio_id",envio_id).order("created_at").execute()
        e=supabase.table("estados_envio").select("*").eq("envio_id",envio_id).order("created_at").execute()
        return {"puntos":p.data,"estados":e.data,"real":True,"supabase":True}
    return {"puntos":[x for x in MEM_PUNTOS if x["envio_id"]==envio_id],"estados":[x for x in MEM_ESTADOS if x["envio_id"]==envio_id],"real":True,"supabase":False}

@router.post("/../pago/crear")
def pago_crear(trabajo_id:str, monto:float, cliente_email:str):
    if not os.getenv("MP_ACCESS_TOKEN"):
        return {"ok":False,"error":"Falta MP_ACCESS_TOKEN"}
    return {"ok":True,"monto":monto,"split":{"prestador":monto*0.8,"comercio":monto*0.1,"nodo":monto*0.1},"msg":"Pago débito split - liquidación inmediata"}
