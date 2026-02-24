from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

# Conexión a la base de datos
def get_connection():
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "Admin1234"),
        database=os.environ.get("DB_NAME", "casino_turnos")
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

@app.route('/descanso-medico', methods=['POST'])
def registrar_dm():
    datos = request.get_json()
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Registrar la ausencia por DM
    cursor.execute("""
        INSERT INTO asistencia 
        (id_operador, id_turno, fecha, estado)
        VALUES (%s, %s, %s, 'falto')
    """, (datos['id_operador'], datos['id_turno'], datos['fecha']))
    conn.commit()

    # Contar operadores por turno en esa fecha
    cursor.execute("""
        SELECT 
            t.id_turno,
            t.nombre_turno,
            COUNT(a.id_operador) as total_operadores
        FROM asistencia a
        JOIN turnos t ON a.id_turno = t.id_turno
        WHERE a.fecha = %s 
        AND a.estado = 'asistio'
        AND a.id_turno != %s
        GROUP BY t.id_turno
    """, (datos['fecha'], datos['id_turno']))
    
    turnos_disponibles = cursor.fetchall()
    
    # Aplicar reglas de minimos
    minimos = {2: 1, 3: 2, 4: 2, 1: 2, 5: 1}
    candidatos = []
    
    for turno in turnos_disponibles:
        minimo = minimos.get(turno['id_turno'], 1)
        if turno['total_operadores'] > minimo:
            # Buscar un operador de ese turno
            cursor.execute("""
                SELECT o.id_operador, o.nombres, o.apellidos, %s as turno_origen
                FROM asistencia a
                JOIN operadores o ON a.id_operador = o.id_operador
                WHERE a.fecha = %s 
                AND a.id_turno = %s 
                AND a.estado = 'asistio'
                AND a.id_operador != %s
                LIMIT 1
            """, (turno['nombre_turno'], datos['fecha'], turno['id_turno'], datos['id_operador']))
            operador = cursor.fetchone()
            if operador:
                candidatos.append(operador)
    
    conn.close()
    
    if candidatos:
        return jsonify({
            "mensaje": "Descanso medico registrado",
            "sugerencias_cobertura": candidatos
        }), 201
    else:
        return jsonify({
            "mensaje": "Descanso medico registrado. Manejar con personal del turno afectado.",
            "sugerencias_cobertura": []
        }), 201

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)