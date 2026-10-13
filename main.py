from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import uuid
from datetime import datetime

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# ============== KEYS ADM ==============
ADM_KEYS_RAW = ["AsistMax2026", "AsistMax2026!"]
ADM_KEYS = [k.strip().lower() for k in ADM_KEYS_RAW]

# ============== DB FICTICIA EN MEMORIA ==============
USUARIOS = {}
QR_CODES = {}

# ============== TAREAS BASE CON COORDS REALES ==============
TAREAS_BASE = [
    # CATAMARCA -29 a -27 / -66.5 a -65
    {"id": "cat-1", "titulo": "Retiro en efectivo - Centro", "region": "Catamarca", "lat": -28.4696, "lng": -65.7792, "direccion": "Sarmiento 550, San Fernando del Valle", "pago": 1200, "tipo": "retiro"},
    {"id": "cat-2", "titulo": "Entrega paquete - Alto Fariñango", "region": "Catamarca", "lat": -28.4395, "lng": -65.8012, "direccion": "Av. Belgrano 1500", "pago": 950, "tipo": "entrega"},
    {"id": "cat-3", "titulo": "Compra verificada - Supermercado", "region": "Catamarca", "lat": -28.4709, "lng": -65.7850, "direccion": "República 450", "pago": 1800, "tipo": "compra"},
    # BUENOS AIRES -35.2 a -34.3 / -58.7 a -58.2
    {"id": "bsas-1", "titulo": "Retiro CABA - Microcentro", "region": "Buenos Aires", "lat": -34.6037, "lng": -58.3816, "direccion": "Florida 100, CABA", "pago": 2500, "tipo": "retiro"},
    {"id": "bsas-2", "titulo": "Entrega moto - Palermo", "region": "Buenos Aires", "lat": -34.5888, "lng": -58.4300, "direccion": "Av. Santa Fe 3253, Palermo", "pago": 3200, "tipo": "entrega"},
    {"id": "bsas-3", "titulo": "Nodo activo - Recoleta", "region": "Buenos Aires", "lat": -34.5900, "lng": -58.3900, "direccion": "Av. Callao 1500", "pago": 2100, "tipo": "compra"},
    # CORDOBA -32 a -30 / -65 a -63
    {"id": "cba-1", "titulo": "Retiro efectivo - Nueva Córdoba", "region": "Córdoba", "lat": -31.4285, "lng": -64.1840, "direccion": "Chacabuco 400, Córdoba", "pago": 1900, "tipo": "retiro"},
    {"id": "cba-2", "titulo": "Entrega última milla - Cerro", "region": "Córdoba", "lat": -31.3650, "lng": -64.2300, "direccion": "Rafael Nuñez 4200, Cerro", "pago": 2700, "tipo": "entrega"},
    {"id": "cba-3", "titulo": "Compra verificada - Centro", "region": "Córdoba", "lat": -31.4167, "lng": -64.1833, "direccion": "Deán Funes 100, Centro", "pago": 1500, "tipo": "compra"},
]

def detectar_region_por_coords(lat, lng):
    try:
        lat = float(lat)
        lng = float(lng)
    except:
        return None
    # Buenos Aires CABA/AMBA
    if -35.2 <= lat <= -34.3 and -58.7 <= lng <= -58.2:
        return "Buenos Aires"
    # Córdoba
    if -32.0 <= lat <= -30.0 and -65.0 <= lng <= -63.0:
        return "Córdoba"
    # Catamarca
    if -29.0 <= lat <= -27.0 and -66.5 <= lng <= -65.0:
        return "Catamarca"
    return None

# ============== HEALTH CHECK LIVIANO - SOLUCION LOGS ==============
@app.route("/health")
def health():
    # Endpoint liviano para Render, NO sirve 1.2MB
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat(), "service": "maxshop"}), 200

@app.route("/")
def index():
    # Solo sirve index, health check ya no debería pegar acá
    return render_template("index.html")

# ============== API TAREAS DINAMICA POR UBICACION ==============
@app.route("/api/tareas")
def api_tareas():
    region_param = request.args.get("region", "").strip()
    lat = request.args.get("lat")
    lng = request.args.get("lng")

    region_detectada = None
    if lat and lng:
        region_detectada = detectar_region_por_coords(lat, lng)

    region_final = region_detectada or (region_param if region_param else None)

    if region_final:
        filtradas = [t for t in TAREAS_BASE if t["region"].lower() == region_final.lower()]
    else:
        # Si no detecta nada, devuelve todas pero prioriza BA para fallback
        filtradas = TAREAS_BASE

    # Si no hay en esa region, fallback a Buenos Aires (no Catamarca fijo)
    if not filtradas and region_final:
        filtradas = [t for t in TAREAS_BASE if t["region"] == "Buenos Aires"]

    return jsonify({
        "region_detectada": region_detectada,
        "region_solicitada": region_param,
        "region_final": region_final or "Buenos Aires",
        "lat": lat,
        "lng": lng,
        "tareas": filtradas,
        "total": len(filtradas)
    })

@app.route("/api/qr/generar", methods=["POST"])
def generar_qr():
    data = request.json or {}
    monto = data.get("monto", 0)
    qr_id = str(uuid.uuid4())[:8]
    QR_CODES[qr_id] = {"monto": monto, "creado": datetime.utcnow().isoformat()}
    return jsonify({"qr_id": qr_id, "monto": monto})

@app.route("/api/transferir", methods=["POST"])
def transferir():
    data = request.json or {}
    # Saldo a favor interno - no visible al usuario externo
    origen = data.get("origen")
    destino = data.get("destino")
    monto = float(data.get("monto", 0))
    # Lógica interna, sin exponer saldo
    return jsonify({"ok": True, "msg": "Transferencia interna registrada", "ref": str(uuid.uuid4())[:6]})

@app.route("/api/comprar-csb", methods=["POST"])
def comprar_csb():
    data = request.json or {}
    monto = float(data.get("monto", 0))
    costo_comision = round(monto * 0.07, 2) # 7%
    total = monto + costo_comision
    return jsonify({
        "ok": True,
        "monto_base": monto,
        "comision_7pct": costo_comision,
        "total": total,
        "csb_acreditado": monto
    })

@app.route("/api/comercios")
def comercios():
    return jsonify([
        {"id": 1, "nombre": "Kiosco Nodo Catamarca", "region": "Catamarca", "lat": -28.4696, "lng": -65.7792},
        {"id": 2, "nombre": "MaxShop CABA", "region": "Buenos Aires", "lat": -34.6037, "lng": -58.3816},
        {"id": 3, "nombre": "Nodo CBA Centro", "region": "Córdoba", "lat": -31.4167, "lng": -64.1833},
    ])

@app.route("/api/adm/login", methods=["POST"])
def adm_login():
    data = request.json or {}
    key = data.get("key", "").strip().lower()
    if key in ADM_KEYS:
        return jsonify({"ok": True, "token": "adm_" + str(uuid.uuid4())[:12]})
    return jsonify({"ok": False, "error": "Key invalida"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
