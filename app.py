from flask import Flask, render_template, request, Response, send_from_directory, redirect, redirect, session, url_for
import subprocess
import sys, os
import json
import pandas as pd
import io
from functools import wraps

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

app = Flask(__name__)
app.secret_key = 'clave_ultra_secreta_que_nadie_debe_saber'

@app.route('/')
def home():
    if 'usuario' in session:
        return redirect('/dashboard')
    return redirect('/login')

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'usuario' in session:
            return f(*args, **kwargs)
        return redirect(url_for('login'))
    return wrap

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        users = load_users()
        user = users.get(email)
        if user and user['password'] == password:
            session['usuario'] = email
            session['rol'] = user['rol']
            return redirect(url_for('mis_leads'))
        return render_template('login.html', error="Credenciales incorrectas")
    return render_template('login.html')

@app.route('/buscar')
def buscar():
    return render_template('buscar.html')

def contar_funnel():
    usuario = session.get("usuario")
    if os.path.exists('leads_estado.json'):
        with open('leads_estado.json') as f:
            estados = json.load(f)
    else:
        estados = {}

    estados_contados = {
        "contactado": 0,
        "esperando": 0,
        "gestion": 0,
        "venta": 0
    }

    for data in estados.values():
        if data.get("usuario") != usuario:
            continue
        estado = data.get("estado", "").lower()
        if "contactado" in estado:
            estados_contados["contactado"] += 1
        elif "esperando" in estado:
            estados_contados["esperando"] += 1
        elif "gestion" in estado:
            estados_contados["gestion"] += 1
        elif "venta" in estado:
            estados_contados["venta"] += 1

    return estados_contados

@app.route('/leads')
@login_required
def leads():
    import pandas as pd
    import os
    from flask import session

    path = "static/empresas_unificadas.xlsx"
    if not os.path.exists(path):
        return "<h3 style='text-align:center; margin-top:40px;'>⚠️ Todavía no hay leads cargados.<br>Hacé una búsqueda y unificá primero.<br><br><a href='/dashboard'>Volver</a></h3>"

    df = pd.read_excel(path)
    usuario = session['usuario']
    df = df[df["usuario"] == usuario] if "usuario" in df.columns else df

    leads = df.to_dict(orient="records")

    return render_template("leads.html", leads=leads)


    # 3. Si es GET (mostrar leads)
    if not os.path.exists(ruta_unificada):
        return render_template("leads.html", leads=[], estados={})

    df = pd.read_excel(ruta_unificada)

    if "usuario" not in df.columns:
        return "El Excel no tiene columna 'usuario'."

    df = df[df['usuario'] == usuario]

    # Normalizar y asegurar columnas mínimas
    df.columns = df.columns.str.strip().str.lower().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
    df = df.rename(columns={
        'nombre': 'Nombre',
        'telefono': 'Telefono',
        'rubro': 'Rubro'
    })
    df = df[['Nombre', 'Telefono', 'Rubro']]

    telefonos_usuario = df['Telefono'].astype(str).tolist()

    estados = {
        tel: info for tel, info in todos_los_estados.items()
        if info.get('usuario') == usuario and tel in telefonos_usuario
    }

    leads = df.to_dict(orient='records')
    return render_template("leads.html", leads=leads, estados=estados)

@app.route('/scrap_empresas_googlemaps')
def scrap_empresas_googlemaps():
    zona = request.args.get("zona")
    rubro = request.args.get("rubro")

    def generar_logs():
        try:
            import sys, os
            script_path = os.path.abspath(os.path.join("static", "scrap_empresas_bsas_googlemaps.py"))
            print(" Python path:", sys.executable)
            print(" Script path:", script_path)

            if not os.path.exists(script_path):
                yield f"data:  No se encuentra el script en: {script_path}\n\n"
                return

            process = subprocess.Popen(
                [sys.executable, script_path, zona, rubro, session.get("usuario")],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True
            )

            for line in iter(process.stdout.readline, ''):
                yield f"data: {line.strip()}\n\n"
            process.stdout.close()
            process.wait()

        except Exception as e:
            yield f"data:  Error ejecutando script: {str(e)}\n\n"


    return Response(generar_logs(), mimetype='text/event-stream')

@app.route('/unificar_excel')
@login_required
def unificar_excel():
    import pandas as pd
    import glob
    import os

    output_folder = os.path.abspath("output")
    all_excels = glob.glob(os.path.join(output_folder, "*.xlsx"))

    if not all_excels:
        return "⚠️ No hay archivos Excel para unificar."

    all_dfs = []
    for file in all_excels:
        try:
            df = pd.read_excel(file)
            df["Archivo Origen"] = os.path.basename(file)

            # Aseguramos columna usuario
            if "usuario" not in df.columns:
                df["usuario"] = session.get("usuario")

            all_dfs.append(df)
        except Exception as e:
            print(f"Error leyendo {file}: {e}")

    final_df = pd.concat(all_dfs, ignore_index=True)
    final_path = os.path.join("static", "empresas_unificadas.xlsx")
    final_df.to_excel(final_path, index=False)

    # 🔥 Eliminar archivos viejos
    for file in all_excels:
        try:
            os.remove(file)
        except Exception as e:
            print(f"No se pudo borrar {file}: {e}")

    return send_from_directory('static', 'empresas_unificadas.xlsx', as_attachment=True)

@app.route('/enviar_masivo', methods=['GET', 'POST'])
@login_required
def enviar_masivo():
    import pandas as pd
    import os
    import re

    ruta_excel = "static/empresas_unificadas.xlsx"

    if request.method == 'POST':
        mensaje = request.form.get("mensaje", "").strip()
        if not mensaje:
            return "Mensaje vacío", 400

        # Verificamos si el archivo existe antes de leerlo
        if not os.path.exists(ruta_excel):
            return "<h3 style='text-align:center; margin-top:50px;'>⚠️ No hay archivo unificado aún.<br>Primero generá leads y unificá el Excel.<br><br><a href='/dashboard'>Volver al Dashboard</a></h3>"

        df = pd.read_excel(ruta_excel)

        # Aseguramos columna "Teléfono" y limpieza
        if "Teléfono" not in df.columns:
            return "⚠️ El Excel no tiene columna 'Teléfono'."

        df["Teléfono"] = df["Teléfono"].astype(str).str.replace(r"\D", "", regex=True)
        telefonos = [t for t in df["Teléfono"] if t.startswith("54") and len(t) >= 10][:50]

        return render_template("enviar_masivo.html", mensaje=mensaje, telefonos=telefonos)

    # GET - formulario vacío
    return render_template("enviar_masivo.html", mensaje="", telefonos=[])

@app.route('/ver_tabla')
@login_required
def ver_tabla():
    import os
    import pandas as pd

    ruta = "static/empresas_unificadas.xlsx"
    if not os.path.exists(ruta):
        return "<h3 style='text-align:center; margin-top:40px;'>⚠️ No hay Excel unificado para mostrar.<br><br><a href='/dashboard'>Volver</a></h3>"

    df = pd.read_excel(ruta)
    data = df.to_dict(orient="records")
    return render_template("tabla.html", data=data)

@app.route('/attack')
@login_required
def attack():
    return render_template('attack.html')

@app.route('/mensajes', methods=['GET', 'POST'])
@login_required
def mensajes():
    import json
    import os

    path_json = "mensajes_generados.json"

    if request.method == 'POST':
        rubro = request.form['rubro']
        zona = request.form['zona']
        producto = request.form['producto']
        valor = request.form['valor']

        mensaje = f"Hola, vi que tenés un emprendimiento de {rubro} en {zona} y quería ofrecerte una propuesta concreta: una {producto} por solo {valor}. Te sirve para mostrar tus servicios, recibir consultas o vender más desde redes. Si te interesa, respondé este mensaje y te paso más info."

        # Guardar en JSON
        if os.path.exists(path_json):
            with open(path_json, 'r') as f:
                historial = json.load(f)
        else:
            historial = []

        historial.insert(0, mensaje)  # Insertar al principio
        historial = historial[:10]    # Limitar a 10 últimos

        with open(path_json, 'w') as f:
            json.dump(historial, f)

        return render_template("mensajes.html", mensaje_generado=mensaje, historial=historial)

    # GET → solo mostrar historial
    if os.path.exists(path_json):
        with open(path_json, 'r') as f:
            historial = json.load(f)
    else:
        historial = []

    return render_template("mensajes.html", historial=historial)

@app.route('/productos')
@login_required
def productos():
    return render_template('productos.html')

@app.route('/funnel')
@login_required
def funnel():
    import json
    import os

    path_json = "leads_estado.json"

    embudo = {
        "contactado": 0,
        "esperando": 0,
        "gestion": 0,
        "venta": 0
    }

    if os.path.exists(path_json):
        with open(path_json) as f:
            estados = json.load(f)

        usuario = session.get("usuario")
        for info in estados.values():
            if info.get("usuario") != usuario:
                continue
            estado = info.get("estado", "").lower()
            if "contactado" in estado:
                embudo["contactado"] += 1
            elif "esperando" in estado:
                embudo["esperando"] += 1
            elif "gestion" in estado:
                embudo["gestion"] += 1
            elif "venta" in estado:
                embudo["venta"] += 1

    return render_template("funnel.html", embudo=embudo)
@app.route('/dashboard')
@login_required
def dashboard():
    import pandas as pd
    import glob
    import os
    import json
    from collections import Counter

    usuario = session.get("usuario")
    output_folder = os.path.abspath("output")
    user_excels = glob.glob(os.path.join(output_folder, f"{usuario}_*.xlsx"))

    if not user_excels:
        return "<h3 style='text-align:center; margin-top:40px;'>⚠️ No hay archivos aún para este usuario.<br>Hacé una búsqueda primero.<br><br><a href='/buscar'>Ir a buscar</a></h3>"

    rubros = []
    zonas = []

    for file in user_excels:
        try:
            df = pd.read_excel(file)
            if "Rubro" in df.columns:
                rubros.extend(df["Rubro"].dropna().astype(str).tolist())
            if "Zona" in df.columns:
                zonas.extend(df["Zona"].dropna().astype(str).tolist())
        except Exception as e:
            print(f"Error leyendo {file}: {e}")

    # Leer estados guardados por usuario
    leads_estado_path = os.path.join("leads_estado.json")
    estados_contados = {
        "contactado": 0,
        "esperando": 0,
        "gestion": 0,
        "venta": 0
    }
    whatsapp_enviados = 0
    contactados_hoy = 0
    ventas = 0
    total_en_gestion = 0

    if os.path.exists(leads_estado_path):
        with open(leads_estado_path, "r") as f:
            estados = json.load(f)

        for telefono, info in estados.items():
            if info.get("usuario") != usuario:
                continue
            estado = info.get("estado", "").lower()
            mensaje = info.get("mensaje", "")

            if "contactado" in estado:
                estados_contados["contactado"] += 1
                contactados_hoy += 1
            elif "esperando" in estado:
                estados_contados["esperando"] += 1
            elif "gestion" in estado:
                estados_contados["gestion"] += 1
                total_en_gestion += 1
            elif "venta" in estado:
                estados_contados["venta"] += 1
                ventas += 1

            if mensaje.strip():
                whatsapp_enviados += 1

    data = {
        "cantidad_archivos": len(user_excels),
        "total_leads": sum(estados_contados.values()),
        "rubros": Counter(rubros).most_common(10),
        "zonas": Counter(zonas).most_common(10),
        "whatsapp_enviados": whatsapp_enviados,
        "contactados_hoy": contactados_hoy,
        "ventas": ventas,
        "total_en_gestion": total_en_gestion,
        "funnel": estados_contados
    }

    return render_template("dashboard.html", data=data)

@app.route('/enviar_masivo', methods=['GET', 'POST'])
@login_required
def enviar_masivo():
    import pandas as pd
    import os
    import re

    path = "static/empresas_unificadas.xlsx"

    if request.method == 'POST':
        mensaje = request.form.get("mensaje", "").strip()
        if not mensaje:
            return "Mensaje vacío", 400

        if not os.path.exists(path):
            return "<h3 style='text-align:center; margin-top:40px;'>⚠️ No hay archivo unificado.<br>Hacé búsquedas y unificá primero.<br><br><a href='/dashboard'>Volver</a></h3>"

        df = pd.read_excel(path)
        df["Teléfono"] = df["Teléfono"].astype(str).str.replace(r"\D", "", regex=True)
        telefonos = [t for t in df["Teléfono"] if t.startswith("54") and len(t) >= 10][:50]

        return render_template("enviar_masivo.html", mensaje=mensaje, telefonos=telefonos)

    return render_template("enviar_masivo.html", mensaje="", telefonos=[])

USERS_FILE = 'users.json'

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'usuario' in session:
            return f(*args, **kwargs)
        return redirect(url_for('login'))
    return wrap



@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        rol = request.form.get('rol', 'vendedor')
        users = load_users()
        if email in users:
            return render_template('registro.html', error="El usuario ya existe")
        users[email] = {'password': password, 'rol': rol}
        save_users(users)
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/mis-leads')
@login_required
def mis_leads():
    # A futuro: leer leads y filtrar por session['usuario']
    return render_template('mis_leads.html', usuario=session['usuario'])


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)


