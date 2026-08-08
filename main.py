from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
import random

app = FastAPI()

# Almacenamiento en memoria para simular sesiones y datos de la app completa
app_state = {
    "usuario_registrado": False,
    "rol_actual": "Cliente / Socio",
    "pagado_bolillero": False,
    "historial_giros": [],
    "ultimo_giro": None,
    "comercios": [
        {"nombre": "Supermercados León", "rubro": "Alimentos y Supermercados", "publicacion": "20% de descuento abonando en efectivo o transferencia."},
        {"nombre": "Ferretería El Tornillo", "rubro": "Construcción y Hogar", "publicacion": "15% de ahorro en toda la línea de materiales."},
        {"nombre": "Indumentaria Urban", "rubro": "Moda y Calzado", "publicacion": "3 cuotas sin interés y 25% off con tarjetas adheridas."},
        {"nombre": "Gastronomía Don Aldo", "rubro": "Restaurantes", "publicacion": "2x1 en menú ejecutivo todos los mediodías."}
    ],
    "ganadores_bolillero": [
        {"numero": "4821", "premio": "$250.000", "nombre": "Carlos M."},
        {"numero": "1109", "premio": "$150.000", "nombre": "Ana G."}
    ]
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Max% Shop - Descuentos, Bolillero y Coberturas</title>
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
        .btn-header { background-color: var(--blue-accent); color: var(--text-light); border: 1px solid rgba(255,152,0,0.4); padding: 6px 12px; border-radius: 16px; font-size: 12px; cursor: pointer; }
        .btn-participar-top { background-color: var(--orange); color: #000; font-weight: bold; padding: 6px 12px; border-radius: 16px; border: none; font-size: 12px; cursor: pointer; }

        .container { width: 100%; max-width: 480px; background-color: var(--card-bg); border-radius: 24px; padding: 20px; box-shadow: 0 8px 24px rgba(0,0,0,0.5); margin-bottom: 20px; text-align: center; }
        
        /* Imagen principal estática */
        .main-image-container { width: 100%; border-radius: 16px; overflow: hidden; margin-bottom: 15px; }
        .main-image-container img { width: 100%; height: auto; display: block; }

        /* Banner Max% Shop con puntas recortadas */
        .banner-maxshop { background: linear-gradient(135deg, var(--blue-accent), var(--card-bg)); padding: 15px; margin-bottom: 20px; clip-path: polygon(12px 0%, calc(100% - 12px) 0%, 100% 12px, 100% calc(100% - 12px), calc(100% - 12px) 100%, 12px 100%, 0% calc(100% - 12px), 0% 12px); border: 1px solid rgba(255,152,0,0.4); text-align: left; display: flex; align-items: center; justify-content: space-between; }
        .banner-maxshop h3 { color: var(--orange); font-size: 16px; margin-bottom: 3px; }
        .banner-maxshop p { font-size: 12px; color: var(--text-gray); }

        .badge-club { background-color: rgba(255, 152, 0, 0.15); color: var(--orange); border: 1px solid rgba(255, 152, 0, 0.4); padding: 6px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; display: inline-block; margin-bottom: 12px; }
        
        .pozo-title { font-size: 26px; font-weight: bold; margin-bottom: 5px; }
        .pozo-monto { font-size: 34px; font-weight: bold; color: var(--orange); margin-bottom: 12px; }
        .pozo-desc { font-size: 13px; color: var(--text-gray); line-height: 1.4; margin-bottom: 15px; }
        
        .btn-primary { background-color: var(--orange); color: #000; font-weight: bold; width: 100%; padding: 14px; border-radius: 12px; border: none; cursor: pointer; font-size: 15px; margin-bottom: 10px; }
        .btn-primary:hover { background-color: var(--orange-hover); }

        /* Sección Comercios y Publicaciones */
        .comercios-section { text-align: left; margin-top: 5px; }
        .comercio-card { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); padding: 12px; border-radius: 12px; margin-bottom: 10px; }
        .comercio-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px; }
        .comercio-card h4 { color: var(--orange); font-size: 14px; }
        .comercio-rubro { font-size: 10px; background: rgba(255,152,0,0.2); color: var(--orange); padding: 2px 6px; border-radius: 6px; }
        .comercio-card p { font-size: 12px; color: var(--text-gray); }

        /* Ruleta de Coberturas */
        .ruleta-box { position: relative; width: 240px; height: 240px; margin: 15px auto; border-radius: 50%; background: conic-gradient(#e74c3c 0deg 36deg, #e67e22 36deg 72deg, #f1c40f 72deg 108deg, #2ecc71 108deg 144deg, #1abc9c 144deg 180deg, #3498db 180deg 216deg, #9b59b6 216deg 252deg, #34495e 252deg 288deg, #e84393 288deg 324deg, #fdcb6e 324deg 360deg); border: 4px solid var(--orange); display: flex; align-items: center; justify-content: center; }
        .ruleta-centro { width: 55px; height: 55px; background-color: var(--bg-dark); border: 3px solid var(--orange); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 11px; color: var(--orange); }
        .resultado-text { font-size: 14px; font-weight: bold; color: var(--orange); margin: 12px 0; padding: 10px; background: rgba(255,152,0,0.1); border-radius: 8px; border: 1px solid rgba(255,152,0,0.3); }

        /* Sección Bolillero Historial */
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
            <button class="btn-header">Accesos y Roles</button>
            <button class="btn-participar-top">PARTICIPAR $1.000</button>
        </div>
    </header>

    <!-- ETAPA 1: BOLILLERO Y POZO ACUMULADO -->
    <div class="container">
        <div class="main-image-container">
            <!-- Imagen estática corregida -->
            <img src="https://images.unsplash.com/photo-1555529771-835f59fc5efe?w=500&auto=format&fit=crop&q=60" alt="Max% Shop Comunidad">
        </div>
        
        <div class="badge-club">🔥 CLUB DE BENEFICIOS, COBERTURA Y SORTEOS SEMANALES</div>
        
        <div class="pozo-title">Pozo Acumulado</div>
        <div class="pozo-monto">$400,000</div>
        <div class="pozo-desc">
            Disfruta de la red de comercios, cobertura y participa por el bolillero dominical de los domingos a las 19:00 hs. (Modo navegación libre activo).
        </div>
        
        <form action="/comprar_numeros" method="POST">
            <button type="submit" class="btn-primary">Comprar Mis Números ($1,000)</button>
        </form>

        <div style="margin-top: 15px; text-align: left;">
            <span style="font-size: 12px; font-weight: bold; color: var(--orange);">Últimos Ganadores del Bolillero:</span>
            <table class="bolillero-tabla">
                <tr><th>Nº</th><th>Premio</th><th>Socio</th></tr>
                <tr><td>4821</td><td>$250.000</td><td>Carlos M.</td></tr>
                <tr><td>1109</td><td>$150.000</td><td>Ana G.</td></tr>
            </table>
        </div>
    </div>

    <!-- ETAPA 2: BANNER DE MAX% SHOP (Puntas recortadas) -->
    <div class="container banner-maxshop">
        <div>
            <h3>Max% Shop - Descuentos de Locos</h3>
            <p>Red de beneficios directos y respaldo garantizado.</p>
        </div>
        <div style="font-size: 24px; color: var(--orange);">🛡️</div>
    </div>

    <!-- ETAPA 3: COMERCIOS Y PUBLICACIONES -->
    <div class="container">
        <div class="pozo-title" style="font-size: 20px; margin-bottom: 12px;">Comercios y Publicaciones</div>
        <div class="comercios-section">
            {% for comercio in comercios %}
            <div class="comercio-card">
                <div class="comercio-header">
                    <h4>{{ comercio.nombre }}</h4>
                    <span class="comercio-rubro">{{ comercio.rubro }}</span>
                </div>
                <p>{{ comercio.publicacion }}</p>
            </div>
            {% endfor %}
        </div>
    </div>

    <!-- ETAPA 4: RULETA DE COBERTURAS -->
    <div class="container">
        <div class="pozo-title" style="font-size: 22px;">Gira por Cobertura Familiar</div>
        <div class="pozo-desc">
            Gira por $5.000 (Cobertura para el grupo familiar). Límite temporal: hasta $20.000.000. Navegación libre habilitada (puedes ver sin costo, pago requerido solo al girar).
        </div>

        <form action="/girar_ruleta" method="POST">
            <button type="submit" class="btn-primary" style="background-color: #2ecc71; color: #fff;">GIRAR RULETA ($5.000)</button>
        </form>

        <div class="ruleta-box">
            <div class="ruleta-centro">MAX%</div>
        </div>

        RESULTADO_ZONA

        <form action="/solicitar_comprobante" method="POST">
            <button type="submit" class="btn-primary" style="background-color: #3498db; color: #fff; margin-top: 8px;">Solicitar Comprobante</button>
        </form>
    </div>

    <footer>
        Max%Shop &copy; 2026 - Catamarca (Capital), Argentina. Todos los derechos reservados.
    </footer>

</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def index():
    ultimo = app_state["ultimo_giro"]
    if ultimo:
        res_html = f'<div class="resultado-text">¡Felicitaciones! Obtuviste {ultimo} en tu póliza para tu grupo familiar.</div>'
    else:
        res_html = ""
    
    # Renderizamos pasando la lista completa de comercios y el resultado de la ruleta
    page_content = HTML_TEMPLATE
    
    # Inyectar comercios dinámicamente
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
    page_content = page_content.replace("{% for comercio in comercios %}\n            <div class=\"comercio-card\">\n                <div class=\"comercio-header\">\n                    <h4>{{ comercio.nombre }}</h4>\n                    <span class=\"comercio-rubro\">{{ comercio.rubro }}</span>\n                </div>\n                <p>{{ comercio.publicacion }}</p>\n            </div>\n            {% endfor %}", comercios_html)
    
    page_content = page_content.replace("RESULTADO_ZONA", res_html)
    return HTMLResponse(content=page_content)

@app.post("/comprar_numeros")
async def comprar_numeros():
    app_state["pagado_bolillero"] = True
    return RedirectResponse(url="/", status_code=303)

@app.post("/girar_ruleta")
async def girar_ruleta():
    # 10 casilleros con progresión hasta $20.000.000 máximos temporales
    montos_cobertura = [
        "$2.000.000", "$5.000.000", "$7.500.000", "$10.000.000", 
        "$12.500.000", "$15.000.000", "$17.500.000", "$20.000.000",
        "$10.000.000", "$5.000.000"
    ]
    giro_actual = random.choice(montos_cobertura)
    app_state["historial_giros"].append(giro_actual)
    app_state["ultimo_giro"] = giro_actual
    return RedirectResponse(url="/", status_code=303)

@app.post("/solicitar_comprobante")
async def solicitar_comprobante():
    historial = app_state["historial_giros"]
    if historial:
        def parse_monto(m):
            return int(m.replace('$', '').replace('.', ''))
        # Criterio: Se queda con la póliza más alta obtenida tras los giros realizados
        poliza_mas_alta = max(historial, key=parse_monto)
        app_state["ultimo_giro"] = poliza_mas_alta
    return RedirectResponse(url="/", status_code=303)
