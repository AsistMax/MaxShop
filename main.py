import os
import random
from typing import List
from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Max%Shop API", version="1.0.0")

# Crear carpeta para almacenar las imágenes subidas si no existe
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Montar la carpeta estática para que las imágenes sean visibles públicamente
app.mount("/static", StaticFiles(directory="static"), name="static")

# Base de datos en memoria inicial
DB_MOCK = {
    "socios": [
        {"dni": "33438178", "nombre": "Juan Pérez", "plan": "Familiar VIP ($5M)", "estado": "activo"}
    ],
    "comercios": [
        {
            "id": 1,
            "nombre": "Café & Bar Central",
            "categoria": "Gastronomía",
            "oferta": "20% OFF en efectivo",
            "imagen": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?w=400",
            "estado": "Aprobado"
        },
        {
            "id": 2,
            "nombre": "Moda Urbana Store",
            "categoria": "Indumentaria",
            "oferta": "3 cuotas sin interés + 15% off",
            "imagen": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400",
            "estado": "Aprobado"
        }
    ]
}

@app.get("/", response_class=HTMLResponse)
async def home(premio: str = None):
    """
    Landing Page principal de Max%Shop con la Ruleta de la Fortuna, formulario de comercios
    y la vitrina de publicidades activas.
    """
    comercios_activos = [c for c in DB_MOCK["comercios"] if c["estado"] == "Aprobado"]
    
    cards_html = ""
    for comercio in comercios_activos:
        cards_html += f"""
        <div class="card">
            <img src="{comercio.get('imagen', 'https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400')}" alt="{comercio['nombre']}" class="card-img" onerror="this.src='https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400'">
            <div class="card-body">
                <div class="badge-cat">{comercio['categoria']}</div>
                <div class="titulo-comercio">{comercio['nombre']}</div>
                <div class="oferta">🔥 {comercio['oferta']}</div>
            </div>
        </div>
        """

    resultado_html = ""
    if premio:
        resultado_html = f"""
        <div class="result-box">
            <h3>🎰 Resultado del Giro:</h3>
            <p style="font-size: 18px; color: #34d399; font-weight: bold;">{premio}</p>
        </div>
        """

    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Max%Shop - Red de Descuentos y Ruleta</title>
        <style>
            body {{ background-color: #0b0f19; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
            .logo {{ font-size: 24px; font-weight: bold; color: #fff; }}
            .logo span {{ color: #ff8c00; }}
            .nav-buttons a {{ margin-left: 10px; text-decoration: none; padding: 10px 18px; border-radius: 8px; font-weight: bold; font-size: 14px; display: inline-block; }}
            .btn-suscribir {{ background: linear-gradient(135deg, #ff8c00, #ffb347); color: #000; }}
            .btn-admin {{ background: rgba(255,255,255,0.1); color: #fff; }}
            
            /* Contenedores generales */
            .box-container {{ background: #131b2e; padding: 25px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); margin-bottom: 40px; max-width: 600px; margin-left: auto; margin-right: auto; text-align: center; }}
            .box-container h3 {{ margin-top: 0; color: #38bdf8; }}
            
            label {{ display: block; margin-top: 12px; font-size: 13px; color: #94a3b8; text-align: left; }}
            input, select {{ width: 100%; padding: 10px; margin-top: 5px; border-radius: 8px; border: 1px solid #334155; background: #0b0f19; color: #fff; box-sizing: border-box; }}
            input[type="file"] {{ padding: 8px; background: #1e293b; cursor: pointer; }}
            
            .btn-accion {{ background: #34d399; color: #000; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; margin-top: 20px; font-size: 16px; }}
            .btn-ruleta {{ background: linear-gradient(135deg, #38bdf8, #3b82f6); color: #fff; }}

            .result-box {{ background: rgba(52, 211, 153, 0.1); border: 1px solid #34d399; padding: 15px; border-radius: 8px; margin-top: 20px; }}

            /* Vitrina de comercios */
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; margin-top: 20px; }}
            .card {{ background: #131b2e; border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); text-align: left; }}
            .card-img {{ width: 100%; height: 160px; object-fit: cover; background: #1e293b; }}
            .card-body {{ padding: 20px; }}
            .badge-cat {{ background: #1e293b; color: #38bdf8; padding: 4px 10px; border-radius: 20px; font-size: 12px; display: inline-block; margin-bottom: 10px; }}
            .titulo-comercio {{ font-size: 18px; font-weight: bold; margin-bottom: 8px; }}
            .oferta {{ color: #34d399; font-size: 15px; font-weight: 500; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">Max<span>%</span>Shop</div>
            <div class="nav-buttons">
                <a href="/validar" class="btn-admin" style="background: rgba(52,211,153,0.1); color: #34d399;">Validar DNI</a>
                <a href="/admin" class="btn-admin">Panel Admin</a>
                <a href="/suscripcion" class="btn-suscribir">SUSCRIBIRME</a>
            </div>
        </div>

        <!-- Sección Ruleta de la Fortuna MaxShop -->
        <div class="box-container" style="border-color: rgba(56, 189, 248, 0.3);">
            <h3 style="color: #ff8c00;">🎡 La Ruleta de la Fortuna - MaxShop</h3>
            <p style="color: #94a3b8; font-size: 13px;">¡Gira por solo <b>$1.000</b>! Gana servicios, coberturas, descuentos o premios en efectivo especiales.</p>
            <form action="/ruleta/girar" method="POST">
                <button type="submit" class="btn-accion btn-ruleta">GIRAR RULETA ($1.000)</button>
            </form>
            {resultado_html}
        </div>

        <!-- Formulario para subir publicidades -->
        <div class="box-container" style="text-align: left;">
            <h3>¿Tienes un negocio? Sube tu publicidad gratis</h3>
            <p style="color: #94a3b8; font-size: 13px;">Puedes seleccionar una o varias imágenes de tu galería a la vez.</p>
            <form action="/comercio/publicar" method="POST" enctype="multipart/form-data">
                <label>Nombre de tu Tienda / Comercio</label>
                <input type="text" name="nombre" placeholder="Ej: Indumentaria Central" required>
                
                <label>Categoría</label>
                <select name="categoria">
                    <option value="Gastronomía">Gastronomía</option>
                    <option value="Indumentaria">Indumentaria</option>
                    <option value="Servicios">Servicios</option>
                    <option value="Tecnología">Tecnología</option>
                    <option value="Salud y Belleza">Salud y Belleza</option>
                </select>

                <label>Descripción del Descuento u Oferta</label>
                <input type="text" name="oferta" placeholder="Ej: 20% off pagando en efectivo" required>

                <label>Imágenes o Logos (Puedes seleccionar varios archivos)</label>
                <input type="file" name="imagenes_archivos" accept="image/*" multiple required>

                <button type="submit" class="btn-accion">SUBIR PUBLICIDAD</button>
            </form>
        </div>

        <h2>🛍️ Comercios y Publicidades Activas en la Red</h2>
        <div class="grid">
            {cards_html}
        </div>
    </body>
    </html>
    """)


@app.post("/ruleta/girar", response_class=HTMLResponse)
async def girar_ruleta():
    """
    Controla el giro de la ruleta mediante probabilidades matemáticas.
    Prioriza servicios, descuentos y 'seguí participando' para proteger la recaudación,
    dejando premios de dinero en efectivo de forma muy esporádica.
    """
    # Definimos los premios y su ponderación relativa (peso) para controlar el margen de la casa:
    # - Seguí participando / Servicios básicos: Mayor peso (alta probabilidad)
    # - Premios en efectivo altos: Peso muy bajo (baja probabilidad)
    premios_posibles = [
        ("¡Seguí participando! Gracias por apoyar a MaxShop.", 40),
        ("Servicio de Asesoría / Cobertura Básica bonificada", 30),
        ("Descuento Especial del 50% en Comercios Adheridos", 20),
        ("Premio en Efectivo: $5.000", 6),
        ("Premio en Efectivo: $20.000", 3),
        ("¡Premio Mayor en Efectivo: $50.000!", 0.9),
        ("¡JACKPOT MÁXIMO: $100.000!", 0.1)
    ]

    textos = [p[0] for p in premios_posibles]
    pesos = [p[1] for p in premios_posibles]

    # Elección aleatoria ponderada
    premio_obtenido = random.choices(textos, weights=pesos, k=1)[0]

    # Redirigimos de vuelta a la home pasando el premio obtenido por parámetro GET
    from fastapi.responses import RedirectResponse
    import urllib.parse
    encoded_premio = urllib.parse.quote(premio_obtenido)
    return RedirectResponse(url=f"/?premio={encoded_premio}", status_code=303)


@app.post("/comercio/publicar", response_class=HTMLResponse)
async def publicar_comercio(
    nombre: str = Form(...),
    categoria: str = Form(...),
    oferta: str = Form(...),
    imagenes_archivos: List[UploadFile] = File(...)
):
    for imagen_archivo in imagenes_archivos:
        if imagen_archivo.filename:
            file_path = os.path.join(UPLOAD_DIR, imagen_archivo.filename)
            with open(file_path, "wb") as buffer:
                content = await imagen_archivo.read()
                buffer.write(content)
            
            imagen_url = f"/static/uploads/{imagen_archivo.filename}"
            
            nuevo_id = len(DB_MOCK["comercios"]) + 1
            nuevo_comercio = {
                "id": nuevo_id,
                "nombre": nombre,
                "categoria": categoria,
                "oferta": oferta,
                "imagen": imagen_url,
                "estado": "Aprobado"
            }
            DB_MOCK["comercios"].append(nuevo_comercio)

    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Éxito - Max%Shop</title>
        <style>
            body { background-color: #0b0f19; color: #ffffff; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; text-align: center; }
            .box { background: #131b2e; padding: 30px; border-radius: 12px; width: 100%; max-width: 400px; border: 1px solid rgba(255,255,255,0.05); }
        </style>
    </head>
    <body>
        <div class="box">
            <h3 style="color: #34d399;">✔ ¡Publicidades Subidas con Éxito!</h3>
            <p style="color: #94a3b8; font-size: 14px;">Tus imágenes ya están publicadas en la vitrina del club.</p>
            <br>
            <a href="/" style="color: #38bdf8; text-decoration: none; font-weight: bold;">Volver a la vitrina</a>
        </div>
    </body>
    </html>
    """)


@app.get("/admin", response_class=HTMLResponse)
async def panel_admin():
    total_socios = len(DB_MOCK["socios"])
    total_comercios = len(DB_MOCK["comercios"])
    
    filas_comercios = ""
    for comercio in DB_MOCK["comercios"]:
        filas_comercios += f"""
                <tr>
                    <td><img src="{comercio.get('imagen', '')}" style="width: 40px; height: 40px; border-radius: 6px; object-fit: cover;" onerror="this.src='https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400'"></td>
                    <td><b>{comercio['nombre']}</b><br><span style="font-size:12px; color:#94a3b8;">{comercio['categoria']}</span></td>
                    <td>{comercio['oferta']}</td>
                    <td><span style="background: rgba(52, 211, 153, 0.1); color: #34d399; padding: 4px 8px; border-radius: 4px; font-size: 12px;">{comercio['estado']}</span></td>
                </tr>
        """

    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Panel Maestro Admin - Max%Shop</title>
        <style>
            body {{ background-color: #0b0f19; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }}
            .stat-card {{ background: #131b2e; padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.05); }}
            .stat-number {{ font-size: 28px; font-weight: bold; color: #34d399; margin-top: 5px; }}
            .section {{ background: #131b2e; padding: 20px; border-radius: 12px; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); vertical-align: middle; }}
            .btn-volver {{ color: #94a3b8; text-decoration: none; display: inline-block; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Panel Maestro Admin (Seguro)</h2>
            <a href="/" style="color: #38bdf8; text-decoration: none;">Ver Sitio Público →</a>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div>SOCIOS ACTIVOS</div>
                <div class="stat-number">{total_socios}</div>
            </div>
            <div class="stat-card">
                <div>COMERCIOS TOTALES</div>
                <div class="stat-number">{total_comercios}</div>
            </div>
            <div class="stat-card">
                <div>COBROS DEL MES</div>
                <div class="stat-number" style="color: #fb923c;">$8.450.000</div>
            </div>
        </div>

        <div class="section">
            <h3>Gestión de Comercios y Publicidades</h3>
            <table>
                <tr>
                    <th>LOGO</th>
                    <th>COMERCIO</th>
                    <th>OFERTA</th>
                    <th>ESTADO</th>
                </tr>
                {filas_comercios}
            </table>
        </div>
        <a href="/" class="btn-volver">← Volver al sitio principal</a>
    </body>
    </html>
    """)


@app.get("/validar", response_class=HTMLResponse)
async def validar_socio_form():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Validar DNI de Socio - Max%Shop</title>
        <style>
            body { background-color: #0b0f19; color: #ffffff; font-family: 'Segoe UI', sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
            .box { background: #131b2e; padding: 30px; border-radius: 12px; width: 100%; max-width: 400px; border: 1px solid rgba(255,255,255,0.05); text-align: center; }
            input { width: 100%; padding: 12px; margin: 15px 0; border-radius: 8px; border: 1px solid #334155; background: #0b0f19; color: #fff; box-sizing: border-box; }
            button { background: #34d399; color: #000; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="box">
            <h3>Validar DNI de Socio</h3>
            <form action="/validar" method="POST">
                <input type="text" name="dni" placeholder="Ej: 33438178" required>
                <button type="submit">VERIFICAR ESTADO</button>
            </form>
            <br><a href="/" style="color: #94a3b8; text-decoration: none; font-size: 13px;">← Volver al inicio</a>
        </div>
    </body>
    </html>
    """)


@app.post("/validar", response_class=HTMLResponse)
async def verificar_dni(dni: str = Form(...)):
    socio_encontrado = next((s for s in DB_MOCK["socios"] if s["dni"] == dni), None)
    
    if socio_encontrado:
        resultado = f'<span style="color: #34d399; font-weight: bold;">✔ SOCIO ACTIVO HABILITADO</span><br><b>Cliente:</b> {socio_encontrado["nombre"]}<br><b>Plan:</b> {socio_encontrado["plan"]}'
    else:
        resultado = '<span style="color: #f87171; font-weight: bold;">✖ SOCIO NO ENCONTRADO O INACTIVO</span>'

    return HTMLResponse(content=f"""
    <!DOCTYPE html>
    <html lang="es">
    <head><title>Resultado</title>
    <style>body {{ background-color: #0b0f19; color: #fff; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }} .box {{ background: #131b2e; padding: 30px; border-radius: 12px; text-align: center; max-width: 400px; width: 100%; }}</style>
    </head>
    <body>
        <div class="box">
            <h3>Resultado de Verificación</h3>
            <div style="background: rgba(255,255,255,0.03); padding: 15px; border-radius: 8px; margin-top: 15px; text-align: left;">{resultado}</div>
            <br><a href="/validar" style="color: #38bdf8; text-decoration: none;">← Consultar otro DNI</a>
        </div>
    </body>
    </html>
    """)


@app.get("/suscripcion", response_class=HTMLResponse)
async def suscripcion_page():
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="es">
    <head><title>Suscripción</title>
    <style>body { background-color: #0b0f19; color: #fff; font-family: sans-serif; text-align: center; padding-top: 50px; }</style>
    </head>
    <body>
        <h2>Únete a Max%Shop</h2>
        <p>Próximamente integración completa con Mercado Pago y Sorteos Automáticos.</p>
        <br><a href="/" style="color: #ff8c00; text-decoration: none;">Volver al inicio</a>
    </body>
    </html>
    """)
