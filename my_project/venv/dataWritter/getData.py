from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from datetime import datetime

app = Flask(__name__)
CORS(app)

def get_db_connection():
    conn = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",             # 修改为你的 MySQL 用户名
        password="GYYgyy123",# 修改为你的 MySQL 密码
        database="plant_data_db"
    )
    return conn

# add new user
@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')  # 建议加密后存储
    email = data.get('email')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, password, email)
        VALUES (%s, %s, %s)
    """, (username, password, email))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'success'}), 201


# register fog sensor
@app.route('/api/fog', methods=['POST'])
def create_fog_device():
    data = request.json
    device_name = data.get('device_name')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO fog_devices (device_name)
        VALUES (%s)
    """, (device_name,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({'status': 'fog device added'}), 201


# register edge device
# 添加 edge_device
@app.route('/api/edge', methods=['POST'])
def create_edge_device():
    data = request.json
    fog_device_id = data.get('fog_device_id')
    sensor_type = data.get('sensor_type')

    conn = get_db_connection()
    cursor = conn.cursor()

    # 检查 fog_device_id 是否存在
    cursor.execute("SELECT fog_device_id FROM fog_devices WHERE fog_device_id = %s", (fog_device_id,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        return jsonify({'error': 'fog_device_id does not exist'}), 400

    cursor.execute("""
        INSERT INTO edge_devices (fog_device_id, sensor_type)
        VALUES (%s, %s)
    """, (fog_device_id, sensor_type))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({'status': 'edge device added'}), 201

# Get edge_devices
@app.route('/api/edge', methods=['GET'])
def get_edge_devices():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM edge_devices")
    edge_devices = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(edge_devices)


# Query all devices
@app.route('/api/devices', methods=['GET'])
def get_all_devices():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT f.fog_device_id, f.device_name, f.status,
               e.edge_device_id, e.sensor_type
        FROM fog_devices f
        LEFT JOIN edge_devices e ON f.fog_device_id = e.fog_device_id
    """)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(results)


# Main method
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)