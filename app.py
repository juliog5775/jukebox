from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_socketio import SocketIO, emit
import time
import sqlite3


app = Flask(__name__)  # Crea la aplicación Flask
app.secret_key = "12345678987654321"
socketio = SocketIO(app)

Max_usuarios = 30
usuarios_activos = []
canciones_votos = {}
canciones_votos_k={}

CONTRASENA_CORRECTA = '12345'
admin_passwd='admin123'

TIEMPO_VOTACION = 60  # 60 segundos para votar
votacion_iniciada = False
temporizador_inicio = None

from datetime import timedelta
app.permanent_session_lifetime = timedelta(days=7) #la sesion se mantiene durante 7 dias

def obtener_canciones():
    conn=sqlite3.connect('canciones.db')
    c=conn.cursor()
    c.execute('SELECT * FROM canciones')
    canciones=c.fetchall()
    conn.close()
    return canciones


def reproducir_cancion_kodi(cancion_ruta):
    url_kodi = "http://localhost:8080/jsonrpc"  #configurar kodi para que se acceda a atraves de http configuración de Kodi (asegúrate de que Kodi esté habilitado para aceptar peticiones JSON-RPC)
    
    # Crear el cuerpo de la solicitud JSON-RPC
    payload = {
        "jsonrpc": "2.0",
        "method": "Player.Open",
        "params": {
            "item": {
                "file": cancion_ruta
            }
        },
        "id": 1
    }





@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        contrasena = request.form.get('password')

        if contrasena == CONTRASENA_CORRECTA:
            usuario_numero = 1
            while usuario_numero in usuarios_activos:
                usuario_numero += 1

            if len(usuarios_activos) < Max_usuarios:
                usuario_numero = len(usuarios_activos) + 1
                usuarios_activos.append(usuario_numero)
                session['usuario_numero'] = usuario_numero
                session['autenticado'] = True
                session['canciones_votadas'] = []
                flash(f'¡Acceso permitido! tu numero de usuario es el {usuario_numero}')
                
                return redirect(url_for('home'))
            else:
                flash("Lo sentimos, ya hay 30 usuarios conectados. Por favor intentelo mas tarde")
                return redirect(url_for('login'))
        else:
            flash('Contraseña incorrecta. Intenta de nuevo.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')

        if password == admin_passwd:
            session['admin_authenticated'] = True
            flash('¡Acceso permitido para el administrador!')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Contraseña incorrecta. Intenta de nuevo.')
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

@app.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
    if 'admin_authenticated' not in session or not session['admin_authenticated']:
        flash('Acceso denegado. Por favor inicia sesión como administrador.')
        return redirect(url_for('admin_login'))
    return render_template('admin_dashboard.html', canciones_votos=canciones_votos)

@app.route('/')
def home():
    if 'autenticado' not in session or not session['autenticado']:
        return redirect(url_for('login'))
    usuario_numero = session.get('usuario_numero', None)
    canciones_kodi=obtener_canciones()
    return render_template('home.html', canciones_votos=canciones_votos, usuario_numero=usuario_numero,canciones_kodi=canciones_kodi)

@app.route('/buscar', methods=['POST'])
def buscar():
    texto_busqueda = request.form.get('buscar')
    cancion = f"Canción {texto_busqueda}"
    if cancion not in canciones_votos:
        canciones_votos[cancion] = {"me_gusta": 0}
        socketio.emit('nueva_cancion', {'cancion': cancion, 'votos': canciones_votos[cancion]},to='all')
    return redirect(url_for('home'))

@app.route('/votar/<cancion>', methods=['POST'])
def votar(cancion):
    if 'canciones_votadas' not in session:
        session['canciones_votadas']=[]

    if cancion in session['canciones_votadas']:
        flash(f"Ya has votado por la cancion. No puedes votar de nuevo")
        return redirect(url_for('home'))
    
    voto = request.form.get('voto')  # Obtiene el voto del usuario

    if 'ultima_cancion_votada' in session:
        ultima_cancion = session['ultima_cancion_votada']
        if ultima_cancion != cancion:
            if ultima_cancion in canciones_votos: # Si el usuario está votando por una canción diferente
            # Si ya tiene un "me gusta", lo eliminamos
                if canciones_votos[ultima_cancion]['me_gusta'] > 0:
                    canciones_votos[ultima_cancion]['me_gusta'] -= 1
    
    # Usamos la canción tal cual se pasa, sin decodificación
    if cancion not in canciones_votos:
        flash(f"La canción {cancion} no se encuentra en la lista.")
        return redirect(url_for('home')) 
    
    # Incrementar el voto correspondiente
    if voto == 'me_gusta':
        canciones_votos[cancion]['me_gusta'] += 1
    session['canciones_votadas'].append(cancion)
    session['ultima_cancion_votada']=cancion
    flash(f"Gracias por votar por la canción: {cancion}")
    return redirect(url_for('home'))


@app.route('/votar_k/<cancion>', methods=['POST'])
def votar_k(cancion):
    if 'canciones_votadas' not in session:
        session['canciones_votadas']=[]




    if cancion in session['canciones_votadas']:
        flash(f"Ya has votado por la cancion. No puedes votar de nuevo")
        return redirect(url_for('home'))
    
    voto = request.form.get('voto')  # Obtiene el voto del usuario

    if 'ultima_cancion_votada' in session:
        ultima_cancion = session['ultima_cancion_votada']
        if ultima_cancion != cancion:
            if ultima_cancion in canciones_votos_k: # Si el usuario está votando por una canción diferente
            # Si ya tiene un "me gusta", lo eliminamos
                if canciones_votos_k[ultima_cancion]['me_gusta'] > 0:
                    canciones_votos_k[ultima_cancion]['me_gusta'] -= 1
    
    # Usamos la canción tal cual se pasa, sin decodificación
    if cancion not in canciones_votos_k:
        flash(f"La canción {cancion} no se encuentra en la lista.")
        return redirect(url_for('home')) 
    
    # Incrementar el voto correspondiente
    if voto == 'me_gusta':
        canciones_votos_k[cancion]['me_gusta'] += 1
    session['canciones_votadas'].append(cancion)
    session['ultima_cancion_votada']=cancion
    flash(f"Gracias por votar por la canción: {cancion}")
    return redirect(url_for('home'))


















@app.route('/resetear', methods=['POST'])
def resetear():
    global canciones_votos
    canciones_votos = {}
    session['canciones_votadas'] = []
    session['puede_ver_resultados']=True
    #return jsonify({"status": "success"}), 200
   
    socketio.emit('redirigir_resultados',{})
    return redirect(url_for('admin_dashboard'))
  

@app.route('/resultado', methods=['GET'])
def resultado():
    
        if canciones_votos:
            ganadora = max(canciones_votos.items(), key=lambda item: item[1]['me_gusta'])
            cancion = ganadora[0]
            votos = ganadora[1]['me_gusta']
            return render_template('resultado.html', cancion=cancion, votos=votos)
        else:
            return render_template('resultado.html', cancion=None, votos=0)


@app.route('/mostrar_resultados', methods=['POST','GET'])
def mostrar_resultados():
    if 'admin_authenticated' not in session or not session['admin_authenticated']:
        return jsonify({"status": "error", "message": "Acceso denegado. Necesitas estar autenticado como administrador."})

    global canciones_votos
    if canciones_votos:
        ganadora = max(canciones_votos.items(), key=lambda item: item[1]['me_gusta'])
        cancion = ganadora[0]
        votos = ganadora[1]['me_gusta']

        socketio.emit('redirigir_resultados', {'cancion': cancion, 'votos': votos})
        canciones_votos = {}  # Resetea los votos
        session['canciones_votadas'] = []  # Limpiar la lista de canciones votadas
        socketio.emit('reset_votos', {})  # Emitir el evento de reset

        return jsonify({"status": "success", "cancion": cancion, "votos": votos})
    else:
        return jsonify({"status": "error", "message": "No hay canciones votadas."})

connected_clients = []

@app.route('/ver_sesion', methods=['GET'])
def ver_sesion():
    return f"Datos de la sesion {session['usuario_numero'], session['canciones_votadas']} "


@app.route('/clear_session')
def clear_session():
    session.clear()
    return" toda la sesion ha sido eliminada"
    



@socketio.on('connect')
def connect():
    sid = request.sid
    if sid not in connected_clients:
        connected_clients.append(sid)
    emit('usuarios_conectados', len(connected_clients))

@socketio.on('disconnect')
def disconnect():
    sid = request.sid
    if sid in connected_clients:
        connected_clients.remove(sid)
    emit('usuarios_conectados', len(connected_clients))

def start_vote_timer():
    global votacion_iniciada, temporizador_inicio
    votacion_iniciada = True
    temporizador_inicio = time.time()
    socketio.emit('mensaje_flash', {'mensaje': 'La votación ha comenzado!'})
    socketio.emit('redirigir_resultados', {})

@socketio.on('check_voting_time')
def check_voting_time():
    if votacion_iniciada:
        elapsed_time = time.time() - temporizador_inicio
        if elapsed_time >= TIEMPO_VOTACION:
            socketio.emit('redirigir_resultados', {})
            votacion_iniciada = False

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', debug=True)
