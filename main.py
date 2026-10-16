import os, io, base64, qrcode, uuid
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from supabase import create_client
import mercadopago

app = FastAPI(title="NODO-Argentina API", version="3.1 QR UNICO")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY")
MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN")
supabase = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY) if SUPABASE_URL and SUPABASE_SECRET_KEY else None
sdk = mercadopago.SDK(MP_ACCESS_TOKEN) if MP_ACCESS_TOKEN else None

class CancelarReq(BaseModel):
    tarea_id: str; cliente_id: str; porcentaje_recorrido: float; mp_payment_id: str; idempotency_key: str = None
class SolicitarReq(BaseModel):
    tarea_id: str; cliente_id: str; monto: float; token_tarjeta: str
class PagarServicioReq(BaseModel):
    tarea_id: str; cliente_id: str; metodo_pago: str; token_tarjeta: str = None
class PagarQRReq(BaseModel):
    comercio_id: str; cliente_id: str; monto_real: float; csb_a_usar: float = 0
class ComprarCSBReq(BaseModel):
    cliente_id: str; cantidad_csb: float
class GenerarQRReq(BaseModel):
    comercio_id: str

def bot1_validar(tarea, porcentaje, payment_id):
    if not tarea: return False, "Tarea no existe"
    if tarea.get("estado") in ["cancelada", "reembolsada", "cancelada_reembolsada_100", "cancelada_reembolso_85_15"]:
        return False, f"Ya cancelada {tarea.get('estado')}"
    return True, "OK BOT1"
def bot2_split(monto_total, porcentaje_recorrido):
    if porcentaje_recorrido < 70: return True, {"cliente": float(monto_total), "trabajador": 0.0}
    else:
        cliente = round(monto_total * 0.85, 2); trabajador = round(monto_total * 0.15, 2)
        return True, {"cliente": cliente, "trabajador": trabajador}

@app.get("/")
def root():
    return {"nodo-api": "Live V3.1 QR UNICO + BOTS", "base_url_acordada": "https://maxshop-api.onrender.com", "version_diseno": "642d635032ce", "status": "OK"}

@app.get("/health")
def health():
    return {"ok": True, "v3.1": "QR + Bots", "supabase": bool(supabase), "mp": bool(sdk)}

@app.post("/api/solicitar-servicio-pago-anticipado")
def solicitar_servicio(req: SolicitarReq):
    payment_data = {"transaction_amount": float(req.monto), "token": req.token_tarjeta, "description": f"NODO+ {req.tarea_id[:8]}", "payer": {"email": f"{req.cliente_id}@nodo.com.ar"}}
    resp = sdk.payment().create(payment_data); payment = resp.get("response", {})
    if payment.get("status") != "approved": raise HTTPException(400, "Pago no aprobado")
    idem = str(uuid.uuid4())
    supabase.table("transactions").insert({"tarea_id": req.tarea_id, "cliente_id": req.cliente_id, "monto_total": req.monto, "mp_payment_id": str(payment.get("id")), "idempotency_key": idem, "estado": "pago_anticipado_en_cuenta_admin"}).execute()
    supabase.table("tareas").update({"estado": "pagada_esperando_trabajador"}).eq("id", req.tarea_id).execute()
    return {"ok": True, "mp_payment_id": payment.get("id"), "monto": req.monto, "idempotency_key": idem}

@app.post("/api/cancelar-servicio")
def cancelar_servicio(req: CancelarReq, x_idempotency_key: str = Header(None)):
    tarea_res = supabase.table("tareas").select("*").eq("id", req.tarea_id).single().execute(); tarea = tarea_res.data
    trans_res = supabase.table("transactions").select("*").eq("mp_payment_id", req.mp_payment_id).single().execute(); monto_total = float(trans_res.data.get("monto_total", 0))
    ok1, msg1 = bot1_validar(tarea, req.porcentaje_recorrido, req.mp_payment_id)
    if not ok1: raise HTTPException(400, msg1)
    ok2, split = bot2_split(monto_total, req.porcentaje_recorrido); monto_cliente = split["cliente"]; monto_trabajador = split["trabajador"]
    idem_cancel = req.idempotency_key or str(uuid.uuid4())
    if req.porcentaje_recorrido < 70:
        sdk.payment().refund(req.mp_payment_id, {"amount": float(monto_total)})
        supabase.table("transactions").insert({"tarea_id": req.tarea_id, "monto_cliente_devolucion": monto_cliente, "estado": "reembolsada_100", "idempotency_key": idem_cancel}).execute()
        return {"ok": True, "caso": f"<70% ({req.porcentaje_recorrido}%)", "devolucion_cliente": monto_cliente}
    else:
        sdk.payment().refund(req.mp_payment_id, {"amount": float(monto_cliente)})
        supabase.table("transactions").insert({"tarea_id": req.tarea_id, "monto_cliente_devolucion": monto_cliente, "monto_trabajador": monto_trabajador, "estado": "reembolso_parcial_85_15", "idempotency_key": idem_cancel}).execute()
        return {"ok": True, "caso": f">=70% ({req.porcentaje_recorrido}%)", "cliente": monto_cliente, "trabajador": monto_trabajador}

@app.post("/api/pagar-servicio")
def pagar_servicio_uber(req: PagarServicioReq):
    tarea_res = supabase.table("tareas").select("*").eq("id", req.tarea_id).single().execute(); tarea = tarea_res.data; monto = float(tarea.get("presupuesto", 0)); trabajador_id = tarea.get("trabajador_id")
    try:
        pendientes = supabase.table("transactions").select("monto_comision").eq("trabajador_id", trabajador_id).eq("estado", "saldo_pendiente_comision").execute()
        saldo_previo = sum([float(t.get("monto_comision",0)) for t in pendientes.data]) if pendientes.data else 0
    except: saldo_previo = 0
    comision_actual = round(monto * 0.12, 2)
    if req.metodo_pago == "efectivo":
        supabase.table("transactions").insert({"tarea_id": req.tarea_id, "monto_comision": comision_actual, "estado": "saldo_pendiente_comision", "metodo_pago": "efectivo", "trabajador_id": trabajador_id}).execute()
        return {"ok": True, "tipo": "efectivo_uber", "pendiente": saldo_previo + comision_actual, "bloqueado": False}
    total_desc = saldo_previo + comision_actual; monto_trab = max(0, round(monto - total_desc, 2))
    payment_data = {"transaction_amount": float(monto), "token": req.token_tarjeta, "description": f"NODO+ {req.tarea_id[:8]}", "payer": {"email": f"{req.cliente_id}@nodo.com.ar"}, "application_fee": float(total_desc)}
    resp = sdk.payment().create(payment_data); payment = resp.get("response", {})
    if payment.get("status") != "approved": raise HTTPException(400, "Pago rechazado")
    supabase.table("transactions").insert({"tarea_id": req.tarea_id, "monto_trabajador": monto_trab, "mp_payment_id": str(payment.get("id")), "estado": "aprobado", "trabajador_id": trabajador_id}).execute()
    return {"ok": True, "monto_transferir": monto_trab}

@app.post("/api/generar-qr-unico-comercio")
def generar_qr_unico(req: GenerarQRReq):
    try:
        com_res = supabase.table("comercios").select("*").eq("id", req.comercio_id).single().execute()
        if com_res.data and com_res.data.get("qr_codigo_unico"):
            return {"ok": True, "mensaje": "Ya tiene QR", "qr_codigo_unico": com_res.data.get("qr_codigo_unico"), "qr_imagen_base64": com_res.data.get("qr_imagen_base64")}
    except: pass
    qr_codigo = f"NODO-{req.comercio_id[:8].upper()}-{str(uuid.uuid4())[:8].upper()}"
    qr_data = f"https://maxshop-api.onrender.com/qr/{req.comercio_id}?code={qr_codigo}"
    qr = qrcode.QRCode(box_size=10, border=4); qr.add_data(qr_data); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO(); img.save(buffered, format="PNG")
    img_base64 = f"data:image/png;base64,{base64.b64encode(buffered.getvalue()).decode()}"
    try: supabase.table("comercios").update({"qr_codigo_unico": qr_codigo, "qr_data": qr_data, "qr_imagen_base64": img_base64}).eq("id", req.comercio_id).execute()
    except: pass
    return {"ok": True, "qr_codigo_unico": qr_codigo, "qr_data": qr_data, "qr_imagen_base64": img_base64, "instrucciones": "Imprimir 10x10cm y pegar en caja"}

@app.get("/qr/{comercio_id}", response_class=HTMLResponse)
def qr_redirect(comercio_id: str, code: str = None):
    return HTMLResponse(f"<html><body><h1>NODO+ Comercio {comercio_id}</h1><p>QR {code}</p><p><a href='/scanner'>Scanner</a></p></body></html>")

@app.get("/scanner", response_class=HTMLResponse)
def scanner_page():
    return HTMLResponse("<html><head><script src='https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js'></script></head><body><div id='reader'></div><script>function onScanSuccess(t){window.location.href=t;} new Html5QrcodeScanner('reader',{fps:10,qrbox:250}).render(onScanSuccess);</script></body></html>")

@app.post("/api/pagar-qr")
def pagar_qr(req: PagarQRReq):
    return {"ok": True, "descuento": "20%", "csb_usado": req.csb_a_usar}

@app.post("/api/comprar-csb")
def comprar_csb(req: ComprarCSBReq):
    return {"ok": True, "csb": req.cantidad_csb}
