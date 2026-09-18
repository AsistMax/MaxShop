import os, uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import jwt

JWT_SECRET = os.getenv("JWT_SECRET", "maxshop-super-secret-2026")
COMISION = 0.017
CSB_ADHERIDO_CLIENTE = 0.10
CSB_NO_ADHERIDO_CLIENTE = 0.05
CSB_COMERCIO = 0.05

app = FastAPI(title="MaxShop V5")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

COMERCIOS_ADHERIDOS = {"felipe", "panaderia_pm", "lomitos_lo_mas", "comercio_123"}

class PagoRequest(BaseModel):
    user_id: str
    comercio_id: str
    monto_original: float
    card_token: str = "card_token_demo"
    qr_posnet_data: Optional[str] = None

class WebhookPago(BaseModel):
    status: str
    amount: float
    comercio_id: str
    user_id: str
    transaction_id: str

def validar_qr_posnet(qr_data: str):
    try:
        if qr_data and qr_data.startswith("MAXSHOP"):
            clean = qr_data.split(":")[-1].rsplit(".",1)[0] if "." in qr_data else ""
            if clean:
                decoded = jwt.decode(clean, JWT_SECRET, algorithms=["HS256"])
                return decoded
        return {"monto": None, "comercio_id": "detectado_por_gps"}
    except:
        return {"monto": None, "comercio_id": "detectado_por_gps"}

INDEX_HTML_EMBED = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>MaxShop - Descuentos de Locos</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@800;900&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet">
<style>
:root{--primary:#11084C;--accent:#FF2E2E;--bg:#f7f6ff;--card:#fff;--ok:#00c950;--muted:#6b6a8a;--border:rgba(17,8,76,.08)}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Manrope',sans-serif;background:var(--bg);color:var(--primary);-webkit-font-smoothing:antialiased}
.navbar{position:sticky;top:0;z-index:10;background:rgba(255,255,255,.95);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:12px 16px;display:flex;justify-content:space-between;align-items:center}
.logo{font-family:'Inter',sans-serif;font-weight:900;font-size:22px;letter-spacing:-1px}.logo span{color:var(--accent)}
.card{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:16px;box-shadow:0 8px 24px rgba(17,8,76,.06)}
.hero{max-width:1100px;margin:0 auto;padding:18px 16px;display:grid;grid-template-columns:1.1fr .9fr;gap:16px}
.hero h1{font-family:'Inter',sans-serif;font-weight:900;font-size:42px;line-height:.95;letter-spacing:-1px}
.hero h1 b{color:var(--accent)}
.btn{padding:12px 18px;border-radius:12px;font-weight:800;border:0;cursor:pointer;display:inline-flex;gap:6px;align-items:center;justify-content:center}
.btn-primary{background:var(--accent);color:#fff}.btn-dark{background:var(--primary);color:#fff}.btn-white{background:#fff;color:var(--primary);border:1px solid var(--border)}
.badge{display:inline-flex;padding:5px 10px;border-radius:99px;font-weight:800;font-size:11px;background:var(--accent);color:#fff}
.badge.green{background:var(--ok)}
.grid{max-width:1100px;margin:0 auto;padding:0 16px 24px;display:grid;gap:14px}
.list{display:flex;flex-direction:column;gap:8px}
.item{display:flex;justify-content:space-between;align-items:center;padding:12px;border:1px solid var(--border);border-radius:12px;background:#fff}
.success{background:#eafff2;border:1px solid rgba(0,201,80,.2);border-radius:14px;padding:14px;font-weight:700}
.hidden{display:none}
@media(max-width:800px){.hero{grid-template-columns:1fr}.hero h1{font-size:34px}}
</style>
</head>
<body>
<div class="navbar">
  <div class="logo">MaxShop <span>%</span></div>
  <div style="display:flex;gap:8px;align-items:center">
    <div class="card" style="padding:8px 12px">Saldo: <b id="saldoCB">$18.450 C$B</b></div>
  </div>
</div>
<div class="hero">
  <div>
    <h1>Pagá rápido con tus <b>tarjetas asociadas</b></h1>
    <p style="margin-top:10px;color:var(--muted)">Escaneá el QR del posnet del comercio y pagá en 1 minuto. El sistema detecta la compra y acredita C$B automáticamente.</p>
    <div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">
      <span class="badge">Tarjetas asociadas</span>
      <span class="badge green">Compra exitosa</span>
    </div>
    <div class="card" style="margin-top:14px">
      <b>Tus tarjetas asociadas</b>
      <div class="list" style="margin-top:10px">
        <div class="item"><span>Visa débito •• 1234</span><span class="badge green">Activa</span></div>
        <div class="item"><span>Mastercard •• 5678</span><span class="badge">Principal</span></div>
      </div>
      <button class="btn btn-white" style="margin-top:10px;width:100%">+ Asociar tarjeta</button>
      <small style="color:var(--muted)">Tus tarjetas quedan guardadas de forma segura para pagar más rápido.</small>
    </div>
  </div>
  <div class="card">
    <b>Comercios cercanos</b>
    <p style="color:var(--muted);font-size:13px">Detectamos por tu ubicación: Felipe, Panadería PM, Lomitos lo-más</p>
    <button class="btn btn-dark" onclick="buscarCercanos()" style="margin-top:8px;width:100%">📍 Detectar comercios cercanos</button>
    <div id="cercanos" class="list" style="margin-top:10px"></div>
    <div style="margin-top:14px;border-top:1px solid var(--border);padding-top:12px">
      <b>Escanear QR del posnet del comercio</b>
      <p style="color:var(--muted);font-size:13px">El comercio genera QR dinámico desde su posnet con el monto. Vos escaneás y pagás con tarjetas asociadas.</p>
      <input id="monto" type="number" value="10000" style="width:100%;padding:10px;border-radius:10px;border:1px solid var(--border);margin-top:8px" placeholder="Monto detectado">
      <select id="comercio" style="width:100%;padding:10px;border-radius:10px;border:1px solid var(--border);margin-top:6px">
        <option value="felipe">Felipe (adherido)</option>
        <option value="panaderia_pm">Panadería PM (adherido)</option>
        <option value="lomitos_lo_mas">Lomitos lo-más (adherido)</option>
        <option value="carrefour_no_adherido">Carrefour (no adherido)</option>
        <option value="musimundo_no_adherido">Musimundo (no adherido)</option>
      </select>
      <button class="btn btn-primary" onclick="pagar()" style="margin-top:8px;width:100%">Pagar con tarjeta asociada</button>
      <div id="resultado" class="hidden" style="margin-top:10px"></div>
    </div>
  </div>
</div>
<div class="grid">
  <div class="card">
    <b>¿Cómo funciona?</b>
    <div class="list" style="margin-top:8px">
      <div class="item"><span>1. Comercio genera QR dinámico desde su posnet con el monto</span></div>
      <div class="item"><span>2. Escaneás con MaxShop y pagás con tarjetas asociadas</span></div>
      <div class="item"><span>3. Sistema detecta pago exitoso automáticamente</span></div>
      <div class="item"><span>4. Ves: Compra exitosa, pagaste $10.000 + C$B acreditado</span></div>
    </div>
  </div>
  <div class="card">
    <b>Beneficios</b>
    <div class="list" style="margin-top:8px">
      <div class="item"><span>Adherido:</span><b>+10% C$B para vos, +5% C$B para comercio</b></div>
      <div class="item"><span>No adherido:</span><b>+5% C$B para vos</b></div>
      <div class="item"><span>Comisión:</span><b>1.7% con tarjeta asociada</b></div>
    </div>
  </div>
</div>
<script>
const API = location.origin;
async function buscarCercanos(){
  const el=document.getElementById('cercanos');
  el.innerHTML='Detectando...';
  try{
    if(navigator.geolocation){
      navigator.geolocation.getCurrentPosition(async pos=>{
        const lat=pos.coords.latitude, lng=pos.coords.longitude;
        const res=await fetch(`${API}/comercios/cercanos?lat=${lat}&lng=${lng}`);
        const data=await res.json();
        el.innerHTML=data.cercanos.map(c=>`<div class='item'><span>${c.nombre} • ${c.distancia}</span><span class='badge ${c.adherido?'green':''}'>${c.promo}</span></div>`).join('');
      }, async ()=>{
        const res=await fetch(`${API}/comercios/cercanos?lat=-28.4696&lng=-65.7857`);
        const data=await res.json();
        el.innerHTML=data.cercanos.map(c=>`<div class='item'><span>${c.nombre} • ${c.distancia}</span><span class='badge ${c.adherido?'green':''}'>${c.promo}</span></div>`).join('');
      });
    }else{
      const res=await fetch(`${API}/comercios/cercanos?lat=-28.4696&lng=-65.7857`);
      const data=await res.json();
      el.innerHTML=data.cercanos.map(c=>`<div class='item'><span
