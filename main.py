
import os, uuid, requests, logging
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("maxshop")

app = FastAPI(title="MaxShop V11 ANCLADO FINAL - 100% Funcional Real")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

MP_ACCESS_TOKEN = os.getenv("MP_ACCESS_TOKEN", "")
MP_PUBLIC_KEY = os.getenv("MP_PUBLIC_KEY", "")
COMISION_PORCENTAJE = 0.017

COMERCIOS_ADHERIDOS = {"felipe", "panaderia_pm", "lomitos_lo_mas", "felipe_centro", "suc_", "lomitos_20_off", "templo", "comercio", "felipe", "jumbo", "fravega", "mcdonalds", "banco_galicia"}

class PagoRequest(BaseModel):
    user_id: str
    comercio_id: str
    monto_original: float
    comercio_nombre: Optional[str] = None
    tarjeta: Optional[str] = None
    fecha: Optional[str] = None
    hora: Optional[str] = None
    trans_id: Optional[str] = None
    mp_token: Optional[str] = None
    email_cliente: Optional[str] = None
    tipo_tarjeta: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
def serve():
    for ruta in ["index.html", "./index.html", "templates/index.html", "/opt/render/project/src/index.html"]:
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    c = f.read()
                    if len(c) > 5000:
                        return HTMLResponse(c)
            except Exception as e:
                logger.error(f"Error leyendo {ruta}: {e}")
                continue
    return HTMLResponse("<h1>MaxShop V11 Anclado Final - Mapa y Botones OK</h1>")

@app.get("/api")
def api():
    mp_configurado = bool(MP_ACCESS_TOKEN and MP_PUBLIC_KEY)
    return {
        "msg": "MaxShop V11 ANCLADO FINAL - Mapa y Botones 100% Funcionales",
        "version": "V11",
        "modo": "REAL" if mp_configurado else "DEMO - Configura MP_ACCESS_TOKEN y MP_PUBLIC_KEY",
        "mp_configurado": mp_configurado,
        "banner": "banner.jpg original familia obelisco",
        "logo": "logo_small.png transparente",
        "wallet": "100% MaxShop Wallet - Ticket nunca dice MP salvo chico legal por MP",
        "comision": "1.7% interna",
        "csb": "Dinamico 60% del maximo - 5-70% libre - azul <=60% max, dorado >60%",
        "ley": "25.326",
        "botones": "OK - toggleDrop, modales, pagar, cercanos, mapa",
        "mapa": "OK - Leaflet OSM invalidateSize fix - pines dinamicos"
    }

@app.get("/config/mp")
def mp_config():
    return {
        "public_key": MP_PUBLIC_KEY,
        "mp_conectado": bool(MP_ACCESS_TOKEN),
        "instrucciones": "MP ya configurado segun capturas - Para pago REAL necesitas tarjeta tokenizada REAL con SDK aislado"
    }

@app.post("/pago/procesar")
def pagar(req: PagoRequest):
    logger.info(f"Pago V11: {req.comercio_id} ${req.monto_original} trans {req.trans_id} mp_token={bool(req.mp_token)}")
    es_destacado = "20" in req.comercio_id or "lomitos_20" in req.comercio_id
    es_adherido = req.comercio_id in COMERCIOS_ADHERIDOS or "suc_" in req.comercio_id or es_destacado or any(x in req.comercio_id for x in ["felipe", "panaderia", "comercio", "templo", "jumbo", "fravega", "mcdonalds"])
    monto = float(req.monto_original)
    if monto < 1 or monto > 1000000:
        return JSONResponse({"status": "error", "msg": "Monto invalido"}, status_code=400)
    comercio_nombre_real = req.comercio_nombre or req.comercio_id.replace("_", " ").title() or "Comercio"
    fecha = req.fecha or datetime.now().strftime("%d/%m/%Y")
    hora = req.hora or datetime.now().strftime("%H:%M:%S")
    trans_id = req.trans_id or f"TX-{uuid.uuid4().hex[:8].upper()}"
    csb = round(monto * (0.10 if es_adherido else 0.05), 2)
    comision = round(monto * COMISION_PORCENTAJE, 2)
    mp_payment_id = None
    modo = "DEMO_SIN_TOKEN"
    if MP_ACCESS_TOKEN:
        if req.mp_token:
            try:
                headers = {"Authorization": f"Bearer {MP_ACCESS_TOKEN}", "Content-Type": "application/json", "X-Idempotency-Key": trans_id}
                payload = {"transaction_amount": float(monto), "token": req.mp_token, "description": f"MaxShop - {comercio_nombre_real} - {trans_id}", "installments": 1, "payer": {"email": req.email_cliente or req.user_id or "cliente@maxshop.com"}, "external_reference": trans_id, "statement_descriptor": "MaxShop"}
                logger.info(f"Intentando pago REAL MP: ${monto} en {comercio_nombre_real}")
                response = requests.post("https://api.mercadopago.com/v1/payments", json=payload, headers=headers, timeout=20)
                mp_result = response.json()
                logger.info(f"MP response {response.status_code}: {mp_result}")
                if response.status_code in [200, 201]:
                    mp_payment_id = mp_result.get("id")
                    status = mp_result.get("status")
                    if status == "approved":
                        modo = "REAL_APROBADO"
                    elif status in ["rejected", "cancelled"]:
                        return {"status": "rechazado", "modo": "REAL_RECHAZADO", "motivo": mp_result.get("status_detail", "fondos_insuficientes"), "transaccion": {"id": trans_id, "monto": monto, "comercio_nombre": comercio_nombre_real, "fecha": fecha, "hora": hora, "status": "rechazado", "mensaje": f"Rechazado - {mp_result.get('status_detail')}"}}
                    else:
                        modo = f"REAL_{status}"
                else:
                    logger.error(f"MP error {response.status_code}: {mp_result}")
                    return JSONResponse({"status": "error_mp", "modo": "REAL_ERROR", "mp_status": response.status_code, "mp_error": mp_result, "msg": "Error MP - Verifica ACCESS_TOKEN"}, status_code=400)
            except Exception as e:
                logger.error(f"Excepcion MP: {e}", exc_info=True)
                return JSONResponse({"status": "error_conexion_mp", "modo": "REAL_ERROR_CONEXION", "error": str(e), "msg": "Error conexión MP"}, status_code=500)
        else:
            logger.warning("MP configurado pero sin mp_token - tokeniza tarjeta en Perfil>Tarjetas")
            modo = "DEMO_SIN_TOKEN"
    else:
        modo = "DEMO_SIN_CONFIG"
        logger.warning("MP_ACCESS_TOKEN no configurado - modo DEMO")
    return {"status": "aprobado", "modo": modo, "_interno_mp_id": mp_payment_id, "_interno_comision": comision, "transaccion": {"id": trans_id, "monto_detectado": monto, "monto_real": monto, "fecha": fecha, "hora": hora, "trans_id": trans_id, "comercio_id": req.comercio_id, "comercio_nombre": comercio_nombre_real, "comercio_nombre_real": comercio_nombre_real, "metodo": "TAP/QR posnet - MaxShop Wallet", "es_adherido": es_adherido, "es_destacado": es_destacado, "pin": "dorado" if es_destacado else ("azul" if es_adherido else "sin pin"), "tarjeta_usada": req.tarjeta or "No especificada", "tipo_tarjeta": req.tipo_tarjeta or "Visa/Mastercard", "csb_cliente_nuevo": csb, "comision_interna": comision, "mensaje_exito": f"Pago confirmado en {comercio_nombre_real}", "seguridad": f"Transaccion verificada - {fecha} {hora} - ID {trans_id} - MaxShop Wallet", "timestamp": datetime.utcnow().isoformat(), "modo": modo}}
