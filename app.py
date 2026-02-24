from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)

# Conexión a la base de datos
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Admin1234",  # Cambia esto por tu contraseña real
        database="casino_turnos"
    )

# Ruta principal - prueba que el servidor funciona
@app.route('/')
def inicio():
    return jsonify({"mensaje": "Sistema de Turnos Casino - API funcionando"})

# Endpoint para ver todos los operadores activos
@app.route('/operadores')
def get_operadores():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM operadores WHERE estado = 'activo'")
    operadores = cursor.fetchall()
    conn.close()
    return jsonify(operadores)

@app.route('/turnos')
def get_turnos():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM turnos")
    turnos = cursor.fetchall()
    conn.close()
    # Convertir timedelta a string legible
    for turno in turnos:
        turno['hora_inicio'] = str(turno['hora_inicio'])
        turno['hora_fin'] = str(turno['hora_fin'])
    return jsonify(turnos)
@app.route('/asistencia', methods=['GET'])
def get_asistencia():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            a.id_asistencia,
            a.fecha,
            o.nombres,
            o.apellidos,
            t.nombre_turno,
            a.estado,
            a.horas_extra
        FROM asistencia a
        JOIN operadores o ON a.id_operador = o.id_operador
        JOIN turnos t ON a.id_turno = t.id_turno
    """)
    registros = cursor.fetchall()
    conn.close()
    for r in registros:
        r['fecha'] = str(r['fecha'])
    return jsonify(registros)

from flask import Flask, jsonify, request  # Agrega 'request' al import del inicio

@app.route('/asistencia', methods=['POST'])
def registrar_asistencia():
    datos = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO asistencia 
        (id_operador, id_turno, fecha, estado, cubierto_por, horas_extra)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        datos['id_operador'],
        datos['id_turno'],
        datos['fecha'],
        datos['estado'],
        datos.get('cubierto_por', None),
        datos.get('horas_extra', 0)
    ))
    conn.commit()
    conn.close()
    return jsonify({"mensaje": "Asistencia registrada correctamente"}), 201

if __name__ == '__main__':
    app.run(debug=True)