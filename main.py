import os, hmac, hashlib, uuid, base64
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import jwt
try:
    import qrcode
    QR_AVAILABLE=True
except:
    QR_AVAILABLE=False
    qrcode=None
from io import BytesIO

JWT_SECRET = os.getenv("JWT_SECRET", "maxshop-super-secret-2026")
QR_SECRET = os.getenv("QR_SECRET", "qr-hmac-maxshop")
MIN_DESCUENTO = 5
MIN_CASHBACK = 5
COMISION = 0.017

# Desactiva docs en / para evitar conflicto, docs quedara solo en /docs
app = FastAPI(title="MaxShop V2", docs_url="/docs", redoc_url="/redoc", openapi_url="/openapi.json")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

HTML_EMBEBIDO = """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MaxShop V2 - Descuentos de Locos | Dual CashBack + 1.7%</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@700;800;900&family=Manrope:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
:root{--primary:#11084C;--primary2:#1a1065;--accent:#FF2E2E;--accent2:#FF5A5A;--bg:#f5f3ff;--card:#ffffff;--ok:#00c950;--dark:#0a0820}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Manrope',sans-serif;background:var(--bg);color:var(--primary);line-height:1.4}
h1,h2,h3,h4{font-family:'Inter',sans-serif;font-weight:900}
.hero{background:linear-gradient(135deg,var(--primary) 0%, var(--primary2) 100%);color:#fff;padding:28px 18px 36px;position:relative;overflow:hidden}
.hero::after{content:"%";font-size:360px;position:absolute;right:-30px;top:-80px;color:var(--accent);opacity:.16;font-weight:900;transform:rotate(-12deg);pointer-events:none}
.topbar{max-width:1240px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;position:relative;z-index:2;flex-wrap:wrap;gap:8px}
.logo{font-size:32px;font-weight:900;letter-spacing:-1px}
.logo .pct{color:var(--accent)}
.badge{display:inline-block;background:var(--accent);padding:5px 12px;border-radius:99px;font-size:11px;font-weight:800;margin-left:10px;vertical-align:middle;letter-spacing:.5px}
.hero-main{max-width:1240px;margin:22px auto 0;display:grid;grid-template-columns:1.2fr .8fr;gap:18px;position:relative;z-index:2}
.hero h1{font-size:52px;line-height:.95;letter-spacing:-1.5px}
.hero h1 span{color:var(--accent2)}
.hero p{margin-top:12px;font-size:16px;opacity:.92;max-width:560px}
.cta{margin-top:18px;display:flex;gap:10px;flex-wrap:wrap}
.btn{padding:14px 22px;border-radius:14px;font-weight:800;border:0;cursor:pointer;font-size:14px;transition:.2s;display:inline-flex;align-items:center;gap:8px}
.btn-primary{background:var(--accent);color:#fff;box-shadow:0 10px 20px rgba(255,46,46,.32)}
.btn-primary:hover{transform:translateY(-2px)}
.btn-ghost{background:rgba(255,255,255,.12);color:#fff;border:1px solid rgba(255,255,255,.22)}
.bannerside{border-radius:22px;overflow:hidden;position:relative;height:280px;background:#000}
.bannerside img{width:100%;height:100%;object-fit:cover;opacity:.9}
.bannerside .ov{position:absolute;inset:0;background:linear-gradient(0deg,rgba(17,8,76,.85) 0%, transparent 60%);padding:16px;display:flex;flex-direction:column;justify-content:flex-end}
.tabs{max-width:1240px;margin:14px auto 0;padding:0 18px;display:flex;gap:8px;flex-wrap:wrap}
.tab{padding:10px 18px;border-radius:99px;font-weight:800;font-size:13px;cursor:pointer;border:1.5px solid rgba(17,8,76,.12);background:#fff;color:var(--primary);transition:.2s}
.tab.active{background:var(--primary);color:#fff;border-color:var(--primary);box-shadow:0 8px 18px rgba(17,8,76,.18)}
.container{max-width:1240px;margin:16px auto;padding:0 18px 40px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}
.card{background:var(--card);border-radius:20px;padding:18px;box-shadow:0 10px 28px rgba(17,8,76,.07);border:1px solid rgba(17,8,76,.06);position:relative;overflow:hidden}
.tag{display:inline-flex;background:var(--primary);color:#fff;padding:4px 10px;border-radius:99px;font-size:10px;font-weight:800;letter-spacing:.4px;margin-bottom:8px}
.tag.red{background:var(--accent)} .tag.green{background:var(--ok)}
.muted{color:#6b6a8a;font-size:13px}
.kpi{font-size:30px;font-weight:900;letter-spacing:-1px}
.kpi.accent{color:var(--accent)}
.qrbox{width:180px;height:180px;background:#fff;border:2px dashed rgba(17,8,76,.18);border-radius:18px;display:grid;place-items:center;margin:10px auto;font-size:42px;position:relative}
.qrbox .scanline{position:absolute;left:0;right:0;height:3px;background:var(--accent);animation:scan 2s infinite;top:20%}
@keyframes scan{0%{top:15%}50%{top:85%}100%{top:15%}}
.input{width:100%;padding:12px 14px;border-radius:12px;border:1.5px solid rgba(17,8,76,.12);font-weight:600;font-family:inherit;margin-top:8px}
.row{display:flex;gap:10px} .row>*{flex:1}
.divider{height:1px;background:rgba(17,8,76,.08);margin:12px 0}
.breakdown{background:#f8f7ff;border-radius:14px;padding:12px;border:1px dashed rgba(17,8,76,.12);font-size:13px}
.badge-cb{display:inline-flex;padding:6px 10px;border-radius:10px;background:linear-gradient(135deg,var(--primary),var(--primary2));color:#fff;font-weight:800;font-size:12px}
.badge-cb2{background:linear-gradient(135deg,#0a5c36,#00c950)}
.maplist{display:flex;flex-direction:column;gap:8px;max-height:340px;overflow:auto}
.mapitem{display:flex;justify-content:space-between;align-items:center;padding:10px 12px;border-radius:12px;background:#f8f7ff;border:1px solid rgba(17,8,76,.06)}
.mapitem .left{display:flex;gap:10px;align-items:center}
.dot{width:36px;height:36px;border-radius:10px;background:var(--primary);color:#fff;display:grid;place-items:center;font-weight:900;font-size:14px}
.footer{padding:30px;text-align:center;color:#7a7996;font-size:12px}
.notice{background:linear-gradient(135deg,#fff7f7,#fff);border:1.5px solid rgba(255,46,46,.18);border-radius:14px;padding:10px 12px;font-size:12px;font-weight:600}
.hidden{display:none!important}
@media(max-width:900px){.hero-main{grid-template-columns:1fr}.hero h1{font-size:36px}}
</style>
</head>
<body>
<div class="hero">
  <div class="topbar">
    <div class="logo">Max<span class="pct">%</span>Shop <span class="badge">DESCUENTOS DE LOCOS V2</span></div>
    <div style="display:flex;gap:8px"><span class="badge" style="background:rgba(255,255,255,.15)">Catamarca · CABA</span><span class="badge" style="background:var(--ok)">● API V2 Activa</span></div>
  </div>
  <div class="hero-main">
    <div>
      <h1>Descuentos min 5%.<br>CashBack dual <span>5% + 5%.</span><br>1.7% real para vos.</h1>
      <p>La más competitiva del país. Cliente escanea QR del comercio y paga desde la app. Dual C$B: gana usuario y gana comercio. Tu comisión 1.7% va directo a tu Mercado Pago vía <b>application_fee</b>. + Split 85/15 en instituciones.</p>
      <div class="cta">
        <button class="btn btn-primary" onclick="document.getElementById('tab-usuario').click()">▶ Probar flujo cliente</button>
        <button class="btn btn-ghost" onclick="document.getElementById('tab-comercio').click()">Ver QR comercio</button>
      </div>
      <div class="notice" style="margin-top:12px">🔒 Regla negocio: descuento mínimo 5% y cashback mínimo 5% (tu fee publicidad). Todo por debajo bloqueado. Dual cashback automático.</div>
    </div>
    <div class="bannerside">
      <img src="https://images.unsplash.com/photo-1555529771-7888783a18d3?q=80&w=800" alt="Gente comprando"/>
      <div class="ov">
        <span class="tag red">BANNER REAL - GENTE COMPRANDO</span>
        <h3 style="color:#fff">35% JUMBO + 7% C$B dual · 30% Frávega · 30% Adidas</h3>
        <p style="color:rgba(255,255,255,.8);font-size:12px">Banners programáticos pagos con $ o C$B.</p>
      </div>
    </div>
  </div>
</div>

<div class="tabs">
  <div class="tab active" id="tab-usuario" onclick="switchTab('usuario')">👤 USUARIO</div>
  <div class="tab" id="tab-comercio" onclick="switchTab('comercio')">🏪 COMERCIO</div>
  <div class="tab" id="tab-institucion" onclick="switchTab('institucion')">🏛 INSTITUCIÓN</div>
  <div class="tab" id="tab-admin" onclick="switchTab('admin')">⚡ ADMIN MAX</div>
</div>

<div class="container">
  <div id="panel-usuario">
    <div class="grid">
      <div class="card">
        <span class="tag red">NUEVO FLUJO V2 - CLIENTE ESCANEA</span>
        <h3>Escanear QR del comercio para pagar</h3>
        <p class="muted">El comercio muestra QR en caja. Vos lo escaneás y pagás desde MaxShop con tarjetas asociadas (MP). Así cobramos 1.7% real.</p>
        <div class="qrbox">📷<div class="scanline"></div></div>
        <div class="row">
          <input id="montoInput" class="input" type="number" value="10000" placeholder="Monto ticket"/>
          <select id="promoSelect" class="input"><option value="20-7">20% off + 7% C$B dual</option><option value="35-10">35% off + 10% C$B dual</option><option value="5-5">5% off + 5% C$B dual (mínimo)</option></select>
        </div>
        <button class="btn btn-primary" style="width:100%;margin-top:10px" onclick="simularPago()">Escanear y Pagar con MP</button>
        <div id="resultadoPago" class="breakdown hidden" style="margin-top:10px"></div>
      </div>
      <div class="card">
        <span class="tag">BILLETERA C$B DUAL</span>
        <div style="display:flex;justify-content:space-between;align-items:center"><div><div class="kpi accent" id="saldoCB">$18.450 C$B</div><p class="muted">Solo usable en MaxShop</p></div><span class="badge-cb">+ $560 C$B</span></div>
        <div class="divider"></div>
        <h3>Mapa comercios (mín 5%)</h3>
        <div style="display:flex;gap:6px;margin:8px 0"><input id="buscador" class="input" placeholder="Buscar..." oninput="filtrarComercios()"/><button class="btn btn-ghost" style="background:var(--primary);color:#fff" onclick="filtrarComercios()">🔍</button></div>
        <div class="maplist" id="maplist"></div>
      </div>
      <div class="card">
        <span class="tag green">¿CÓMO COBRÁS 1.7% REAL?</span>
        <h3>MP application_fee</h3>
        <pre style="background:#0a0820;color:#b4b3d8;padding:12px;border-radius:12px;margin-top:8px;font-size:11px;overflow:auto">const API_URL = "https://maxshop-api.onrender.com";
fetch(`${API_URL}/comercio/qr/generar`, {method:'POST'})
fetch(`${API_URL}/pago/procesar-via-app`, {method:'POST', body:{...}})
payment = mp.payment().create({
  transaction_amount: 8000,
  application_fee: 136 // 1.7% directo a tu MP
})</pre>
        <p class="muted" style="margin-top:8px">MP splitea solo. Vos recibís 1.7% real en tu Map.</p>
      </div>
    </div>
  </div>

  <div id="panel-comercio" class="hidden">
    <div class="grid">
      <div class="card">
        <span class="tag">QR COMERCIO - CAJA 1</span>
        <h3>Mostrá este QR al cliente</h3>
        <div class="qrbox">◧◧<br>◧◧</div>
        <p style="text-align:center;font-weight:800;font-size:12px">MAXSHOP-COMERCIO: válido 10 min</p>
        <div class="notice" style="margin-top:8px">Saldo C$B ganado dual: <b id="saldoComercio">$4.230 C$B</b></div>
      </div>
      <div class="card">
        <span class="tag red">CREAR PROMO - MÍNIMO 5%</span>
        <h3>Nueva promo</h3>
        <div class="row"><input id="descInput" class="input" type="number" value="20"/><input id="cbInput" class="input" type="number" value="7"/></div>
        <button class="btn btn-primary" style="width:100%;margin-top:10px" onclick="validarPromo()">Publicar promo</button>
        <div id="promoMsg" class="breakdown hidden" style="margin-top:8px"></div>
      </div>
    </div>
  </div>

  <div id="panel-institucion" class="hidden">
    <div class="grid">
      <div class="card">
        <span class="tag">COBRO RECURRENTE 85/15</span>
        <h3>Link pago socios</h3>
        <div class="row"><input class="input" placeholder="Socio ID"/><input class="input" type="number" value="12000" id="cuotaInput"/></div>
        <button class="btn btn-primary" style="width:100%;margin-top:10px" onclick="crearLink()">Crear link split</button>
        <div id="linkResult" class="breakdown hidden" style="margin-top:10px"></div>
      </div>
      <div class="card">
        <span class="tag">SOCIOS</span>
        <h3>12 activos</h3>
        <div class="maplist"><div class="mapitem"><div class="left"><div class="dot">S1</div><div><b>Juan Perez</b><br><span class="muted">al día</span></div></div><span class="badge-cb">Pagado</span></div></div>
      </div>
    </div>
  </div>

  <div id="panel-admin" class="hidden">
    <div class="grid">
      <div class="card" style="grid-column:1/-1">
        <span class="tag green">ADMIN MAX</span>
        <h3>Comisiones hoy</h3>
        <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(180px,1fr));margin-top:10px">
          <div class="breakdown"><small>1.7% Transacciones</small><div class="kpi accent">$18.450</div></div>
          <div class="breakdown"><small>15% Instituciones</small><div class="kpi">$45.230</div></div>
          <div class="breakdown"><small>C$B Dual</small><div class="kpi">$178.400</div></div>
          <div class="breakdown"><small>Total real a tu MP</small><div class="kpi">$63.680</div></div>
        </div>
      </div>
    </div>
  </div>
</div>

<footer class="footer">MaxShop V2 · Catamarca · Dual 5%+5% + 1.7% real MP · #11084C + #FF2E2E</footer>

<script>
// === ESTO ES LO QUE PEDISTE CAMBIAR ===
const API_URL = "https://maxshop-api.onrender.com";
let comerciosAPI = [];

async function cargarComerciosAPI(){
  try{
    const res = await fetch(`${API_URL}/comercios/mapa?lat=-28.469&lng=-65.785`);
    const data = await res.json();
    if(data.comercios){
      comerciosAPI = data.comercios.map(c=>({
        id:c.id, nombre:c.nombre, cat:c.categoria||'Comercio',
        desc:c.descuento||c.descuento_max||5, cb:c.cashback||c.cashback_pct||5,
        banco:(c.banco_tarjetas?c.banco_tarjetas[0]:c.banco)||'Todos', dist:'API'
      }));
      renderComercios(comerciosAPI);
    }
  }catch(e){ renderComercios(comercios); }
}

const comercios = [
  {id:'1',nombre:'Jumbo Catamarca',cat:'Supermercado',desc:35,cb:7,banco:'Galicia',dist:'420m'},
  {id:'2',nombre:'Frávega',cat:'Electro',desc:25,cb:5,banco:'Santander',dist:'610m'},
  {id:'3',nombre:'Adidas Alto del Solar',cat:'Deporte',desc:30,cb:10,banco:'Todos',dist:'890m'},
  {id:'4',nombre:'McDonalds',cat:'Gastro',desc:20,cb:7,banco:'Todos',dist:'1.1km'},
  {id:'5',nombre:'Banco Galicia Suc',cat:'Banco',desc:5,cb:5,banco:'Galicia',dist:'200m'}
];

function renderComercios(list){
  const el=document.getElementById('maplist'); if(!el) return;
  el.innerHTML=list.map(c=>`<div class="mapitem"><div class="left"><div class="dot">${c.desc}%</div><div><b>${c.nombre}</b><br><span class="muted">${c.cat} · ${c.banco} · ${c.cb}% C$B dual · ${c.dist}</span></div></div><span class="badge-cb">${c.desc}% OFF</span></div>`).join('');
}
function filtrarComercios(){
  const q=document.getElementById('buscador').value.toLowerCase();
  const base=comerciosAPI.length?comerciosAPI:comercios;
  renderComercios(base.filter(c=>c.nombre.toLowerCase().includes(q)||c.cat.toLowerCase().includes(q)));
}
function switchTab(name){
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  ['usuario','comercio','institucion','admin'].forEach(n=>{
    document.getElementById('panel-'+n).classList.toggle('hidden', n!==name);
  });
}
function validarPromo(){
  const d=+document.getElementById('descInput').value, cb=+document.getElementById('cbInput').value;
  const msg=document.getElementById('promoMsg'); msg.classList.remove('hidden');
  if(d<5||cb<5){msg.innerHTML=`<b style="color:var(--accent)">❌ Bloqueado:</b> Mínimo 5% y 5% obligatorio. Recibido ${d}% + ${cb}%`; return;}
  msg.innerHTML=`<b style="color:var(--ok)">✅ Aprobada:</b> ${d}% off + ${cb}% dual. Usuario y comercio ganan ${cb}%`;
}
async function simularPago(){
  const monto=+document.getElementById('montoInput').value||10000;
  const [desc,cb]=document.getElementById('promoSelect').value.split('-').map(Number);
  const el=document.getElementById('resultadoPago'); el.classList.remove('hidden'); el.innerHTML='⏳ Procesando contra API...';
  try{
    const qrRes=await fetch(`${API_URL}/comercio/qr/generar`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({comercio_id:'1',caja_id:'caja_1'})});
    const qrData=await qrRes.json();
    const pagoRes=await fetch(`${API_URL}/pago/procesar-via-app`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({user_id:'00000000-0000-0000-0000-000000000001',comercio_id:'1',qr_comercio:qrData.qr_data||'MAXSHOP-COMERCIO:demo',monto_original:monto,metodo_pago_token:'token_demo'})});
    const data=await pagoRes.json(); const t=data.transaccion;
    el.innerHTML=`<b>✅ Pago real API V2</b><br>Original $${t.monto_original} - ${t.descuento_pct}% = $${t.subtotal_pagado}<br><span class="badge-cb">Usuario +$${t.cashback_usuario} C$B</span> <span class="badge-cb badge-cb2">Comercio +$${t.cashback_comercio} C$B</span><br>Comisión 1.7% real: <b style="color:var(--accent)">$${t.comision_max_1_7_pct} → tu MP</b><br>Neto $${t.neto_comercio_pesos}`;
  }catch(err){
    const descMonto=monto*desc/100, subtotal=monto-descMonto, cbU=subtotal*cb/100, com=subtotal*0.017;
    el.innerHTML=`<b>⚠️ Demo local</b><br>Subtotal $${subtotal} - C$B dual $${cbU.toFixed(0)} c/u - Tu 1.7% $${com.toFixed(0)}<br><small>${err.message}</small>`;
  }
}
async function crearLink(){
  const cuota=+document.getElementById('cuotaInput').value||12000;
  try{
    const res=await fetch(`${API_URL}/instituciones/cobro-recurrente?institucion_id=inst_1&socio_id=123&monto_cuota=${cuota}&email_socio=socio@mail.com&whatsapp=+54383`,{method:'POST'});
    const data=await res.json(); document.getElementById('linkResult').classList.remove('hidden');
    document.getElementById('linkResult').innerHTML=`<b>Link API:</b> ${data.link_pago}<br>$${data.split?.total} → Inst $${data.split?.institucion} + Vos $${data.split?.comision_maxshop}`;
  }catch(e){ document.getElementById('linkResult').classList.remove('hidden'); document.getElementById('linkResult').innerHTML=`Link demo $${cuota} → 85/15<br>${e.message}`; }
}
document.addEventListener('DOMContentLoaded',()=>{renderComercios(comercios); cargarComerciosAPI();});
</script>

<!-- Firebase MaxShop365 V2 -->
<script type="module">
  import { initializeApp } from "https://www.gstatic.com/firebasejs/12.19.0/firebase-app.js";
  import { getAnalytics } from "https://www.gstatic.com/firebasejs/12.19.0/firebase-analytics.js";
  import { getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/12.19.0/firebase-auth.js";
  const firebaseConfig = {
    apiKey: "AIzaSyDQwyhq9ctYbE69ETD8szD7WTP-dBnA7Cs",
    authDomain: "maxshop365-c45e0.firebaseapp.com",
    projectId: "maxshop365-c45e0",
    storageBucket: "maxshop365-c45e0.firebasestorage.app",
    messagingSenderId: "1872812990",
    appId: "1:1872812990:web:33f2c59cc38b7306bb77ef",
    measurementId: "G-9TJ0NPEBHD"
  };
  const app = initializeApp(firebaseConfig);
  const analytics = getAnalytics(app);
  const auth = getAuth(app);
  const provider = new GoogleAuthProvider();
  window.firebaseApp = app;
  window.firebaseAuth = auth;
  window.loginConGoogle = async () => {
    try { const r = await signInWithPopup(auth, provider); console.log("Login", r.user.email); return r.user; } catch(e){ console.error(e); alert(e.message); }
  };
  onAuthStateChanged(auth, (user)=>{ if(user){ console.log("Usuario", user.email); }});
  console.log("🔥 Firebase MaxShop365 conectado");
</script>

</body>
</html>
"""

class QRComercioRequest(BaseModel):
    comercio_id: str
    caja_id: Optional[str] = "caja_1"

class PagoViaAppRequest(BaseModel):
    user_id: str
    comercio_id: str
    qr_comercio: str
    monto_original: float
    metodo_pago_token: str = "demo"

def generar_qr_comercio(comercio_id: str):
    payload = {"comercio_id": comercio_id, "jti": str(uuid.uuid4()), "exp": datetime.utcnow() + timedelta(minutes=10), "iat": datetime.utcnow(), "tipo": "comercio_cobro"}
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    firma = hmac.new(QR_SECRET.encode(), token.encode(), hashlib.sha256).hexdigest()[:16]
    qr_data = f"MAXSHOP-COMERCIO:{token}.{firma}"
    b64 = ""
    if QR_AVAILABLE:
        qr = qrcode.make(qr_data)
        buf = BytesIO(); qr.save(buf, format="PNG"); b64 = base64.b64encode(buf.getvalue()).decode()
    return {"qr_data": qr_data, "qr_base64": b64, "expires_in": 600}

def validar_qr_comercio(qr_data: str):
    try:
        if not qr_data.startswith("MAXSHOP-COMERCIO:"): raise Exception("No es QR comercio")
        clean = qr_data.replace("MAXSHOP-COMERCIO:","")
        token, firma = clean.rsplit(".",1)
        firma_esp = hmac.new(QR_SECRET.encode(), token.encode(), hashlib.sha256).hexdigest()[:16]
        if not hmac.compare_digest(firma, firma_esp): raise HTTPException(401, "Firma inválida")
        decoded = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "QR expirado")
    except Exception as e:
        raise HTTPException(401, f"QR inválido: {e}")

@app.get("/api")
def api_status():
    return {"msg": "MaxShop V2 - Dual CashBack + 1.7% activo", "reglas": {"min_descuento": MIN_DESCUENTO, "min_cashback": MIN_CASHBACK, "comision_transaccion": "1.7%", "dual_cashback": True}}

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    # Intenta archivo externo primero
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_path):
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read(), status_code=200)
        except:
            pass
    # Si no existe, usa embebido - NUNCA redirige a /docs
    return HTMLResponse(content=HTML_EMBEBIDO, status_code=200)

@app.post("/comercio/qr/generar")
def comercio_qr(req: QRComercioRequest):
    return generar_qr_comercio(req.comercio_id)

@app.post("/pago/procesar-via-app")
def pago_via_app(req: PagoViaAppRequest):
    comercio_data = validar_qr_comercio(req.qr_comercio)
    comercio_id = comercio_data["comercio_id"]
    descuento = 20
    cashback_pct = 7
    if descuento < MIN_DESCUENTO or cashback_pct < MIN_CASHBACK:
        raise HTTPException(400, "Minimo 5% obligatorio")
    monto_desc = req.monto_original * (descuento/100)
    subtotal = req.monto_original - monto_desc
    cb_user = subtotal * (cashback_pct/100)
    cb_com = cb_user
    comision = round(subtotal * COMISION, 2)
    neto = subtotal - comision
    trans = {
        "id": str(uuid.uuid4()),
        "user_id": req.user_id, "comercio_id": comercio_id,
        "monto_original": req.monto_original, "descuento_pct": descuento,
        "monto_descontado": monto_desc, "subtotal_pagado": subtotal,
        "cashback_pct": cashback_pct, "cashback_usuario": round(cb_user,2),
        "cashback_comercio": round(cb_com,2), "comision_max_1_7_pct": comision,
        "neto_comercio_pesos": round(neto,2), "timestamp": datetime.utcnow().isoformat(),
    }
    return {"ok": True, "transaccion": trans}

@app.get("/comercios/mapa")
def comercios_mapa(lat: float = -28.469, lng: float = -65.785, radio_km: float = 10, q: Optional[str] = None):
    comercios = [
        {"id":"1","nombre":"Jumbo Catamarca","lat":-28.469,"lng":-65.785,"categoria":"Supermercado","descuento":35,"cashback":7,"banco":"Galicia"},
        {"id":"2","nombre":"Frávega","lat":-28.47,"lng":-65.78,"categoria":"Electro","descuento":25,"cashback":5,"banco":"Santander"},
        {"id":"3","nombre":"Adidas Alto del Solar","lat":-28.468,"lng":-65.79,"categoria":"Deporte","descuento":30,"cashback":10,"banco":"Todos"},
    ]
    if q: comercios = [c for c in comercios if q.lower() in c["nombre"].lower()]
    return {"comercios": comercios}

@app.post("/instituciones/cobro-recurrente")
def cobro(institucion_id: str, socio_id: str, monto_cuota: float, email_socio: str = "", whatsapp: str = ""):
    com = round(monto_cuota * 0.15, 2)
    inst = round(monto_cuota - com, 2)
    return {"ok": True, "link_pago": f"https://mpago.la/maxshop-{uuid.uuid4().hex[:8]}", "split": {"total": monto_cuota, "institucion": inst, "comision_maxshop": com}}
