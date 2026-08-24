from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
from typing import Optional

app = FastAPI(title="MaxShop - AsistMax Red B2B & Consumidores")

# ==========================================
# BASE DE DATOS SQLITE
# ==========================================
def init_db():
    conn = sqlite3.connect('maxshop.db')
    cursor = conn.cursor()
    
    # Tabla de Comercios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comercios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            cuit TEXT NOT NULL,
            rubro TEXT NOT NULL,
            whatsapp TEXT NOT NULL,
            direccion TEXT NOT NULL
        )
    ''')
    
    # Tabla de Usuarios (Consumidores)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL,
            telefono TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# ==========================================
# MODELOS PYDANTIC (CORREGIDOS Y ESTÁNDAR)
# ==========================================
class ComercioModel(BaseModel):
    nombre: str
    cuit: str
    rubro: str
    whatsapp: str
    direccion: str

class UsuarioModel(BaseModel):
    nombre: str
    email: str
    telefono: str

# ==========================================
# ENDPOINTS API BACKEND
# ==========================================
@app.post("/api/registrar-comercio")
def registrar_comercio(comercio: ComercioModel):
    try:
        conn = sqlite3.connect('maxshop.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO comercios (nombre, cuit, rubro, whatsapp, direccion)
            VALUES (?, ?, ?, ?, ?)
        ''', (comercio.nombre, comercio.cuit, comercio.rubro, comercio.whatsapp, comercio.direccion))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Comercio registrado con éxito"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/comercios")
def obtener_comercios():
    conn = sqlite3.connect('maxshop.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, rubro, whatsapp, direccion FROM comercios")
    rows = cursor.fetchall()
    conn.close()
    
    comercios = []
    for r in rows:
        comercios.append({
            "id": r[0],
            "nombre": r[1],
            "rubro": r[2],
            "whatsapp": r[3],
            "direccion": r[4]
        })
    return comercios

@app.post("/api/registrar-usuario")
def registrar_usuario(usuario: UsuarioModel):
    try:
        conn = sqlite3.connect('maxshop.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO usuarios (nombre, email, telefono)
            VALUES (?, ?, ?)
        ''', (usuario.nombre, usuario.email, usuario.telefono))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Usuario registrado con éxito"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# INTERFAZ FRONTEND (HTML / TailwindCSS / JS)
# ==========================================
@app.get("/", response_class=HTMLResponse)
def index():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MaxShop | AsistMax</title>
    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
    </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen flex flex-col justify-between selection:bg-cyan-500 selection:text-slate-950">

    <!-- CONTENEDOR PRINCIPAL APP MÓVIL / WEB -->
    <div class="w-full max-w-md mx-auto bg-slate-950 min-h-screen flex flex-col shadow-2xl relative border-x border-slate-900">

        <!-- Navbar Superior (LOGO MEJORADO) -->
        <header class="w-full px-5 py-4 border-b border-slate-800/80 flex justify-between items-center bg-slate-900/90 backdrop-blur-md sticky top-0 z-50 shadow-lg">
            <div class="flex items-center space-x-3.5">
                <!-- LOGO MÁS GRANDE Y NITIDO (w-14 h-14) -->
                <img src="https://i.ibb.co/rRGzqgnx/logo.jpg" alt="MaxShop Logo" class="w-14 h-14 rounded-2xl object-cover object-center border-2 border-cyan-500/60 shadow-lg shadow-cyan-500/30 bg-slate-900">
                <div>
                    <h1 class="text-lg font-black tracking-wider text-white">MAXSHOP <span class="text-cyan-400 font-light">| AsistMax</span></h1>
                    <p class="text-[11px] text-cyan-400 font-semibold tracking-widest uppercase">Red B2B & Consumidores</p>
                </div>
            </div>
            <div class="flex items-center space-x-2">
                <button onclick="abrirLogin()" class="text-xs bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 px-3 py-2 rounded-xl border border-cyan-500/30 transition font-semibold">
                    🔑 Login
                </button>
                <button onclick="abrirAdmin()" class="text-xs bg-slate-800 hover:bg-slate-700 text-slate-300 px-3 py-2 rounded-xl border border-slate-700 transition font-medium">
                    ⚙️ Admin
                </button>
            </div>
        </header>

        <!-- Contenido Principal -->
        <main class="w-full max-w-md mx-auto px-4 py-6 space-y-6 flex-1">

            <!-- BANNER PRINCIPAL (MÁS ALTO h-64 Y CENTRADO) -->
            <div class="w-full rounded-3xl overflow-hidden border border-slate-800 shadow-2xl relative bg-slate-900">
                <img src="https://i.ibb.co/wFDXX9TK/banner.jpg" alt="MaxShop Banner" class="w-full h-64 object-cover object-center">
                <div class="absolute inset-0 bg-gradient-to-t from-slate-950 via-slate-950/40 to-transparent flex items-end p-5">
                    <div>
                        <span class="text-[10px] uppercase tracking-wider text-cyan-400 font-bold bg-cyan-950/90 px-3 py-1 rounded-full border border-cyan-800/50">Comercio Destacado Oficial</span>
                        <h2 class="text-2xl font-extrabold text-white mt-1.5">MaxShop Red Global</h2>
                    </div>
                </div>
            </div>

            <!-- Accesos / Acciones Principales -->
            <div class="grid grid-cols-2 gap-3">
                <button onclick="abrirModalUsuario()" class="p-4 rounded-2xl bg-gradient-to-br from-cyan-600 to-blue-700 hover:from-cyan-500 hover:to-blue-600 text-white font-bold shadow-lg shadow-cyan-900/40 border border-cyan-400/30 text-left transition transform active:scale-95 flex flex-col justify-between h-28">
                    <span class="text-xl">🛍️</span>
                    <div>
                        <div class="text-sm font-extrabold">Soy Consumidor</div>
                        <div class="text-[10px] text-cyan-100 font-normal">Obtén beneficios y descuentos</div>
                    </div>
                </button>
                
                <button onclick="abrirModalComercio()" class="p-4 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-900 hover:from-slate-800 hover:to-slate-800 text-white font-bold shadow-lg border border-slate-700/80 text-left transition transform active:scale-95 flex flex-col justify-between h-28">
                    <span class="text-xl">🏢</span>
                    <div>
                        <div class="text-sm font-extrabold">Soy Comercio</div>
                        <div class="text-[10px] text-slate-400 font-normal">Únete a nuestra red B2B</div>
                    </div>
                </button>
            </div>

            <!-- SECCIÓN MI HISTORIAL (ACTUALIZADA Y DINÁMICA) -->
            <div class="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 space-y-3">
                <div class="flex justify-between items-center">
                    <!-- Título Dinámico según Sesión -->
                    <h3 id="tituloHistorial" class="text-xs font-bold uppercase tracking-wider text-slate-400">🧾 Historial (Inicie Sesión)</h3>
                </div>

                <!-- Mensaje de No Logueado por defecto -->
                <div id="historialVacio" class="text-center py-4 text-[11px] text-slate-500">
                    Inicie sesión o regístrese para ver sus operaciones.
                </div>

                <!-- Historial Consumos (Visible solo si es Usuario Consumidor) -->
                <div id="historialConsumosContainer" class="space-y-2 hidden">
                    <div class="text-xs bg-slate-950 p-3 rounded-xl border border-slate-800/80 space-y-1">
                        <div class="flex justify-between text-slate-400 text-[10px]">
                            <span>Fecha: 24/08/2026 - 08:30hs</span>
                            <span>Op #1042</span>
                        </div>
                        <p class="font-bold text-white">Consumo en MaxShop (5% desc. aplicado)</p>
                        <div class="flex justify-between items-center pt-1 border-t border-slate-900">
                            <span class="text-slate-400">Total pagado: <strong class="text-emerald-400">$9.500</strong></span>
                            <button onclick="verComprobanteDetalle('1042', 'MaxShop', 'Consumo con Descuento', '$9.500')" class="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-1 rounded border border-cyan-500/30 hover:bg-cyan-500/20">Ver Comprobante</button>
                        </div>
                    </div>
                </div>

                <!-- Historial Ventas (Visible solo si es Comercio) -->
                <div id="historialVentasContainer" class="space-y-2 hidden">
                    <div class="text-xs bg-slate-950 p-3 rounded-xl border border-slate-800/80 space-y-1">
                        <div class="flex justify-between text-slate-400 text-[10px]">
                            <span>Fecha: 23/08/2026 - 19:15hs</span>
                            <span>Op #1039</span>
                        </div>
                        <p class="font-bold text-white">Venta realizada a Cliente: Juan Pérez</p>
                        <div class="flex justify-between items-center pt-1 border-t border-slate-900">
                            <span class="text-slate-400">Acreditado: <strong class="text-emerald-400">$12.200</strong></span>
                            <button onclick="verComprobanteDetalle('1039', 'MaxShop', 'Venta a Consumidor', '$12.200')" class="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-1 rounded border border-cyan-500/30 hover:bg-cyan-500/20">Ver Comprobante</button>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Listado de Comercios Red -->
            <div class="space-y-3">
                <div class="flex justify-between items-center">
                    <h3 class="text-xs font-bold uppercase tracking-wider text-slate-400">📍 Comercios Adheridos</h3>
                    <span id="contadorComercios" class="text-[10px] bg-slate-800 text-cyan-400 px-2 py-0.5 rounded-full font-semibold">0 Activos</span>
                </div>
                <div id="listaComercios" class="space-y-2.5">
                    <!-- Dinámico vía JS -->
                </div>
            </div>

        </main>

        <!-- Footer -->
        <footer class="w-full py-4 text-center border-t border-slate-900 text-slate-500 text-[10px]">
            MaxShop Ecosystem &bull; Powered by AsistMax &copy; 2026
        </footer>
    </div>

    <!-- MODAL REGISTRO COMERCIO -->
    <div id="modalComercio" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-6 space-y-4 shadow-2xl">
            <div class="flex justify-between items-center">
                <h3 class="font-bold text-base text-white">🏢 Registro de Comercio</h3>
                <button onclick="cerrarModalComercio()" class="text-slate-400 hover:text-white text-lg">&times;</button>
            </div>
            <form id="formComercio" onsubmit="enviarComercio(event)" class="space-y-3">
                <div>
                    <label class="text-[11px] text-slate-400 font-medium">Nombre del Comercio</label>
                    <input type="text" id="comNombre" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500">
                </div>
                <div>
                    <label class="text-[11px] text-slate-400 font-medium">CUIT</label>
                    <input type="text" id="comCuit" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500">
                </div>
                <div>
                    <label class="text-[11px] text-slate-400 font-medium">Rubro</label>
                    <input type="text" id="comRubro" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500">
                </div>
                <div>
                    <label class="text-[11px] text-slate-400 font-medium">WhatsApp de Contacto</label>
                    <input type="text" id="comWp" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500">
                </div>
                <div>
                    <label class="text-[11px] text-slate-400 font-medium">Dirección</label>
                    <input type="text" id="comDir" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500">
                </div>
                <button type="submit" class="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-extrabold py-2.5 rounded-xl text-sm shadow-lg shadow-cyan-500/20 transition mt-2">
                    Registrar Comercio
                </button>
            </form>
        </div>
    </div>

    <!-- MODAL REGISTRO USUARIO -->
    <div id="modalUsuario" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-6 space-y-4 shadow-2xl">
            <div class="flex justify-between items-center">
                <h3 class="font-bold text-base text-white">🛍️ Registro de Consumidor</h3>
                <button onclick="cerrarModalUsuario()" class="text-slate-400 hover:text-white text-lg">&times;</button>
            </div>
            <form id="formUsuario" onsubmit="enviarUsuario(event)" class="space-y-3">
                <div>
                    <label class="text-[11px] text-slate-400 font-medium">Nombre y Apellido</label>
                    <input type="text" id="usuNombre" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500">
                </div>
                <div>
                    <label class="text-[11px] text-slate-400 font-medium">Correo Electrónico</label>
                    <input type="email" id="usuEmail" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500">
                </div>
                <div>
                    <label class="text-[11px] text-slate-400 font-medium">Teléfono / Celular</label>
                    <input type="text" id="usuTel" required class="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500">
                </div>
                <button type="submit" class="w-full bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-extrabold py-2.5 rounded-xl text-sm shadow-lg shadow-cyan-500/20 transition mt-2">
                    Continuar y Obtener Beneficio
                </button>
            </form>
        </div>
    </div>

    <!-- MODAL OPCIONES DE PAGO / BENEFICIO -->
    <div id="modalOpcionesPago" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-6 space-y-4 shadow-2xl text-center">
            <div class="w-12 h-12 bg-emerald-500/10 border border-emerald-500/30 rounded-2xl flex items-center justify-center mx-auto text-emerald-400 text-xl font-bold">
                ✓
            </div>
            <div>
                <h3 class="font-bold text-base text-white">¡Registro Exitoso!</h3>
                <p class="text-xs text-slate-400 mt-1">Selecciona tu método de pago preferido para aplicar tu descuento en MaxShop:</p>
            </div>
            <div class="space-y-2 pt-2">
                <button onclick="seleccionarMetodoPago('QR MaxShop')" class="w-full bg-slate-950 hover:bg-slate-800 border border-slate-800 p-3 rounded-xl text-xs font-bold text-left flex justify-between items-center transition">
                    <span>📱 Pagar con QR MaxShop</span>
                    <span class="text-cyan-400">10% OFF</span>
                </button>
                <button onclick="seleccionarMetodoPago('Tarjeta Débito/Crédito')" class="w-full bg-slate-950 hover:bg-slate-800 border border-slate-800 p-3 rounded-xl text-xs font-bold text-left flex justify-between items-center transition">
                    <span>💳 Tarjeta de Débito / Crédito</span>
                    <span class="text-emerald-400">5% OFF</span>
                </button>
                <button onclick="seleccionarMetodoPago('Efectivo / Transferencia')" class="w-full bg-slate-950 hover:bg-slate-800 border border-slate-800 p-3 rounded-xl text-xs font-bold text-left flex justify-between items-center transition">
                    <span>💵 Efectivo o Transferencia</span>
                    <span class="text-slate-400">Sin desc.</span>
                </button>
            </div>
            <button onclick="cerrarModalPago()" class="text-xs text-slate-500 hover:text-slate-300 pt-2">Cerrar</button>
        </div>
    </div>

    <!-- MODAL COMPROBANTE -->
    <div id="modalComprobante" class="fixed inset-0 bg-slate-950/80 backdrop-blur-sm z-50 hidden flex items-center justify-center p-4">
        <div class="bg-slate-900 border border-slate-800 w-full max-w-sm rounded-3xl p-6 space-y-4 shadow-2xl">
            <div class="flex justify-between items-center border-b border-slate-800 pb-3">
                <h3 class="font-bold text-sm text-white">🧾 Comprobante Digital</h3>
                <button onclick="cerrarComprobante()" class="text-slate-400 hover:text-white text-lg">&times;</button>
            </div>
            <div id="contenidoComprobante" class="text-xs space-y-2 text-slate-300">
                <!-- Se llena por JavaScript -->
            </div>
            <button onclick="cerrarComprobante()" class="w-full bg-slate-800 hover:bg-slate-700 text-white font-bold py-2.5 rounded-xl text-xs transition">
                Cerrar Comprobante
            </button>
        </div>
    </div>

    <!-- JAVASCRIPT LOGIC -->
    <script>
        // Variable global para simular la sesión activa
        let rolActual = null; // 'consumidor', 'comercio' o null

        function actualizarVistaHistorial() {
            const titulo = document.getElementById('tituloHistorial');
            const contConsumos = document.getElementById('historialConsumosContainer');
            const contVentas = document.getElementById('historialVentasContainer');
            const contVacio = document.getElementById('historialVacio');

            if (rolActual === 'comercio') {
                titulo.innerText = "🧾 Mi Historial de Ventas";
                contConsumos.classList.add('hidden');
                contVentas.classList.remove('hidden');
                contVacio.classList.add('hidden');
            } else if (rolActual === 'consumidor') {
                titulo.innerText = "🧾 Mi Historial de Consumos";
                contConsumos.classList.remove('hidden');
                contVentas.classList.add('hidden');
                contVacio.classList.add('hidden');
            } else {
                titulo.innerText = "🧾 Historial (Inicie Sesión)";
                contConsumos.classList.add('hidden');
                contVentas.classList.add('hidden');
                contVacio.classList.remove('hidden');
            }
        }

        function abrirLogin() {
            let id = prompt("Ingrese 'comercio' para entrar como tienda, o 'usuario' para entrar como consumidor:");
            if(id) {
                if (id.toLowerCase().includes('comercio')) {
                    rolActual = 'comercio';
                    alert("Sesión iniciada como COMERCIO.");
                } else {
                    rolActual = 'consumidor';
                    alert("Sesión iniciada como USUARIO CONSUMIDOR.");
                }
                actualizarVistaHistorial();
            }
        }

        function abrirAdmin() {
            alert("Panel Administrativo de MaxShop v1.0 (Restringido)");
        }

        function abrirModalComercio() {
            document.getElementById('modalComercio').classList.remove('hidden');
        }
        function cerrarModalComercio() {
            document.getElementById('modalComercio').classList.add('hidden');
        }

        function abrirModalUsuario() {
            document.getElementById('modalUsuario').classList.remove('hidden');
        }
        function cerrarModalUsuario() {
            document.getElementById('modalUsuario').classList.add('hidden');
        }

        function cerrarModalPago() {
            document.getElementById('modalOpcionesPago').classList.add('hidden');
        }

        function seleccionarMetodoPago(metodo) {
            alert("Método seleccionado: " + metodo + ". ¡Disfruta tu beneficio MaxShop!");
            cerrarModalPago();
        }

        function verComprobanteDetalle(op, comercio, tipo, monto) {
            let html = `
                <div class="flex justify-between py-1 border-b border-slate-800">
                    <span class="text-slate-400">Operación:</span>
                    <strong class="text-white">#${op}</strong>
                </div>
                <div class="flex justify-between py-1 border-b border-slate-800">
                    <span class="text-slate-400">Establecimiento:</span>
                    <strong class="text-white">${comercio}</strong>
                </div>
                <div class="flex justify-between py-1 border-b border-slate-800">
                    <span class="text-slate-400">Concepto:</span>
                    <strong class="text-white">${tipo}</strong>
                </div>
                <div class="flex justify-between py-1 font-bold text-sm pt-2">
                    <span class="text-slate-300">Monto Total:</span>
                    <span class="text-emerald-400">${monto}</span>
                </div>
            `;
            document.getElementById('contenidoComprobante').innerHTML = html;
            document.getElementById('modalComprobante').classList.remove('hidden');
        }

        function cerrarComprobante() {
            document.getElementById('modalComprobante').classList.add('hidden');
        }

        // Enviar Registro Comercio vía API
        async function enviarComercio(e) {
            e.preventDefault();
            const data = {
                nombre: document.getElementById('comNombre').value,
                cuit: document.getElementById('comCuit').value,
                rubro: document.getElementById('comRubro').value,
                whatsapp: document.getElementById('comWp').value,
                direccion: document.getElementById('comDir').value
            };

            try {
                let res = await fetch('/api/registrar-comercio', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                let json = await res.json();
                if(json.success) {
                    alert("¡Comercio MaxShop registrado con éxito!");
                    cerrarModalComercio();
                    document.getElementById('formComercio').reset();
                    cargarComerciosPublicos();
                    
                    // Auto-iniciar sesión como comercio registrado
                    rolActual = 'comercio';
                    actualizarVistaHistorial();
                } else {
                    alert("Error al registrar: " + json.detail);
                }
            } catch (err) {
                alert("Error de conexión con el servidor.");
            }
        }

        // Enviar Registro Usuario vía API
        async function enviarUsuario(e) {
            e.preventDefault();
            const data = {
                nombre: document.getElementById('usuNombre').value,
                email: document.getElementById('usuEmail').value,
                telefono: document.getElementById('usuTel').value
            };

            try {
                let res = await fetch('/api/registrar-usuario', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                let json = await res.json();
                if(json.success) {
                    cerrarModalUsuario();
                    document.getElementById('modalOpcionesPago').classList.remove('hidden');
                    document.getElementById('formUsuario').reset();
                    
                    // Auto-iniciar sesión como consumidor registrado
                    rolActual = 'consumidor';
                    actualizarVistaHistorial();
                } else {
                    alert("Error al registrar: " + json.detail);
                }
            } catch (err) {
                alert("Error de conexión con el servidor.");
            }
        }

        // Cargar listado de comercios desde la base de datos
        async function cargarComerciosPublicos() {
            try {
                let res = await fetch('/api/comercios');
                let comercios = await res.json();
                let container = document.getElementById('listaComercios');
                let contador = document.getElementById('contadorComercios');
                
                contador.innerText = comercios.length + " Activos";
                
                if(comercios.length === 0) {
                    container.innerHTML = `<div class="text-center py-4 text-xs text-slate-500 bg-slate-950 rounded-xl border border-slate-900">No hay comercios registrados aún.</div>`;
                    return;
                }

                container.innerHTML = "";
                comercios.forEach(c => {
                    container.innerHTML += `
                        <div class="bg-slate-900/40 border border-slate-800/80 p-3.5 rounded-2xl flex justify-between items-center transition hover:border-cyan-500/40">
                            <div>
                                <h4 class="font-bold text-xs text-white">${c.nombre}</h4>
                                <p class="text-[11px] text-cyan-400 font-medium">${c.rubro} &bull; <span class="text-slate-400">${c.direccion}</span></p>
                            </div>
                            <a href="https://wa.me/${c.whatsapp}" target="_blank" class="bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 p-2 rounded-xl text-xs font-bold transition">
                                💬 Wp
                            </a>
                        </div>
                    `;
                });
            } catch (err) {
                console.error("Error cargando comercios:", err);
            }
        }

        // Cargar al iniciar la página
        window.onload = () => {
            cargarComerciosPublicos();
            actualizarVistaHistorial();
        };
    </script>
</body>
</html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
