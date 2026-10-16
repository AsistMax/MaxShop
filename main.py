import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from dotenv import load_dotenv
import qrcode
import io
import base64

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

app = FastAPI(title="NODO Argentina API - V3.5 Final")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- APP ANCLADA REAL (tu index.html) ---
# Pegá aquí el contenido EXACTO que me pasaste como archivo app.html
# Por tamaño, lo cargamos desde archivo en el repo
APP_HTML_PATH = "app.html"

@app.get("/", response_class=HTMLResponse)
def root():
    return """
    <html><body style="font-family:Inter,sans-serif;padding:40px;text-align:center">
    <h1 style="font-size:42px;font-weight:800;color:#0A0A0A">NODO</h1>
    <p>ARGENTINA ° API V3.5 Live</p>
    <a href="/app" style="display:inline-block;margin-top:20px;background:#FF6B0A;color:white;padding:12px 24px;border-radius:999px;text-decoration:none;font-weight:700">Ver APP Completa → /app</a><br><br>
    <a href="/scanner" style="color:#FF6B0A">Scanner QR</a> | 
    <a href="/api/comercios" style="color:#FF6B0A">API Comercios</a>
    </body></html>
    """

@app.get("/app", response_class=HTMLResponse)
def get_app():
    if not os.path.exists(APP_HTML_PATH):
        return HTMLResponse("<h1>app.html no encontrado</h1><p>Subí el index.html que me pasaste como app.html al repo</p>", status_code=404)
    with open(APP_HTML_PATH, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/api/comercios")
def get_comercios():
    if not supabase:
        return []
    try:
        res = supabase.table("comercios").select("*").eq("activo", True).execute()
        return res.data or []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/qr/{comercio_id}", response_class=HTMLResponse)
def get_qr(comercio_id: str):
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase no configurado")
    
    comercio = supabase.table("comercios").select("*").eq("id", comercio_id).single().execute()
    if not comercio.data:
        raise HTTPException(status_code=404, detail="Comercio no encontrado")
    
    data = comercio.data
    qr_content = f"https://maxshop-api.onrender.com/qr/{comercio_id}"
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(qr_content)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0A0A0A", back_color="white")
    
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()
    
    return f"""
    <!DOCTYPE html>
    <html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>body{{font-family:Inter;background:#0A0A0A;color:white;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0}}
    .card{{background:#141414;border:1px solid #1E1E1E;border-radius:24px;padding:32px;text-align:center;max-width:360px;width:90%}}
    .qr{{background:white;padding:16px;border-radius:16px;display:inline-block;margin:20px 0;border:4px solid #FF6B0A}}
    </style></head>
    <body><div class="card">
    <h2 style="margin:0;font-size:22px">{data.get('nombre','Comercio')}</h2>
    <p style="color:#A0A0A0;font-size:12px">{data.get('categoria','')} • {comercio_id[:8]}</p>
    <div class="qr"><img src="data:image/png;base64,{img_b64}" style="width:240px;height:240px"></div>
    <p style="font-size:11px;color:#6A6A6A">QR único • Imprimible • NODO Argentina</p>
    <p style="margin-top:16px"><span style="background:#FF6B0A;color:white;padding:6px 12px;border-radius:999px;font-size:12px;font-weight:700">-{data.get('descuento_porcentaje',20)}% OFF +10% C$B</span></p>
    </div></body></html>
    """

@app.get("/scanner", response_class=HTMLResponse)
def scanner():
    return """
    <!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <script src="https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js"></script>
    <style>body{font-family:Inter;background:#0A0A0A;color:white;margin:0;padding:20px;text-align:center}
    #reader{width:100%;max-width:360px;margin:20px auto;border:2px solid #FF6B0A;border-radius:18px;overflow:hidden}
    </style></head><body>
    <h2>Scanner NODO</h2><p style="color:#A0A0A0;font-size:12px">Cámara trasera real • Permisos reales</p>
    <div id="reader"></div><div id="result" style="margin-top:20px;background:#141414;padding:16px;border-radius:12px;display:none"></div>
    <script>
    const html5QrCode = new Html5Qrcode("reader");
    html5QrCode.start({facingMode:"environment"}, {fps:10, qrbox:{width:250,height:250}},
    (decoded)=>{document.getElementById('result').style.display='block';document.getElementById('result').innerHTML='<b>QR Detectado:</b><br>'+decoded+'<br><br><a href="'+decoded+'" style="color:#FF6B0A">Abrir comercio →</a>';},
    ()=>{}).catch(e=>{document.getElementById('result').style.display='block';document.getElementById('result').innerHTML='Error cámara: '+e});
    </script></body></html>
    """
