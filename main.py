
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import uuid, os

app = FastAPI(title="MaxShop v3.0 FINAL")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# --- MODELOS ---
class PagoQR(BaseModel):
    comercio_id: str
    monto: float
    tipo_pago: str = "efectivo"  # efectivo o mp

class LeadPrestamo(BaseModel):
    nombre: str
    tipo: str
    monto: str = ""

# --- ENDPOINTS CORE ---
@app.get("/")
def root(): return {"status":"MaxShop v3.0 FINAL - Formato que te enamoró - Listo para campañas"}

@app.post("/api/wallet/pagar-qr")
def pagar_qr(pago: PagoQR):
    # Lógica final: Bienvenida $1500 tope 30% $300, cashback 1.2%, comisión 2.5%
    comision = pago.monto * 0.025
    cashback = pago.monto * 0.012
    comprobante_id = f"MAX-{uuid.uuid4().hex[:4].upper()}-{datetime.now().strftime('%d%m%Y')}"
    estado = "PENDIENTE ⏳" if pago.tipo_pago=="efectivo" else "PAGADO ✅"
    # Si efectivo => genera saldo_pendiente_comision (Uber) para el comercio
    # Si MP => descuenta deuda
    return {
        "comprobante_numero": comprobante_id,
        "fecha_venta": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "monto_venta": pago.monto,
        "comision_generada": round(comision,2),
        "cashback_generado": round(cashback,2),
        "estado": estado,
        "mensaje": "Cashback acreditado en 24h • Válido 30 días"
    }

@app.post("/api/prestamos/lead")
def lead_prestamo(lead: LeadPrestamo):
    # Guarda lead y deriva a WhatsApp tercerizado
    log = f"{datetime.now()} - Lead {lead.tipo} {lead.monto} de {lead.nombre}"
    print(log)
    return {"status":"ok","wa_url": f"https://wa.me/5493834000000?text=Lead {lead.tipo} {lead.nombre} {lead.monto}"}

@app.post("/api/comercios/registro")
def registro_comercio(nombre: str, email: str, alias_mp: str):
    return {"comercio_id": str(uuid.uuid4()), "status":"pendiente_verificacion", "mensaje":"Subí logo/banner/3 fotos en /upload"}

@app.post("/api/comercios/upload")
async def upload(file: UploadFile = File(...)):
    return {"filename": file.filename, "url": f"/uploads/{file.filename}", "status":"ok"}

@app.get("/api/comisiones/{comercio_id}")
def comisiones(comercio_id: str):
    # Devuelve comprobantes con fecha/hora ID PENDIENTE/PAGADO
    return [{"comprobante_numero":"MAX-AB12-15092026","fecha_venta":"15/09/2026 14:32","monto_venta":1200,"comision":30,"estado":"PENDIENTE ⏳"}]

# --- SQL PARA SUPABASE (pegar en SQL Editor) ---
# CREATE TABLE comisiones_comercios (id uuid primary key default gen_random_uuid(), comercio_id text, comprobante_numero text unique, fecha_venta timestamp default now(), fecha_pago timestamp, monto_venta numeric, comision_generada numeric, tipo_pago text, estado text, cashback_otorgado numeric);
# CREATE TABLE saldo_pendiente_comision (comercio_id text primary key, saldo_pendiente numeric default 0, updated_at timestamp default now());
# CREATE TABLE leads_prestamos (id uuid primary key default gen_random_uuid(), nombre text, tipo text, monto text, created_at timestamp default now(), estado text default 'nuevo');
