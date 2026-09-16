from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Dict
import uuid

app = FastAPI(title="Max%Shop v8 FINAL CAMPAÑA - maxshop365-c45e0 - Modelo 1.7% real")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def load_html():
    try:
        with open("index.html","r",encoding="utf-8") as f:
            return f.read()
    except:
        with open("/mnt/data/index.html","r",encoding="utf-8") as f:
            return f.read()

DB: Dict = {
    "usuarios": {"demo": {"id":"demo","dni":"30111222","saldo":1250,"bienvenida_total":1500,"bienvenida_usada":250,"rol":"usuario","verificado":True}},
    "comercios": {
        "demo": {"id":"demo","nombre":"Supermercado La Bodega","cuit":"30-12345678-9","ventas_mes":45200,"rol":"comercio","promo_lunes":20,"promo_miercoles":0}
    },
    "comprobantes": [],
}

class PagoQR(BaseModel):
    comercio_id: str
    monto: float
    descuento_comercio_porcentaje: float = 5  # 5% base obligatorio, si promo reemplaza
    tipo_pago: str = "qr"
    user_id: str = "demo"

def get_descuento_comercio(comercio, porcentaje_enviado: float):
    # Regla: 5% base obligatorio todos los días. Promo reemplaza, NO suma.
    # Si comercio quiere lunes 20%, es 20% solo, no 25%
    if porcentaje_enviado < 5:
        return 5  # minimo 5%
    return porcentaje_enviado  # si manda 20, es 20, no 25

@app.get("/", response_class=HTMLResponse)
def root():
    return load_html()

@app.get("/api/status")
def status():
    return {
        "status":"v8 FINAL CAMPAÑA - TODOS CONTENTOS - maxshop365-c45e0",
        "modelo":"5% base obligatorio todo los días (como pub Facebook) - Promo reemplaza, no suma. Lunes 20% = 20% solo",
        "comision_real":"1.7% real va directo a cuenta Max%Shop vía split automático al pagar QR - No hay que cobrarle al comercio",
        "cashback_virtual":"1.2% virtual cliente + 1.2% virtual comercio como comprador - No es plata real, son numeritos para próximo descuento",
        "bienvenida":"$1.500 tope $300 x compra válida 30 días - Virtual, la paga el comercio como costo de adquisición",
        "ejemplo_10000":"Venta $10.000 - 5% base = $9.500 paga cliente - Split: $9.338,50 comercio + $161,50 real Max%Shop (1.7%) - Virtual: $114 cliente + $114 comercio",
        "firebase":"maxshop365-c45e0 - apiKey AIzaSyDQwy... - Analytics G-9TJ0NPEBHD - Auth + Firestore + Storage",
        "logo":"268px transparente sin fondo blanco pegado",
        "pines":"Ojo + lengua azul #1e3a5f y naranja #ff6a00",
        "seguridad":"por rol + Firebase Auth + datos aislados DNI/CUIT + validación",
        "campana":"Lista para lanzar - Sin ruleta - Modelo sostenible"
    }

@app.post("/api/wallet/pagar-qr")
def pagar_qr(p: PagoQR):
    comercio = DB["comercios"].get(p.comercio_id, {"id":p.comercio_id})
    user = DB["usuarios"].get(p.user_id, {"saldo":1250,"bienvenida_total":1500,"bienvenida_usada":0})
    
    # 1. Descuento comercio: 5% base obligatorio, promo reemplaza no suma
    desc_porcentaje = get_descuento_comercio(comercio, p.descuento_comercio_porcentaje)
    descuento_comercio_monto = round(p.monto * (desc_porcentaje/100), 2)
    monto_con_desc_comercio = p.monto - descuento_comercio_monto
    
    # 2. Bienvenida $1500 tope $300 x compra válida 30 días
    bienvenida_disponible = user["bienvenida_total"] - user["bienvenida_usada"]
    descuento_bienvenida = min(monto_con_desc_comercio * 0.30, 300, bienvenida_disponible)
    descuento_bienvenida = max(0, descuento_bienvenida)
    neto_a_pagar = monto_con_desc_comercio - descuento_bienvenida
    
    # 3. Split automático: 1.7% real para Max%Shop
    comision_real = round(neto_a_pagar * 0.017, 2)  # $161,50 de $9.500 - va directo a tu cuenta
    monto_para_comercio = round(neto_a_pagar - comision_real, 2)  # $9.338,50 va directo al comercio
    
    # 4. Virtual (no es plata real, solo numeritos para próximo descuento)
    cashback_cliente_virtual = round(neto_a_pagar * 0.012, 2)  # $114 virtual cliente
    cashback_comercio_virtual = round(neto_a_pagar * 0.012, 2)  # $114 virtual comercio como comprador
    
    # Actualiza saldos virtuales
    user["saldo"] = user.get("saldo", 1250) + cashback_cliente_virtual
    user["bienvenida_usada"] = user.get("bienvenida_usada", 0) + descuento_bienvenida
    DB["usuarios"][p.user_id] = user
    
    comp_id = f"MAX-{uuid.uuid4().hex[:4].upper()}-{datetime.now().strftime('%d%m%Y')}"
    
    comprobante = {
        "comprobante_numero": comp_id,
        "monto_original": p.monto,
        "descuento_comercio_porcentaje": desc_porcentaje,
        "descuento_comercio_monto": descuento_comercio_monto,
        "descuento_bienvenida": descuento_bienvenida,
        "neto_a_pagar_cliente": neto_a_pagar,
        "split_automatico": {
            "para_comercio_real": monto_para_comercio,
            "para_maxshop_real_1_7_porciento": comision_real,
            "nota": "Split automático - No hay que cobrarle al comercio - Entra directo a tu cuenta"
        },
        "virtual_no_es_plata_real": {
            "cashback_cliente_virtual_1_2_porciento": cashback_cliente_virtual,
            "cashback_comercio_como_comprador_virtual_1_2_porciento": cashback_comercio_virtual,
            "nota": "Virtual no es reembolsable en efectivo - Solo descuento para próxima compra - No lo puede reclamar"
        },
        "bienvenida_restante": user["bienvenida_total"] - user["bienvenida_usada"],
        "estado": "PAGADO ✅",
        "firebase_project": "maxshop365-c45e0",
        "modelo": "5% base obligatorio + 1.7% real MaxShop + 1.2% virtual cliente + 1.2% virtual comercio"
    }
    DB["comprobantes"].append(comprobante)
    return comprobante

@app.get("/api/comercios")
def listar_comercios():
    return [
        {"id":"demo","nombre":"Supermercado La Bodega","categoria":"Supermercado","descuento_base":"5% todos los días obligatorio","promo_lunes":"20% (reemplaza 5%, no suma)","comision_real":"1.7% split automático"},
    ]
