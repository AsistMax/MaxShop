from fastapi import FastAPI, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import random
import os

app = FastAPI()
security = HTTPBasic()

# Estado general de la aplicación en memoria (configurado para persistencia de sesión)
app_state = {
    "pozo_acumulado": 400000,
    "valor_bolillero": 1000,
    "valor_ruleta": 5000,
    "limite_cobertura": 20000000,
    "historial_giros": [],
    "ultimo_giro": None,
    "ganadores_bolillero": [
        {"numero": "4821", "premio": "$250.000", "nombre": "Carlos M."},
        {"numero": "1109", "premio": "$150.000", "nombre": "Ana G."}
    ],
    "comercios": [
        {"nombre": "Supermercados León", "rubro": "Alimentos", "publicacion": "20% de descuento abonando en efectivo."},
        {"nombre": "Ferretería El Tornillo", "rubro": "Construcción", "publicacion": "15% de ahorro en toda la línea."},
        {"nombre": "Indumentaria Urban", "rubro": "Moda", "publicacion": "3 cuotas sin interés y 25% off."}
    ]
}

# Credenciales de Administrador seguras
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "maxshop2026")

def verificar_admin(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != ADMIN_USER or credentials.password != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Acceso no autorizado")
    return credentials.username

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Max% Shop - Beneficios, Bolillero y Coberturas</title>
    <!-- SDK de Mercado Pago Checkout Bricks -->
    <script src="https://sdk.mercadopago.com/js/v2"></script>
    <style>
        :root {
            --bg-dark: #070b19;
            --card-bg: #101730;
            --orange: #ff9800;
            --orange-hover: #e68900;
            --text-light: #ffffff;
            --text-gray: #b0b8c4;
            --blue-accent: #1b264f;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-light); display: flex; flex-direction: column; align-items: center; padding: 15px; }
        
        header { width: 100%; max-width: 480px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .logo-text { font-size: 22px; font-weight: bold; color: var(--text-light); }
        .logo-text span { color: var(--orange); }
        .header-actions { display: flex; gap: 8px; }
        .btn-header { background-color: var(--blue-accent); color: var(--text-light); border: 1px solid rgba(255,152,0,0.4); padding: 6px 12px; border-radius: 16px; font-size: 12px; cursor: pointer; text-decoration: none; display: flex; align-items: center; }
        .btn-participar-top { background-color: var(--orange); color: #000; font-weight: bold; padding: 6px 12px; border-radius: 16px; border: none; font-size: 12px; cursor: pointer; }

        .container { width: 100%; max-width: 480px; background-color: var(--card-bg); border-radius: 24px; padding: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); margin-bottom: 20px; text-align: center; }
        
        .main-image-container { width: 100%; border-radius: 16px; overflow: hidden; margin-bottom: 15px; }
        .main-image-container img { width: 100%; height: auto; display: block; }

        .banner-maxshop { background: linear-gradient(135deg, var(--blue-accent), var(--card-bg)); padding: 15px; margin-bottom: 20px; clip-path: polygon(12px 0%, calc(100% - 12px) 0%, 100% 12px, 100% calc(100% - 12px), calc(100% - 12px) 100%, 12px 100%, 0% calc(100% - 12px), 0% 12px); border: 1px solid rgba(255,152,0,0.4); text-align: left; display: flex; align-items: center; justify-content: space-between; }
        .banner-maxshop h3 { color: var(--orange); font-size: 16px; margin-bottom: 3px; }
        .banner-maxshop p { font-size: 12px; color: var(--text-gray); }

        .badge-club { background-color: rgba(255, 152, 0, 0.15); color: var(--orange); border: 1px solid rgba(255, 152, 0, 0.4); padding: 6px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; display: inline-block; margin-bottom: 12px; }
        
        .pozo-title { font-size: 26px; font-weight: bold; margin-bottom: 5px; }
        .pozo-monto { font-size: 34px; font-weight: bold; color: var(--orange); margin-bottom: 12px; }
        .pozo-desc { font-size: 13px; color: var(--text-gray); line-height: 1.4; margin-bottom: 15px; }
        
        .btn-primary { background-color: var(--orange); color: #000; font-weight: bold; width: 100%; padding: 14px; border-radius: 12px; border: none; cursor: pointer; font-size: 15px; margin-bottom: 10px; transition: background 0.2s; }
        .btn-primary:hover { background-color: var(--orange-hover); }

        .bolillero-3d { width: 120px; height: 120px; margin: 15px auto; border-radius: 50%; background: radial-gradient(circle at 30% 30%, #ff9800, #101730); border: 3px solid var(--orange); display: flex; align-items: center; justify-content: center; font-size: 24px; font-weight: bold; box-shadow: inset 0 0 15px rgba(0,0,0,0.8), 0 0 15px rgba(255,152,0,0.4); animation: flotar 3s ease-in-out infinite; }
        @keyframes flotar { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-6px); } }

        .comercios-section { text-align: left; margin-top: 5px; }
        .comercio-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 12px; border-radius: 12px; margin-bottom: 10px; }
        .comercio-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
        .comercio-card h4 { color: var(--orange); font-size: 14px; }
        .comercio-rubro { font-size: 10px; background: rgba(255,152,0,0.2); color: var(--orange); padding: 2px 6px; border-radius: 6px; }
        .comercio-card p { font-size: 12px; color: var(--text-gray); }

        .ruleta-box { position: relative; width: 240px; height: 240px; margin: 15px auto; border-radius: 50%; background: conic-gradient(#e74c3c 0deg 36deg, #e67e22 36deg 72deg, #f1c40f 72deg 108deg, #2ecc71 108deg 144deg, #1abc9c 144deg 180deg, #3498db 180deg 216deg, #9b59b6 216deg 252deg, #34495e 252deg 288deg, #e84393 288deg 324deg, #fdcb6e 324deg 360deg); border: 4px solid var(--orange); display: flex; align-items: center; justify-content: center; }
        .ruleta-centro { width: 55px; height: 55px; background-color: var(--bg-dark); border: 3px solid var(--orange); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px; color: var(--orange); }
        .resultado-text { font-size: 14px; font-weight: bold; color: var(--orange); margin: 12px 0; padding: 10px; background: rgba(255,152,0,0.1); border-radius: 8px; border: 1px solid rgba(255,152,0,0.3); }

        .bolillero-tabla { width: 100%; margin-top: 10px; font-size: 12px; text-align: left; border-collapse: collapse; }
        .bolillero-tabla th, .bolillero-tabla td { padding: 6px; border-bottom: 1px solid rgba(255,255,255,0.08); }
        .bolillero-tabla th { color: var(--orange); }

        footer { font-size: 11px; color: var(--text-gray); margin-top: 15px; text-align: center; }
    </style>
</head>
<body>

    <header>
        <div class="logo-text">Max <span>%</span> Shop</div>
        <div class="header-actions">
            <a href="/admin" class="btn-header">Panel Admin</a>
            <button class="btn-participar-top">PARTICIPAR</button>
        </div>
    </header>

    <!-- ETAPA 1: BOLILLERO Y POZO ACUMULADO -->
    <div class="container">
        <div class="main-image-container">
            <img src="https://images.unsplash.com/photo-1555529771-835f59fc5efe?w=500&auto=format&fit=crop&q=60" alt="Max% Shop Comunidad">
        </div>
        
        <div class="badge-club">🔥 CLUB DE BENEFICIOS Y SORTEOS SEMANALES</div>
        
        <div class="pozo-title">Pozo Acumulado</div>
        <div class="pozo-monto">${{ "{:,}".format(pozo_acumulado).replace(',', '.') }}</div>
        <div class="pozo-desc">
            Participa por el bolillero dominical de los domingos a las 19:00 hs. Valor de participación: ${{ valor_bolillero }}.
        </div>
        
        <div class="bolillero-3d">🎲</div>

        <!-- Contenedor Integrado para Mercado Pago Brick -->
        <div id="payment-brick-container" style="margin-bottom: 15px;"></div>

        <form action="/comprar_numeros" method="POST">
            <button type="submit" class="btn-primary">Pagar con Botón Rápido (${{ valor_bolillero }})</button>
        </form>

        <div style="margin-top: 15px; text-align: left;">
            <span style="font-size: 12px; font-weight: bold; color: var(--orange);">Últimos Ganadores del Bolillero:</span>
            <table class="bolillero-tabla">
                <tr><th>Nº</th><th>Premio</th><th>Socio</th></tr>
                {% ganadores_rows %}
            </table>
        </div>
    </div>

    <!-- ETAPA 2: BANNER DE MAX% SHOP -->
    <div class="container banner-maxshop">
        <div>
            <h3>Max% Shop - Descuentos de Locos</h3>
            <p>Red de beneficios directos y respaldo garantizado.</p>
        </div>
        <div style="font-size: 24px; color: var(--orange);">🛡️</div>
    </div>

    <!-- ETAPA 3: COMERCIOS Y PUBLICACIONES -->
    <div class="container">
        <div class="pozo-title" style="font-size: 20px; margin-bottom: 12px;">Comercios Adheridos</div>
        <div class="comercios-section">
            {% comercios_rows %}
        </div>
    </div>

    <!-- ETAPA 4: RULETA DE COBERTURAS -->
    <div class="container">
        <div class="pozo-title" style="font-size: 22px;">Gira por Cobertura Familiar</div>
        <div class="pozo-desc">
            Gira por ${{ valor_ruleta }} (Cobertura familiar). Límite temporal máximo: ${{ "{:,}".format(limite_cobertura).replace(',', '.') }}.
        </div>

        <form action="/girar_ruleta" method="POST">
            <button type="submit" class="btn-primary" style="background-color: #2ecc71; color: #fff;">GIRAR RULETA (${{ valor_ruleta }})</button>
        </form>

        <div class="ruleta-box">
            <div class="ruleta-centro">MAX%</div>
        </div>

        {% resultado_zona %}

        <form action="/solicitar_comprobante" method="POST">
            <button type="submit" class="btn-primary" style="background-color: #3498db; color: #fff; margin-top: 8px;">Solicitar Comprobante</button>
        </form>
    </div>

    <footer>
        Max%Shop &copy; 2026 - Catamarca (Capital), Argentina. Todos los derechos reservados.
    </footer>

    <script>
      const mp = new MercadoPago('TEST-public-key-placeholder', {
        locale: 'es-AR'
      });
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    ultimo = app_state["ultimo_giro"]
    res_html = f'<div class="resultado-text">¡Felicitaciones! Obtuviste {ultimo} en tu póliza familiar.</div>' if ultimo else ""
    
    ganadores_html = ""
    for g in app_state["ganadores_bolillero"]:
        ganadores_html += f"<tr><td>{g['numero']}</td><td>{g['premio']}</td><td>{g['nombre']}</td></tr>"
        
    comercios_html = ""
    for c in app_state["comercios"]:
        comercios_html += f"""
        <div class="comercio-card">
            <div class="comercio-header">
                <h4>{c['nombre']}</h4>
                <span class="comercio-rubro">{c['rubro']}</span>
            </div>
            <p>{c['publicacion']}</p>
        </div>
        """
    
    html = HTML_TEMPLATE.replace("{pozo_acumulado}", str(app_state["pozo_acumulado"]))
    html = html.replace("{valor_bolillero}", str(app_state["valor_bolillero"]))
    html = html.replace("{valor_ruleta}", str(app_state["valor_ruleta"]))
    html = html.replace("{limite_cobertura}", str(app_state["limite_cobertura"]))
    html = html.replace("{% ganadores_rows %}", ganadores_html)
    html = html.replace("{% comercios_rows %}", comercios_html)
    html = html.replace("{% resultado_zona %}", res_html)
    
    return HTMLResponse(content=html)

@app.post("/comprar_numeros")
async def comprar_numeros():
    return RedirectResponse(url="/", status_code=303)

@app.post("/girar_ruleta")
async def girar_ruleta():
    montos = ["$2.000.000", "$5.000.000", "$10.000.000", "$15.000.000", f"${app_state['limite_cobertura']:,}".replace(',', '.')]
    giro = random.choice(montos)
    app_state["historial_giros"].append(giro)
    app_state["ultimo_giro"] = giro
    return RedirectResponse(url="/", status_code=303)

@app.post("/solicitar_comprobante")
async def solicitar_comprobante():
    if app_state["historial_giros"]:
        def parse_monto(m):
            return int(m.replace('$', '').replace('.', ''))
        app_state["ultimo_giro"] = max(app_state["historial_giros"], key=parse_monto)
    return RedirectResponse(url="/", status_code=303)

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(user: str = Depends(verificar_admin)):
    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Panel Admin - Max% Shop</title>
        <style>
            body {{ background: #070b19; color: #fff; font-family: sans-serif; padding: 20px; display: flex; justify-content: center; }}
            .card {{ background: #101730; padding: 20px; border-radius: 12px; width: 100%; max-width: 400px; border: 1px solid #ff9800; }}
            input, button {{ width: 100%; padding: 10px; margin-top: 10px; border-radius: 8px; border: none; }}
            button {{ background: #ff9800; font-weight: bold; cursor: pointer; }}
            a {{ color: #ff9800; display: block; margin-top: 15px; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Panel de Control Admin</h2>
            <form action="/admin/actualizar" method="POST">
                <label>Pozo Acumulado ($):</label>
                <input type="number" name="pozo" value="{app_state['pozo_acumulado']}">
                
                <label>Límite Cobertura Ruleta ($):</label>
                <input type="number" name="limite" value="{app_state['limite_cobertura']}">
                
                <button type="submit">Actualizar Valores</button>
            </form>
            <a href="/">Volver al Inicio</a>
        </div>
    </body>
    </html>
    """)

@app.post("/admin/actualizar")
async def admin_actualizar(pozo: int = Form(...), limite: int = Form(...), user: str = Depends(verificar_admin)):
    app_state["pozo_acumulado"] = pozo
    app_state["limite_cobertura"] = limite
    return RedirectResponse(url="/admin", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
