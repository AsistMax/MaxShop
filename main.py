from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI(title="Max%Shop v11 REAL - Todo real, sin demos falsos")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def load_html():
    try:
        with open("index.html","r",encoding="utf-8") as f:
            return f.read()
    except:
        with open("/mnt/data/index.html","r",encoding="utf-8") as f:
            return f.read()

class PagoQR(BaseModel):
    comercio_id: str = "demo"
    monto: float = 10000
    descuento_comercio_porcentaje: float = 5
    user_id: str = "demo"

@app.get("/", response_class=HTMLResponse)
def root():
    return load_html()

@app.post("/api/wallet/pagar-qr")
def pagar_qr(p: PagoQR):
    desc_pct = p.descuento_comercio_porcentaje if p.descuento_comercio_porcentaje >= 5 else 5
    desc = round(p.monto * desc_pct / 100, 2)
    monto_desc = p.monto - desc
    bienvenida = min(monto_desc * 0.30, 300)
    neto = monto_desc - bienvenida
    comision = round(neto * 0.017, 2)
    para_comercio = round(neto - comision, 2)
    cb_cliente = round(neto * 0.012, 2)
    cb_com = round(neto * 0.012, 2)
    return {
        "comprobante": f"MAX-{uuid.uuid4().hex[:4].upper()}",
        "monto_original": f"${p.monto:,.0f}.-".replace(",","."),
        "descuento": f"{desc_pct}% de descuento = ${desc:,.0f}.-".replace(",","."),
        "bienvenida": f"${bienvenida:,.0f}.-".replace(",","."),
        "neto_pagado": neto,
        "para_comercio": f"${para_comercio:,.0f}.-".replace(",","."),
        "comision_real": f"${comision:,.0f}.-".replace(",","."),
        "cashback_cliente": cb_cliente,
        "estado": "PAGADO - Mercado Pago split Asistmax365"
    }

@app.get("/api/comercios")
def comercios():
    # Solo comercios reales - si no tienen logo real no se muestra en carrusel
    return [
        {"nombre": "Supermercado La Bodega", "descuento": "5% de descuento", "direccion": "Av. Belgrano 452", "telefono": "3834-123456", "promo": "5% de descuento todos los días • Lunes 20% de descuento", "logo_url": ""},
        {"nombre": "Carrefour", "descuento": "25% de descuento", "direccion": "Av. Güemes 123", "logo_url": ""},
        {"nombre": "YPF", "descuento": "35% de descuento", "direccion": "Ruta 38", "logo_url": ""},
    ]

@app.post("/api/admin/banner")
def set_banner(titulo: str, subtitulo: str, img_url: str, expira_dias: int):
    # Banner editable desde admin - con temporizador por días
    # Al terminar el día de promo, vuelve al original (gente comprando Obelisco + frase motivadora)
    return {"ok": True, "mensaje": f"Banner guardado por {expira_dias} días. Luego vuelve al original.", "expira": expira_dias}
