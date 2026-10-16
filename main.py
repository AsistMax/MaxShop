from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import qrcode
import io
import base64
from datetime import datetime
import uuid

# Supabase
try:
    from supabase import create_client, Client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
except:
    supabase = None

app = FastAPI(
    title="NODO ARGENTINA",
    description="API Empresa - QR Unico + BOTS 85/15",
    version="3.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class GenerarQRReq(BaseModel):
    comercio_id: str

class PagarQRReq(BaseModel):
    comercio_id: str
    qr_codigo: str
    monto: float = 0
    usuario_id: str = "anon"

@app.get("/", response_class=HTMLResponse)
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NODO ARGENTINA - API Empresa</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@600;800&display=swap" rel="stylesheet">
    <style>
        * { margin:0; padding:0; box-sizing:border-box; }
        body { background: linear-gradient(180deg, #F6F9FC 0%, #EDF2F7 100%); font-family: 'Inter', sans-serif; min-height:100vh; display:flex; justify-content:center; align-items:center; padding:20px; }
        .card { background: white; width: 100%; max-width: 400px; border-radius: 20px; box-shadow: 0 20px 60px rgba(10,37,64,0.12); border: 1px solid #E6EBF1; padding: 48px 32px 32px; text-align: center; }
        .nodo { font-size: 52px; font-weight: 800; color: #0A2540; letter-spacing: -3.5px; line-height: 1; margin:0; }
        .argentina { font-size: 11px; font-weight: 600; letter-spacing: 6px; background: linear-gradient(90deg, #00A6ED, #00D4FF); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin: 8px 0 24px; }
        .line { width: 64px; height: 3px; background: linear-gradient(90deg, #0A2540 0%, #00A6ED 100%); margin: 0 auto 32px; border-radius: 2px; }
        .links { display:flex; flex-direction:column; gap:12px; }
        .btn { display:block; padding: 14px 20px; border-radius: 10px; text-decoration:none; font-weight:600; font-size:14px; transition: all 0.2s; }
        .btn-primary { background: #0A2540; color: white; }
        .btn-primary:hover { background: #1A3A5F; transform: translateY(-1px); }
        .btn-secondary { background: #F6F9FC; color: #0A2540; border: 1px solid #E6EBF1; }
        .btn-secondary:hover { background: #EDF2F7; }
        .status { margin-top: 28px; padding-top: 20px; border-top: 1px solid #E6EBF1; display:flex; align-items:center; justify-content:center; gap:8px; font-size:11px; color: #8898AA; }
        .dot { width:8px; height:8px; background:#00D26A; border-radius:50%; box-shadow:0 0 0 3px rgba(0,210,106,0.15); }
        .footer { margin-top:16px; font-size:10px; letter-spacing:2px; color:#8898AA; }
    </style>
</head>
<body>
    <div class="card">
        <p class="nodo">NODO</p>
        <p class="argentina">° ARGENTINA °</p>
        <div class="line"></div>
        <div class="links">
            <a class="btn btn-primary" href="/docs">📚 Documentación API</a>
            <a class="btn btn-secondary" href="/scanner">📷 Scanner QR</a>
            <a class="btn btn-secondary" href="/qr/3a4f1471-a1a0-4c60-a7b0-0e87878f71ab">🏪 Comercio Test</a>
        </div>
        <div class="status"><div class="dot"></div> API Live V3.2 QR UNICO + BOTS • OK</div>
        <div class="footer">NODO ARGENTINA • FINTECH</div>
    </div>
</body>
</html>
    """

@app.get("/status")
def status():
    return {
        "nodo-api": "Live V3.2 QR UNICO + BOTS",
        "base_url_acordada": "https://maxshop-api.onrender.com",
        "version_diseno": "NODO azul marino + ARGENTINA celeste tech",
        "status": "OK",
        "supabase": "connected" if supabase else "no-config",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/scanner", response_class=HTMLResponse)
def scanner():
    return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NODO Scanner</title>
    <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
    <style>
        body { margin:0; font-family:Inter, sans-serif; background:#0A2540; color:white; display:flex; flex-direction:column; align-items:center; min-height:100vh; padding:20px; }
        .header { text-align:center; margin:20px 0; } .header h1 { font-size:32px; font-weight:800; letter-spacing:-2px; margin:0; } .header p { font-size:11px; letter-spacing:5px; color:#00A6ED; margin-top:4px; }
        #reader { width:100%; max-width:400px; border-radius:16px; overflow:hidden; background:white; }
        .result { margin-top:20px; background:white; color:#0A2540; padding:20px; border-radius:12px; width:100%; max-width:400px; word-break:break-all; }
        .btn { margin-top:16px; padding:12px 24px; background:white; color:#0A2540; border:none; border-radius:8px; font-weight:600; cursor:pointer; }
    </style>
</head>
<body>
    <div class="header"><h1>NODO</h1><p>° ARGENTINA ° SCANNER</p></div>
    <div id="reader"></div>
    <input type="file" id="file-input" accept="image/*" style="margin-top:20px;" />
    <div id="result" class="result" style="display:none;"></div>
    <button class="btn" onclick="startScanner()">📷 Activar Cámara</button>
    <script>
        let html5QrCode;
        function onScanSuccess(decodedText) {
            document.getElementById('result').style.display='block';
            document.getElementById('result').innerHTML = `<strong>QR:</strong><br>${decodedText}<br><br><a href="${decodedText}" target="_blank" style="color:#00A6ED;">Abrir</a>`;
            if(html5QrCode) html5QrCode.stop();
        }
        function startScanner() {
            html5QrCode = new Html5Qrcode("reader");
            html5QrCode.start({ facingMode: "environment" }, { fps: 10, qrbox: { width: 250, height: 250 } }, onScanSuccess, ()=>{}).catch(err => {
                document.getElementById('result').style.display='block';
                document.getElementById('result').innerHTML = `Error: ${err}<br>Usa archivo de imagen.`;
            });
        }
        document.getElementById('file-input').addEventListener('change', e => {
            if(e.target.files.length==0) return;
            html5QrCode = new Html5Qrcode("reader");
            html5QrCode.scanFile(e.target.files[0], true).then(onScanSuccess).catch(err => {
                document.getElementById('result').style.display='block';
                document.getElementById('result').innerHTML = `No se pudo leer: ${err}`;
            });
        });
    </script>
</body>
</html>
    """

@app.get("/qr/{comercio_id}", response_class=HTMLResponse)
def qr_info(comercio_id: str):
    comercio_data = None
    if supabase:
        try:
            res = supabase.table("comercios").select("*").eq("id", comercio_id).single().execute()
            comercio_data = res.data
        except: pass
    nombre = comercio_data.get("nombre", "Comercio NODO") if comercio_data else "Comercio NODO"
    descuento = comercio_data.get("descuento_porcentaje", 20) if comercio_data else 20
    qr_codigo = comercio_data.get("qr_unico_codigo", "NODO-") if comercio_data else "NODO-"
    return f"""
<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>{nombre} - NODO</title>
<style>body{{background:#F6F9FC;font-family:Inter,sans-serif;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:20px;}}.card{{background:white;max-width:380px;width:100%;border-radius:20px;padding:32px;box-shadow:0 20px 60px rgba(10,37,64,0.12);text-align:center;}}.nodo{{font-size:42px;font-weight:800;color:#0A2540;letter-spacing:-3px;margin:0;}}.arg{{font-size:11px;letter-spacing:5px;color:#00A6ED;font-weight:600;margin:6px 0 20px;}}.line{{width:60px;height:3px;background:linear-gradient(90deg,#0A2540,#00A6ED);margin:0 auto 24px;border-radius:2px;}}.comercio{{font-size:18px;font-weight:600;color:#0A2540;margin-bottom:6px;}}.badge{{display:inline-flex;align-items:center;gap:6px;background:#E6FCF0;color:#00A68C;padding:6px 12px;border-radius:20px;font-size:12px;font-weight:600;margin-bottom:16px;}}.descuento{{font-size:48px;font-weight:800;color:#0A2540;}}.btn{{display:block;margin-top:20px;background:#0A2540;color:white;padding:14px;border-radius:10px;text-decoration:none;font-weight:600;}}</style></head>
<body><div class="card"><p class="nodo">NODO</p><p class="arg">° ARGENTINA °</p><div class="line"></div><p class="comercio">{nombre}</p><div class="badge">● Comercio Verificado</div><p class="descuento">{descuento}<small>% OFF</small></p><p style="font-size:13px;color:#8898AA;margin-top:8px;">QR: {qr_codigo}</p><a class="btn" href="#">ESCANEA Y AHORRA - PAGAR</a><p style="font-size:10px;letter-spacing:2px;color:#8898AA;margin-top:20px;">NODO ARGENTINA • ID: {comercio_id[:8]}</p></div></body></html>
    """

@app.post("/api/generar-qr-unico-comercio")
def generar_qr_unico(req: GenerarQRReq):
    if not supabase: raise HTTPException(status_code=500, detail="Supabase no configurado")
    try:
        res = supabase.table("comercios").select("*").eq("id", req.comercio_id).single().execute()
        comercio = res.data
        if not comercio: raise HTTPException(status_code=404, detail="Comercio no encontrado")
    except Exception as e: raise HTTPException(status_code=404, detail=f"Comercio no encontrado: {e}")
    qr_actual = comercio.get("qr_unico_codigo", "")
    if qr_actual.startswith("NODO-TMP-") or not qr_actual:
        nuevo_qr = f"NODO-{str(req.comercio_id)[:8].upper()}-{str(uuid.uuid4())[:4].upper()}"
    else: nuevo_qr = qr_actual
    qr_data_url = f"https://maxshop-api.onrender.com/qr/{req.comercio_id}?code={nuevo_qr}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(qr_data_url); qr.make(fit=True)
    img = qr.make_image(fill_color="#0A2540", back_color="white").convert("RGB")
    buffered = io.BytesIO(); img.save(buffered, format="PNG")
    img_base64 = "data:image/png;base64," + base64.b64encode(buffered.getvalue()).decode()
    try: supabase.table("comercios").update({"qr_unico_codigo": nuevo_qr}).eq("id", req.comercio_id).execute()
    except: pass
    return {"status":"OK","comercio_id":req.comercio_id,"qr_unico_codigo":nuevo_qr,"qr_data":qr_data_url,"qr_imagen_base64":img_base64,"comercio":comercio.get("nombre")}

@app.post("/api/pagar-qr")
def pagar_qr(req: PagarQRReq):
    if not supabase: raise HTTPException(status_code=500, detail="Supabase no configurado")
    try: res = supabase.table("comercios").select("*").eq("id", req.comercio_id).single().execute(); comercio = res.data
    except: raise HTTPException(status_code=404, detail="Comercio no encontrado")
    if comercio.get("qr_unico_codigo") != req.qr_codigo and not req.qr_codigo.startswith("NODO-"):
        raise HTTPException(status_code=400, detail="QR inválido")
    monto = req.monto or 1000; descuento_pct = comercio.get("descuento_porcentaje", 20)
    monto_descuento = monto * (descuento_pct/100); monto_final = monto - monto_descuento
    comercio_gana = monto_final * 0.85; nodo_gana = monto_final * 0.15
    try:
        venta = {"id":str(uuid.uuid4()),"comercio_id":req.comercio_id,"usuario_id":req.usuario_id,"qr_codigo":req.qr_codigo,"monto_original":monto,"descuento_porcentaje":descuento_pct,"monto_descuento":monto_descuento,"monto_final":monto_final,"comercio_85":comercio_gana,"nodo_15":nodo_gana,"created_at":datetime.now().isoformat()}
        supabase.table("ventas").insert(venta).execute()
    except: venta={"monto_final":monto_final}
    return {"status":"PAGO OK","comercio":comercio.get("nombre"),"descuento":f"{descuento_pct}% OFF","monto_original":monto,"ahorro":monto_descuento,"monto_final":monto_final,"distribucion":{"comercio_85":comercio_gana,"nodo_15":nodo_gana},"qr":req.qr_codigo}

@app.get("/api/comercios")
def listar_comercios():
    if not supabase: return []
    try: res = supabase.table("comercios").select("*").order("created_at", desc=True).execute(); return res.data
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
