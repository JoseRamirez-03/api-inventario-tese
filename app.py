from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi

# Sistema de Control de Inventario - TESE
app = Flask(__name__)
app.secret_key = 'tese_secret_key'

# ==========================================
#        CONEXIÓN A MONGODB ATLAS
# ==========================================
MONGO_URI = "mongodb+srv://jose1995jusn_db_user:Joseramirez04@joseadmin.gox5yvp.mongodb.net/InventarioTESE?appName=joseadmin"

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client['InventarioTESE']
col_reportes = db['reportes']
col_salas = db['salas']

# ==========================================
#        BASE DE DATOS SIMULADA (ALUMNOS)
# ==========================================
ALUMNOS_PERMITIDOS = {
    "202220305": "Jose2003",
    "202214589": "Daniel2003",
    "202236741": "Diana2003",
    "202289012": "Brian2003",
    "202256384": "Luis2003",
    "202271928": "Angel2003"
}

# ==========================================
#          RUTAS WEB (NAVEGADOR)
# ==========================================
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/acceder', methods=['POST'])
def acceder():
    matricula = request.form.get('matricula')
    password = request.form.get('password')
    
    if matricula in ALUMNOS_PERMITIDOS and password == ALUMNOS_PERMITIDOS[matricula]:
        session['rol'] = 'alumno'
        return redirect(url_for('panel'))
        
    elif matricula == "ADM001" and password == "docente":
        session['rol'] = 'docente'
        return redirect(url_for('panel'))
    
    return redirect(url_for('login'))

@app.route('/panel')
def panel():
    rol = session.get('rol')
    if not rol: return redirect(url_for('login'))
    reportes = list(col_reportes.find())
    return render_template('panel.html', rol=rol, reportes=reportes)

@app.route('/nuevo-reporte', methods=['GET', 'POST'])
def nuevo_reporte():
    if request.method == 'POST':
        nuevo_doc = {
            "alumno": request.form.get('alumno'),
            "sala": request.form.get('sala'),
            "maquina": request.form.get('maquina'),
            "falla": request.form.get('falla'),
            "estatus": "Pendiente"
        }
        col_reportes.insert_one(nuevo_doc)
        return redirect(url_for('panel'))
    return render_template('nuevo_reporte.html')

@app.route('/detalle/<id_reporte>', methods=['GET', 'POST'])
def detalle(id_reporte):
    rol = session.get('rol')
    reporte = col_reportes.find_one({"_id": ObjectId(id_reporte)})
    if request.method == 'POST' and rol == 'docente':
        nuevo_est = request.form.get('nuevo_estatus')
        col_reportes.update_one({"_id": ObjectId(id_reporte)}, {"$set": {"estatus": nuevo_est}})
        return redirect(url_for('panel'))
    return render_template('detalle.html', rol=rol, r=reporte)

@app.route('/estado', methods=['GET', 'POST'])
def estado():
    rol = session.get('rol')
    if request.method == 'POST' and rol == 'docente':
        sala_id = request.form.get('sala_id')
        nuevo_est = int(request.form.get('estatus'))
        nom_docente = request.form.get('docente_nombre')
        horario = request.form.get('horario') # <--- NUEVO CAMPO
        
        col_salas.update_one(
            {"numero": sala_id}, 
            {"$set": {
                "estado": nuevo_est, 
                "docente": nom_docente,
                "horario": horario
            }}
        )
        return redirect(url_for('estado'))
        
    salas = list(col_salas.find().sort("numero", 1))
    return render_template('estado.html', rol=rol, salas=salas)

@app.route('/salir')
def salir():
    session.clear()
    return redirect(url_for('login'))

# ==========================================
#          RUTAS DE LA API Y PWA
# ==========================================
@app.route('/api/salas')
def api_salas():
    salas = list(col_salas.find({}, {'_id': 0}).sort("numero", 1))
    return jsonify({"status": "success", "salas": salas})

# ESTA ES LA RUTA NUEVA PARA QUE FUNCIONE LA APLICACIÓN MÓVIL (PWA)
@app.route('/sw.js')
def sw():
    return app.send_static_file('sw.js')

if __name__ == '__main__':
    app.run(debug=True)
