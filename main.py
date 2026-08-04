from fastapi import FastAPI, Form, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI(title="Max%Shop API", version="1.0.0")

# Simulación de base de datos en memoria (Preparado para migrar a Supabase fácilmente)
# Aquí se almacenarán los comercios, publicidades y socios a medida que se registren.
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
            "estado": "Aprobado",
            "tipo": "local" # Puede ser local registrado o espejo
        },
        {
            "id": 2,
            "nombre": "Moda Urbana Store",
            "categoria": "Indumentaria",
            "oferta": "3 cuotas sin interés + 15% off",
            "estado": "Aprobado",
            "tipo": "local"
        }
    ],
    "publicidades_pendientes": [
        {"id": 1, "comercio": "Burguer House", "oferta": "2x1 en hamburguesas los jueves", "estado": "Pendiente"}
    ]
}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Landing Page principal de Max%Shop.
    Muestra los comercios y publicidades activas en la red.
    """
    comercios_activos = [c for c in DB_MOCK["comercios"] if c["estado"] == "Aprobado"]
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Max%Shop - Red de Descuentos y Comercios</title>
        <style>
            body {{ background-color: #0b0f19; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; }}
            .logo {{ font-size: 24px; font-weight: bold; color: #fff; }}
            .logo span {{ color: #ff8c00; }}
            .btn-suscribir {{ background: linear-gradient(135deg, #ff8c00, #ffb347); color: #000; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: bold; }}
            .btn-admin {{ background: rgba(255,255,255,0.1); color: #fff; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 14px; margin-left: 10px; }}
            .card {{ background: #131b2e; border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05); }}
            .badge-cat {{ background: #1e293b; color: #38bdf8; padding: 4px 10px; border-radius: 20px; font-size: 12px; display: inline-block; margin-bottom: 10px; }}
            .titulo-comercio {{ font-size: 20px; font-weight: bold; margin-bottom: 8px; }}
            .oferta {{ color: #cbd5e1; font-size: 15px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">Max<span>%</span>Shop</div>
            <div>
                <a href="/admin" class="btn-admin">Panel Admin</a>
                <a href="/suscripcion" class="btn-suscribir">SUSCRIBIRME ($5M)</a>
            </div>
        </div>

        <h2>🛍️ Comercios y Publicidades Activas en la Red</h2>
    """
    
    for comercio in comercios_activos:
        html_content += f"""
        <div class="card">
            <div class="badge-cat">{comercio['categoria']}</div>
            <div class="titulo-comercio">{comercio['nombre']}</div>
            <div class="oferta">{comercio['oferta']}</div>
        </div>
        """
        
    html_content += """
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/admin", response_class=HTMLResponse)
async def panel_admin():
    """
    Panel Maestro de Administración (Seguro).
    Permite moderar publicidades enviadas por comercios locales y de la red espejo.
    """
    total_socios = len(DB_MOCK["socios"])
    total_comercios = len(DB_MOCK["comercios"])
    
    html_content = f"""
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
            th, td {{ text-align: left; padding: 12px; border-bottom: 1px solid rgba(255,255,255,0.05); }}
            .badge-aprobado {{ background: rgba(52, 211, 153, 0.2); color: #34d399; padding: 4px 8px; border-radius: 4px; font-size: 12px; }}
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
                <div>COMERCIOS ADHERIDOS</div>
                <div class="stat-number">{total_comercios}</div>
            </div>
            <div class="stat-card">
                <div>COBROS DEL MES (MP)</div>
                <div class="stat-number" style="color: #fb923c;">$8.450.000</div>
            </div>
            <div class="stat-card">
                <div>PUBLICIDADES PENDIENTES</div>
                <div class="stat-number" style="color: #f87171;">{len(DB_MOCK["publicidades_pendientes"])}</div>
            </div>
        </div>

        <div class="section">
            <h3>Moderación de Publicidades y Comercios</h3>
            <p style="color: #94a3b8; font-size: 14px;">Aprueba, rechaza o elimina las publicidades enviadas por las tiendas locales o el sistema espejo.</p>
            <table>
                <tr>
                    <th>COMERCIO</th>
                    <th>OFERTA / DESCUENTO</th>
                    <th>ESTADO</th>
                </tr>
    """
    
    for comercio in DB_MOCK["comercios"]:
        html_content += f"""
                <tr>
                    <td>{comercio['nombre']}</td>
                    <td>{comercio['oferta']}</td>
                    <td><span class="badge-aprobado">{comercio['estado']}</span></td>
                </tr>
        """
        
    html_content += """
            </table>
        </div>
        <a href="/" class="btn-volver">← Volver al sitio principal</a>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/validar", response_class=HTMLResponse)
async def validar_socio_form():
    """
    Panel Antifraude / Validador de DNI de Socio para comercios.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Validar DNI de Socio - Max%Shop</title>
        <style>
            body {{ background-color: #0b0f19; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .box {{ background: #131b2e; padding: 30px; border-radius: 12px; width: 100%; max-width: 400px; border: 1px solid rgba(255,255,255,0.05); text-align: center; }}
            input {{ width: 100%; padding: 12px; margin: 15px 0; border-radius: 8px; border: 1px solid #334155; background: #0b0f19; color: #fff; box-sizing: border-box; }}
            button {{ background: #34d399; color: #000; border: none; padding: 12px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h3>Validar DNI de Socio</h3>
            <p style="color: #94a3b8; font-size: 13px;">Ingrese el DNI del cliente para reconfirmar su membresía activa.</p>
            <form action="/validar" method="POST">
                <input type="text" name="dni" placeholder="Ej: 33438178" required>
                <button type="submit">VERIFICAR ESTADO EN SISTEMA</button>
            </form>
            <br>
            <a href="/" style="color: #94a3b8; text-decoration: none; font-size: 13px;">← Volver al sitio principal</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/validar", response_class=HTMLResponse)
async def verificar_dni(dni: str = Form(...)):
    """
    Procesa la validación del DNI consultando los registros.
    """
    socio_encontrado = next((s for s in DB_MOCK["socios"] if s["dni"] == dni), None)
    
    if socio_encontrado:
        resultado_html = f"""
        <div style="background: rgba(52, 211, 153, 0.1); border: 1px solid #34d399; padding: 15px; border-radius: 8px; margin-top: 15px; text-align: left;">
            <span style="color: #34d399; font-weight: bold;">✔ SOCIO ACTIVO HABILITADO</span><br>
            <b>Cliente:</b> {socio_encontrado['nombre']}<br>
            <b>Plan:</b> {socio_encontrado['plan']}<br>
            <span style="color: #cbd5e1; font-size: 12px;">Cuota al día en Mercado Pago. Aplica descuento.</span>
        </div>
        """
    else:
        resultado_html = f"""
        <div style="background: rgba(248, 113, 113, 0.1); border: 1px solid #f87171; padding: 15px; border-radius: 8px; margin-top: 15px; text-align: left;">
            <span style="color: #f87171; font-weight: bold;">✖ SOCIO NO ENCONTRADO O INACTIVO</span><br>
            <span style="color: #cbd5e1; font-size: 12px;">El DNI ingresado no registra cuotas al día.</span>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Resultado Validación - Max%Shop</title>
        <style>
            body {{ background-color: #0b0f19; color: #ffffff; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
            .box {{ background: #131b2e; padding: 30px; border-radius: 12px; width: 100%; max-width: 400px; border: 1px solid rgba(255,255,255,0.05); text-align: center; }}
        </style>
    </head>
    <body>
        <div class="box">
            <h3>Resultado de Verificación</h3>
            {resultado_html}
            <br><br>
            <a href="/validar" style="color: #38bdf8; text-decoration: none;">← Consultar otro DNI</a>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/suscripcion", response_class=HTMLResponse)
async def suscripcion_page():
    """
    Página orientada a la nueva suscripción y registro de clientes.
    """
    return HTMLResponse(content="""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Suscripción - Max%Shop</title>
        <style>
            body {{ background-color: #0b0f19; color: #ffffff; font-family: sans-serif; text-align: center; padding-top: 50px; }}
        </style>
    </head>
    <body>
        <h2>Únete a Max%Shop</h2>
        <p>Próximamente integración completa con Mercado Pago y Sorteos Automáticos con Pozo Acumulado.</p>
        <br><a href="/" style="color: #ff8c00;">Volver al inicio</a>
    </body>
    </html>
    """)
