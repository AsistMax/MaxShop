from flask import Flask, request, jsonify
from flask_cors import CORS
import qrcode, io, base64, os, json, time, random

app = Flask(__name__)
CORS(app)

ADM_KEYS = ["AsistMax2026", "AsistMax2026!"]

TAREAS_BASE = [
    {"id":"1","title":"Electricista matriculado","tag":"OFICIO","loc":"Catamarca • Centro","lat":-28.4696,"lng":-65.7859,"price":"$4.500","region":"Catamarca"},
    {"id":"2","title":"Sacar foto local - Verificar comercio","tag":"FOTO","loc":"Catamarca • Capital","lat":-28.4689,"lng":-65.7789,"price":"$1.500","region":"Catamarca"},
    {"id":"3","title":"Llevar paquete cliente a otra parte - Envío","tag":"ENVIO","loc":"Catamarca • La Chacarita","lat":-28.475,"lng":-65.795,"price":"$2.000","region":"Catamarca"},
]

@app.route("/api/qr/generar", methods=["POST"])
def qr_generar():
    alias = (request.json or {}).get("alias","lucia.nodo")
    texto = f"nodo://qr/{alias}?t={int(time.time())}"
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(texto); qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    buf = io.BytesIO(); img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return jsonify({"alias":alias,"qr_base64":b64})

@app.route("/api/tareas", methods=["GET"])
def tareas():
    region = request.args.get("region","Catamarca")
    return jsonify({"region":region,"tareas":TAREAS_BASE,"mapa_real":True})

@app.route("/api/transferir", methods=["POST"])
def transferir():
    data = request.json or {}; alias = data.get("alias",""); monto = float(data.get("monto",0))
    # Lógica interna saldo favor NO visible UI
    saldo_favor = 40 if monto >= 240 else 0
    return jsonify({"ok":True,"alias":alias,"monto":monto,"a_pagar_caja":monto-saldo_favor})

@app.route("/api/adm/login", methods=["POST"])
def adm_login():
    clave = (request.json or {}).get("clave","").strip()
    if clave in ADM_KEYS or clave.lower() in [k.lower() for k in ADM_KEYS]:
        return jsonify({"ok":True,"token":"ADM_TOKEN"})
    return jsonify({"ok":False}),401

@app.route("/api/comercios", methods=["GET","POST"])
def comercios():
    if request.method=="GET":
        return jsonify({"comercios":json.load(open("comercios.json")) if os.path.exists("comercios.json") else []})
    data = request.json or {}
    comercio = {"id":str(int(time.time()*1000)),"nombre":data.get("nombre"),"logo":data.get("logo",""),"banner":data.get("banner",""),"off":data.get("off"),"csb":data.get("csb")}
    lista = json.load(open("comercios.json")) if os.path.exists("comercios.json") else []
    lista.insert(0, comercio); json.dump(lista, open("comercios.json","w"), ensure_ascii=False, indent=2)
    return jsonify({"ok":True,"comercio":comercio})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
