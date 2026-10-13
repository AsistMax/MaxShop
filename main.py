from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import threading, time, random, datetime, uuid
from collections import defaultdict, deque

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

# --- DB en memoria (reemplazar por Postgres en producción) ---
USERS = {}  # user_id -> {datos bancarios completos + comercio adherido}
WALLETS = {}  # user_id -> {disponible, bloqueado, csi_saldo_favor, tarjetas[]}
CSI_PENDIENTES = {}  # user_id -> deque de {monto_csi, intento, timestamp, tarjetas_intentadas}
MOVIMIENTOS = defaultdict(list)  # user_id -> [{tipo, monto, alias, fecha, hash}]
TRANSFER_LOG = []  # [{from, to, monto, fecha}] para detectar devoluciones
COMERCIOS = [
    {"id":"fc","nombre":"Farmacia Central Norte","rubro":"Farmacia","dir":"Av. Belgrano 1245, CABA","tel":"11 4567-8901","badge_off":"-20% OFF","badge_csb":"+10% C$B","verificado":True,"banner":"#8BB89C"},
    {"id":"kd","nombre":"Kiosco Don Pepe","rubro":"Kiosco","dir":"Av. Corrientes 1234, CABA","tel":"11 4234-5678","badge_off":"-15% OFF","badge_csb":"+12% C$B","verificado":True,"banner":"#C4A35A"},
    {"id":"td","nombre":"Taller Mecánico Ruta 3","rubro":"Taller mecánico","dir":"Ruta 3 Km 12, La Matanza","tel":"11 6789-0123","badge_off":"-25% OFF","badge_csb":"+15% C$B","verificado":True,"banner":"#7A8FA6"},
]
TAREAS_BOTS = deque(maxlen=200)

ADM_CODE = "AsistMax2026!"

# --- Helpers CSI y reintegro ---
def intentar_cobro_csi(user_id, monto_csb):
    """
    Compra C$B: usuario pide monto libre. Costo interno 7% = monto*0.07
    Intenta tarjetas una por una. Si falla, queda pendiente sin intereses.
    """
    costo_csi = round(monto_csb * 0.07, 2)
    wallet = WALLETS[user_id]
    # Descontar saldo a favor de reintegros previos
    saldo_favor = wallet.get("csi_saldo_favor", 0)
    a_cobrar = max(0, costo_csi - saldo_favor)
    resto_favor = max(0, saldo_favor - costo_csi)
    wallet["csi_saldo_favor"] = resto_favor

    tarjetas = wallet.get("tarjetas", [])
    exito = False
    for t in tarjetas:
        # Simula cobro 70% éxito
        if random.random() > 0.3:
            exito = True
            break
    if not exito:
        # Queda pendiente sin intereses
        CSI_PENDIENTES.setdefault(user_id, deque()).append({
            "id": str(uuid.uuid4()),
            "monto_csi": a_cobrar,
            "monto_csb": monto_csb,
            "fecha": datetime.datetime.now().isoformat(),
            "intentos": 1
        })
        return {"ok": False, "pendiente": True, "csi": a_cobrar, "msg": "Saldo insuficiente, ingresá otro monto. Reintentaremos."}
    # Éxito: acredita C$B
    wallet["disponible"] += monto_csb
    MOVIMIENTOS[user_id].append({
        "tipo": "compra_csb", "monto_csb": monto_csb, "csi_cobrado": a_cobrar,
        "saldo_favor_usado": saldo_favor - resto_favor, "fecha": datetime.datetime.now().isoformat(),
        "hash": uuid.uuid4().hex[:12]
    })
    return {"ok": True, "csi": a_cobrar, "saldo_favor_restante": resto_favor}

def detectar_reintegro(from_alias, to_alias, monto):
    """
    Si detectamos devolución: mismo monto, mismo par invertido en ventana corta,
    marcamos como reintegro. Ese CSI ya cobrado se descuenta de próximas compras.
    """
    now = datetime.datetime.now()
    # Buscar transferencia previa inversa
    for log in reversed(TRANSFER_LOG[-50:]):
        if log["from"] == to_alias and log["to"] == from_alias and log["monto"] == monto:
            # Diferencia < 48hs
            delta = (now - datetime.datetime.fromisoformat(log["fecha"])).total_seconds() / 3600
            if delta < 48:
                return True
    return False

# --- Background threads ---
def retry_csi_thread():
    while True:
        time.sleep(7*3600)  # 7 horas como acordamos
        for user_id, pendientes in list(CSI_PENDIENTES.items()):
            if not pendientes:
                continue
            p = pendientes[0]
            # Reintenta
            wallet = WALLETS.get(user_id)
            if not wallet:
                continue
            tarjetas = wallet.get("tarjetas", [])
            for t in tarjetas:
                if random.random() > 0.4:
                    # Cobro exitoso pendiente
                    pendientes.popleft()
                    wallet["disponible"] += p["monto_csb"]
                    MOVIMIENTOS[user_id].append({
                        "tipo": "compra_csb_retry_ok",
                        "monto_csb": p["monto_csb"],
                        "csi": p["monto_csi"],
                        "fecha": datetime.datetime.now().isoformat()
                    })
                    break
            else:
                p["intentos"] += 1

def bots_generador_tareas():
    oficios = ["Electricista matriculado", "Plomero gasista", "Peluquera a domicilio", "Contadora independiente", "Sacar fotos local", "Llevar paquete", "Cuidado adultos", "Diseño CVs"]
    locs = ["Buenos Aires • CABA", "Córdoba • Centro", "Mendoza", "Rosario • Santa Fe", "Salta", "Neuquén"]
    while True:
        time.sleep(12)
        tarea = {
            "id": uuid.uuid4().hex[:8],
            "title": random.choice(oficios) + " - " + random.choice(["Urgencia", "Instalación", "Reparación", "Consulta", "Entrega"]),
            "tag": random.choice(["OFICIO","NUEVO","URGENTE"]),
            "loc": random.choice(locs),
            "dist": f"{random.uniform(0.3,3.5):.1f}km",
            "price": f"${random.randint(3000,15000)}",
            "fecha": datetime.datetime.now().isoformat()
        }
        TAREAS_BOTS.appendleft(tarea)

threading.Thread(target=retry_csi_thread, daemon=True).start()
threading.Thread(target=bots_generador_tareas, daemon=True).start()

# --- Routes ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.json
    # Validación bancaria completa
    required = ["nombres","dni","telefono","direccion","localidad","correo","usuario","clave"]
    for r in required:
        if not data.get(r):
            return jsonify({"ok":False, "error": f"Falta {r}"}), 400
    user_id = data["usuario"]
    if user_id in USERS:
        return jsonify({"ok":False, "error":"Usuario existe"}), 400
    USERS[user_id] = data
    # Comercio adherido opcional
    if data.get("comercio"):
        # Validar comercio datos completos bancarios
        pass
    WALLETS[user_id] = {"disponible": 0, "bloqueado": 0, "csi_saldo_favor": 0, "tarjetas": [], "alias": f"{user_id}.nodo"}
    CSI_PENDIENTES[user_id] = deque()
    return jsonify({"ok":True, "alias": WALLETS[user_id]["alias"]})

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json
    user = USERS.get(data.get("usuario"))
    if not user or user.get("clave") != data.get("clave"):
        return jsonify({"ok":False}), 401
    # ADM check
    if data.get("adm_code") == ADM_CODE:
        return jsonify({"ok":True, "rol":"ADM", "alias": WALLETS[data["usuario"]]["alias"]})
    return jsonify({"ok":True, "rol":"usuario", "alias": WALLETS[data["usuario"]]["alias"]})

@app.route("/api/wallet/<user_id>")
def wallet(user_id):
    w = WALLETS.get(user_id)
    if not w:
        return jsonify({"ok":False}), 404
    return jsonify({"ok":True, "wallet": w, "movimientos": MOVIMIENTOS[user_id][-20:]})

@app.route("/api/wallet/comprar_csb", methods=["POST"])
def comprar_csb():
    data = request.json
    user_id = data["user_id"]
    monto = float(data["monto_csb"])  # Input libre: 5000,7000,100000 lo que quiera
    if user_id not in WALLETS:
        return jsonify({"ok":False}), 404
    res = intentar_cobro_csi(user_id, monto)
    return jsonify(res)

@app.route("/api/tarjetas/agregar", methods=["POST"])
def agregar_tarjeta():
    data = request.json
    user_id = data["user_id"]
    tarjeta = data["tarjeta"]  # ****1234, banco, etc. Truco interno CSI + promo bancaria real
    if user_id not in WALLETS:
        return jsonify({"ok":False}), 404
    # Sin límite: si tiene 11 pone 11
    WALLETS[user_id]["tarjetas"].append(tarjeta)
    # Bot busca promo bancaria real para informar más beneficios (doblete C$B + promo)
    promo = f"Beneficio detectado con {tarjeta.get('banco','tu banco')} + C$B"
    return jsonify({"ok":True, "total": len(WALLETS[user_id]["tarjetas"]), "promo": promo})

@app.route("/api/alias/transferir", methods=["POST"])
def transferir_alias():
    data = request.json
    from_id = data["from_user"]
    to_alias = data["to_alias"]
    monto = float(data["monto"])
    # Resolver alias
    to_user = None
    for uid, w in WALLETS.items():
        if w["alias"] == to_alias:
            to_user = uid
            break
    if not to_user:
        return jsonify({"ok":False, "error":"Alias no existe"}), 404
    from_wallet = WALLETS[from_id]
    if from_wallet["disponible"] < monto:
        return jsonify({"ok":False, "error":"Sin saldo C$B"}), 400
    # Detectar reintegro
    es_reintegro = detectar_reintegro(from_wallet["alias"], to_alias, monto)
    from_wallet["disponible"] -= monto
    WALLETS[to_user]["disponible"] += monto
    TRANSFER_LOG.append({"from": from_wallet["alias"], "to": to_alias, "monto": monto, "fecha": datetime.datetime.now().isoformat(), "reintegro": es_reintegro})
    if es_reintegro:
        # Ese CSI ya cobrado se convierte en saldo a favor para próximas compras
        # Buscar último CSI cobrado de from_user hacia to_user (simplificado: último movimiento compra)
        # Aquí aplicamos lógica: si detectamos devolución, sabemos que sistema ya cobró CSI, entonces lo descontamos
        # Ej: CSI $240 cobrado, devolución, próxima compra CSI $200 -> no cobra, quedan $40 favor
        # Implementado en intentar_cobro_csi via csi_saldo_favor
        # Sumamos monto CSI asociado (estimado: buscar último movimiento)
        ultimo_csi = 0
        for m in reversed(MOVIMIENTOS[from_id]):
            if m.get("csi_cobrado"):
                ultimo_csi = m["csi_cobrado"]
                break
        if ultimo_csi == 0:
            ultimo_csi = monto * 0.07  # fallback
        WALLETS[from_id]["csi_saldo_favor"] = WALLETS[from_id].get("csi_saldo_favor",0) + ultimo_csi
        MOVIMIENTOS[from_id].append({"tipo":"reintegro_detectado","monto":monto,"csi_saldo_favor_generado":ultimo_csi,"fecha":datetime.datetime.now().isoformat()})
    else:
        MOVIMIENTOS[from_id].append({"tipo":"transferencia","to":to_alias,"monto":monto,"fecha":datetime.datetime.now().isoformat()})
    return jsonify({"ok":True, "reintegro": es_reintegro, "saldo_favor": WALLETS[from_id].get("csi_saldo_favor",0)})

@app.route("/api/comercios")
def comercios():
    q = request.args.get("q","").lower()
    rubro = request.args.get("rubro","Todos")
    res = COMERCIOS
    if rubro != "Todos":
        res = [c for c in res if rubro.lower() in c["rubro"].lower()]
    if q:
        res = [c for c in res if q in c["nombre"].lower() or q in c["rubro"].lower()]
    return jsonify(res)

@app.route("/api/nodo_plus/mapa")
def mapa_tareas():
    user_id = request.args.get("user_id")
    # Filtra según oficios usuario (simulado: solo 2 oficios)
    user = USERS.get(user_id, {})
    oficios_user = user.get("oficios", ["Electricista","Llevar paquete"]) if user else ["Electricista","Llevar paquete"]
    # Devuelve tareas que coinciden
    tareas_filtradas = [t for t in list(TAREAS_BOTS) if any(o.lower() in t["title"].lower() for o in oficios_user)][:20]
    if not tareas_filtradas:
        tareas_filtradas = list(TAREAS_BOTS)[:10]
    return jsonify({"tareas": tareas_filtradas, "bots_activos": random.randint(12,35)})

@app.route("/api/nodo_plus/publicar", methods=["POST"])
def publicar_servicio():
    data = request.json
    # No decir estilo libre público, solo input libre
    titulo = data["servicio"]
    TAREAS_BOTS.appendleft({
        "id": uuid.uuid4().hex[:8],
        "title": titulo,
        "tag": "NUEVO",
        "loc": "Tu zona • Publicado",
        "dist": "0.1km",
        "price": "A convenir",
        "fecha": datetime.datetime.now().isoformat()
    })
    return jsonify({"ok":True})

@app.route("/api/qr/escanear", methods=["POST"])
def qr_escanear():
    # QR 100% real: frontend abre cámara, envía comercio_id + monto total
    data = request.json
    comercio_id = data["comercio_id"]
    monto_total = float(data["monto_total"])
    user_id = data["user_id"]
    comercio = next((c for c in COMERCIOS if c["id"]==comercio_id), None)
    if not comercio:
        return jsonify({"ok":False}), 404
    # Calcula promo día comercio (comercio pone lo que quiere)
    promo_pct = random.randint(5,30)  # Simula promo día
    descuento_csb = round(monto_total * promo_pct / 100, 2)
    # Paga con C$B transferencia interna
    wallet = WALLETS[user_id]
    if wallet["disponible"] < descuento_csb:
        return jsonify({"ok":False, "error":"Sin C$B"}), 400
    wallet["disponible"] -= descuento_csb
    wallet["bloqueado"] = wallet.get("bloqueado",0) + 0  # Lógica bloqueo si aplica
    hash_comp = uuid.uuid4().hex[:12]
    MOVIMIENTOS[user_id].append({"tipo":"pago_qr","comercio":comercio["nombre"],"monto_total":monto_total,"descuento_csb":descuento_csb,"promo":f"{promo_pct}%","hash":hash_comp,"fecha":datetime.datetime.now().isoformat()})
    return jsonify({"ok":True, "descuento_csb":descuento_csb, "promo":f"{promo_pct}%", "hash":hash_comp, "msg": f"Pagaste {descuento_csb} C$B, luego aboná diferencia en caja"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
