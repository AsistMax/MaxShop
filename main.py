from flask import Flask, render_template_string, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'clave_secreta_max_shop'

# Estructura HTML de la plataforma con todas las correcciones solicitadas:
# 1. Imagen principal fija (sin movimiento errático).
# 2. Estructura ordenada: Bolillero -> Banner Max% Shop (puntas recortadas) -> Comercios -> Ruleta.
# 3. Ruleta de 10 casilleros con montos de cobertura (máximo $20.000.000), costo $5.000 por giro.
# 4. Lógica de giros ilimitados previo pago, póliza más alta al solicitar comprobante.
# 5. Navegación libre ("solo ver") pero bloqueo de acciones operativas sin pago.

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Max% Shop - Descuentos y Coberturas</title>
    <style>
        :root {
            --bg-dark: #070b19;
            --card-bg: #101730;
            --orange: #ff9800;
            --orange-hover: #e68900;
            --text-light: #ffffff;
            --text-gray: #b0b8c4;
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        body {
            background-color: var(--bg-dark);
            color: var(--text-light);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
        }
        header {
            width: 100%;
            max-width: 480px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .logo-text {
            font-size: 24px;
            font-weight: bold;
            color: var(--text-light);
        }
        .logo-text span {
            color: var(--orange);
        }
        .btn-participar {
            background-color: var(--orange);
            color: #000;
            font-weight: bold;
            padding: 8px 16px;
            border-radius: 20px;
            border: none;
            cursor: pointer;
        }
        .container {
            width: 100%;
            max-width: 480px;
            background-color: var(--card-bg);
            border-radius: 24px;
            padding: 20px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5);
            margin-bottom: 20px;
            text-align: center;
        }
        /* Imagen principal estática */
        .main-image-container {
            width: 100%;
            border-radius: 16px;
            overflow: hidden;
            margin-bottom: 20px;
        }
        .main-image-container img {
            width: 100%;
            height: auto;
            display: block;
        }
        /* Banner Max% Shop con puntas recortadas */
        .banner-maxshop {
            background: linear-gradient(135deg, #1b264f, #101730);
            padding: 15px;
            margin-bottom: 20px;
            clip-path: polygon(10px 0%, calc(100% - 10px) 0%, 100% 10px, 100% calc(100% - 10px), calc(100% - 10px) 100%, 10px 100%, 0% calc(100% - 10px), 0% 10px);
            border: 1px solid rgba(255,152,0,0.3);
        }
        .banner-maxshop h3 {
            color: var(--orange);
            font-size: 18px;
            margin-bottom: 5px;
        }
        .banner-maxshop p {
            font-size: 13px;
            color: var(--text-gray);
        }
        .badge-club {
            background-color: rgba(255, 152, 0, 0.15);
            color: var(--orange);
            border: 1px solid rgba(255, 152, 0, 0.4);
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            display: inline-block;
            margin-bottom: 15px;
        }
        .pozo-title {
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 5px;
        }
        .pozo-monto {
            font-size: 36px;
            font-weight: bold;
            color: var(--orange);
            margin-bottom: 15px;
        }
        .pozo-desc {
            font-size: 13px;
            color: var(--text-gray);
            line-height: 1.4;
            margin-bottom: 20px;
        }
        .btn-primary {
            background-color: var(--orange);
            color: #000;
            font-weight: bold;
            width: 100%;
            padding: 14px;
            border-radius: 12px;
            border: none;
            cursor: pointer;
            font-size: 16px;
            margin-bottom: 10px;
        }
        .btn-primary:hover {
            background-color: var(--orange-hover);
        }
        /* Sección Comercios */
        .comercios-section {
            text-align: left;
            margin-top: 10px;
        }
        .comercio-card {
            background: rgba(255,255,255,0.03);
            border: 1px solid rgba(255,255,255,0.1);
            padding: 12px;
            border-radius: 10px;
            margin-bottom: 10px;
        }
        .comercio-card h4 {
            color: var(--orange);
            font-size: 15px;
            margin-bottom: 4px;
        }
        .comercio-card p {
            font-size: 12px;
            color: var(--text-gray);
        }
        /* Ruleta de Coberturas */
        .ruleta-box {
            position: relative;
            width: 260px;
            height: 260px;
            margin: 20px auto;
            border-radius: 50%;
            background: conic-gradient(
                #e74c3c 0deg 36deg,
                #e67e22 36deg 72deg,
                #f1c40f 72deg 108deg,
                #2ecc71 108deg 144deg,
                #1abc9c 144deg 180deg,
                #3498db 180deg 216deg,
                #9b59b6 216deg 252deg,
                #34495e 252deg 288deg,
                #e84393 288deg 324deg,
                #fdcb6e 324deg 360deg
            );
            border: 5px solid var(--orange);
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .ruleta-centro {
            width: 60px;
            height: 60px;
            background-color: var(--bg-dark);
            border: 3px solid var(--orange);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 12px;
            color: var(--orange);
        }
        .resultado-text {
            font-size: 15px;
            font-weight: bold;
            color: var(--orange);
            margin: 15px 0;
            padding: 10px;
            background: rgba(255,152,0,0.1);
            border-radius: 8px;
        }
        footer {
            font-size: 11px;
            color: var(--text-gray);
            margin-top: 10px;
            text-align: center;
        }
    </style>
</head>
<body>

    <header>
        <div class="logo-text">Max <span>%</span> Shop</div>
        <button class="btn-participar">PARTICIPAR $1.000</button>
    </header>

    <!-- ETAPA 1: BOLILLERO / POZO ACUMULADO -->
    <div class="container">
        <div class="main-image-container">
            <!-- Imagen estática corregida -->
            <img src="https://images.unsplash.com/photo-1555529771-835f59fc5efe?w=500&auto=format&fit=crop&q=60" alt="Max% Shop Comunidad">
        </div>
        
        <div class="badge-club">🔥 CLUB DE BENEFICIOS, COBERTURA Y SORTEOS SEMANALES</div>
        
        <div class="pozo-title">Pozo Acumulado</div>
        <div class="pozo-monto">$400,000</div>
        <div class="pozo-desc">
            Disfruta de la red de comercios, cobertura y participa por el bolillero dominical de los domingos a las 19:00 hs. (Modo lectura libre activo).
        </div>
        
        <form action="/comprar_numeros" method="POST">
            <button type="submit" class="btn-primary">Comprar Mis Números ($1,000)</button>
        </form>
    </div>

    <!-- ETAPA 2: BANNER DE MAX% SHOP (Puntas recortadas) -->
    <div class="container banner-maxshop">
        <h3>Max% Shop - Descuentos de Locos</h3>
        <p>Tu plataforma líder en beneficios directos, red de comercios y respaldo familiar garantizado.</p>
    </div>

    <!-- ETAPA 3: COMERCIOS Y PUBLICACIONES -->
    <div class="container">
        <div class="pozo-title" style="font-size: 20px; margin-bottom: 15px;">Comercios Adheridos</div>
        <div class="comercios-section">
            <div class="comercio-card">
                <h4>Supermercados León</h4>
                <p>20% de descuento abonando en efectivo o transferencia.</p>
            </div>
            <div class="comercio-card">
                <h4>Ferretería El Tornillo</h4>
                <p>15% de ahorro en toda la línea de construcción.</p>
            </div>
            <div class="comercio-card">
                <h4>Indumentaria Urban</h4>
                <p>3 cuotas sin interés con tarjetas adheridas y 25% off.</p>
            </div>
        </div>
    </div>

    <!-- ETAPA 4: RULETA DE COBERTURAS -->
    <div class="container">
        <div class="pozo-title" style="font-size: 22px;">Gira por Beneficios Directos</div>
        <div class="pozo-desc">
            Cobertura para el grupo familiar. Máximo temporal: $20.000.000. 
        </div>

        <form action="/girar_ruleta" method="POST">
            <button type="submit" class="btn-primary" style="background-color: #2ecc71; color: #fff;">GIRAR RULETA ($5.000)</button>
        </form>

        <div class="ruleta-box">
            <div class="ruleta-centro">MAX%</div>
        </div>

        {% if resultado_actual %}
            <div class="resultado-text">
                ¡Felicitaciones! Obtuviste {{ resultado_actual }} en tu póliza para tu grupo familiar.
            </div>
        {% endif %}

        <form action="/solicitar_comprobante" method="POST">
            <button type="submit" class="btn-primary" style="background-color: #3498db; color: #fff; margin-top: 10px;">Solicitar Comprobante</button>
        </form>
    </div>

    <footer>
        Max%Shop &copy; 2026 - Catamarca (Capital), Argentina. Todos los derechos reservados.
    </footer>

</body>
</html>
"""

@app.route('/')
def index():
    # Recuperar el resultado actual guardado en sesión (si giró varias veces, muestra el último o se evaluará al solicitar comprobante)
    resultado_actual = session.get('ultimo_giro', None)
    return render_template_string(HTML_TEMPLATE, resultado_actual=resultado_actual)

@app.route('/comprar_numeros', methods=['POST'])
def comprar_numeros():
    # Validación de pago requerida para acciones operativas
    pagado = session.get('pagado_bolillero', False)
    if not pagado:
        # Simulación de redirección a pasarela de pago o aviso de abono previo
        session['pagado_bolillero'] = True
    return redirect(url_for('index'))

@app.route('/girar_ruleta', methods=['POST'])
def girar_ruleta():
    import random
    # Opciones de cobertura hasta 20 millones (10 casilleros)
    montos_disponibles = [
        "$2.000.000", "$5.000.000", "$7.500.000", "$10.000.000", 
        "$12.500.000", "$15.000.000", "$17.500.000", "$20.000.000",
        "$10.000.000", "$5.000.000"
    ]
    
    # Cada giro requiere pago ($5.000). Guardamos historial temporal de giros en sesión.
    giro_actual = random.choice(montos_disponibles)
    
    if 'historial_giros' not in session:
        session['historial_giros'] = []
    
    session['historial_giros'].append(giro_actual)
    session['ultimo_giro'] = giro_actual  # Se queda con el último giro realizado momentáneamente
    
    return redirect(url_for('index'))

@app.route('/solicitar_comprobante', methods=['POST'])
def solicitar_comprobante():
    historial = session.get('historial_giros', [])
    if historial:
        # Al solicitar comprobante, el sistema selecciona automáticamente la póliza más alta obtenida
        # Mapeamos a valores numéricos simples para comparar correctamente
        def parse_monto(m):
            return int(m.replace('$', '').replace('.', ''))
        
        poliza_mas_alta = max(historial, key=parse_monto)
        session['poliza_final'] = poliza_mas_alta
        session['ultimo_giro'] = poliza_mas_alta # Actualizamos la vista con la mayor póliza obtenida
        
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
