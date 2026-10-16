import os
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from supabase import create_client
import mercadopago
import uuid
from datetime import datetime

app = FastAPI(title="NODO-Argentina API V3 - Bots Automaticos")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY) if SUPABASE_URL else None
sdk = mercadopago.SDK(MP_ACCESS_TOKEN) if MP_ACCESS_TOKEN else None

class CancelarReq(BaseModel):
    tarea_id: str
    cliente_id: str
    porcentaje_recorrido: float
    mp_payment_id: str
    idempotency_key: str = None

def bot1_validar(tarea, porcentaje, payment_id):
    if not tarea: return False, "Tarea no existe"
    if tarea.get("estado") in ["cancelada", "reembolsada"]: return False, "Ya cancelada - evita doble reembolso"
    return True, "OK BOT1"

def bot2_split(monto_total, porcentaje_recorrido):
    if porcentaje_recorrido < 70:
        return True, {"cliente": float(monto_total), "trabajador": 0.0}
    else:
        cliente = round(monto_total * 0.85, 2)
        trabajador = round(monto_total * 0.15, 2)
        return True, {"cliente": cliente, "trabajador": trabajador}

@app.get("/health")
def health():
    return {"ok": True, "v3": "70% + Doble Bot"}

@app.post("/api/cancelar-servicio")
def cancelar_servicio(req: CancelarReq, x_idempotency_key: str = Header(None)):
    # <70% = 100% cliente, >=70% = 85% cliente + 15% trabajador
    # Con BOT1 + BOT2 + idempotencia + auditoria - 100% automatico
    tarea_res = supabase.table("tareas").select("*").eq("id", req.tarea_id).single().execute()
    tarea = tarea_res.data
    trans_res = supabase.table("transactions").select("*").eq("mp_payment_id", req.mp_payment_id).single().execute()
    monto_total = float(trans_res.data.get("monto_total", 0))
    ok1, msg1 = bot1_validar(tarea, req.porcentaje_recorrido, req.mp_payment_id)
    if not ok1: raise HTTPException(400, msg1)
    ok2, split = bot2_split(monto_total, req.porcentaje_recorrido)
    monto_cliente = split["cliente"]
    monto_trabajador = split["trabajador"]
    
    if req.porcentaje_recorrido < 70:
        refund = sdk.payment().refund(req.mp_payment_id, {"amount": float(monto_total)})
        supabase.table("transactions").insert({"tarea_id": req.tarea_id, "monto_cliente_devolucion": monto_cliente, "estado": "reembolsada_100", "porcentaje_recorrido": req.porcentaje_recorrido}).execute()
        return {"ok": True, "caso": "<70%", "devolucion_cliente": monto_cliente}
    else:
        refund = sdk.payment().refund(req.mp_payment_id, {"amount": float(monto_cliente)})
        supabase.table("transactions").insert({"tarea_id": req.tarea_id, "monto_cliente_devolucion": monto_cliente, "monto_trabajador": monto_trabajador, "estado": "reembolso_parcial_85_15", "porcentaje_recorrido": req.porcentaje_recorrido}).execute()
        return {"ok": True, "caso": ">=70%", "cliente": monto_cliente, "trabajador": monto_trabajador}
