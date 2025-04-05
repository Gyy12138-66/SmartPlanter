from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
from datetime import datetime

app = Flask(__name__)
CORS(app)

# 数据库配置
db_config = {
    'host': '127.0.0.1',         # 或你的数据库服务器 IP
    'user': 'root',      # 通常是 root
    'password': 'GYYgyy123', # 你设置的密码
    'database': 'plant_data_db',   # 你的数据库名
    'port': 3306
}

# 数据库连接
def get_db_connection():
    return mysql.connector.connect(**db_config)

# 自动检查设备是否存在，否则插入新设备
def check_or_insert_devices(fog_device_id, edge_device_id, sensor_type):
    conn = get_db_connection()
    cursor = conn.cursor()

    # 检查并插入fog_device
    cursor.execute("SELECT fog_device_id FROM fog_devices WHERE fog_device_id = %s", (fog_device_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO fog_devices (fog_device_id, fog_device_name, status) VALUES (%s, %s, %s)",
                       (fog_device_id, f"Fog_{fog_device_id}", "online"))

    # 检查并插入edge_device
    cursor.execute("SELECT edge_device_id FROM edge_devices WHERE edge_device_id = %s", (edge_device_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO edge_devices (edge_device_id, fog_device_id, sensor_type) VALUES (%s, %s, %s)",
                       (edge_device_id, fog_device_id, sensor_type))
    
    conn.commit()
    cursor.close()
    conn.close()

# 通用数据插入函数
def insert_sensor_data(table_name, fog_device_id, edge_device_id, value_column, value, measured_at):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        f"""
        INSERT INTO {table_name} (fog_device_id, edge_device_id, {value_column}, measured_at)
        VALUES (%s, %s, %s, %s)
        """,
        (fog_device_id, edge_device_id, value, measured_at)
    )
    conn.commit()
    cursor.close()
    conn.close()

# 通用数据查询函数
def get_sensor_data(table_name, value_column, limit=100):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        f"""
        SELECT fog_device_id, edge_device_id, {value_column}, measured_at 
        FROM {table_name} ORDER BY measured_at DESC LIMIT %s
        """,
        (limit,)
    )
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return results

# 定义传感器接口

# 光照强度 (/light)
@app.route('/light', methods=['POST', 'GET'])
def light_sensor():
    if request.method == 'POST':
        data = request.json
        fog_id = data["fog_device_id"]
        edge_id = data["edge_device_id"]
        measured_at = data.get("measured_at", datetime.now().isoformat())
        value = data["light_value"]

        check_or_insert_devices(fog_id, edge_id, "light")
        insert_sensor_data("light_intensity", fog_id, edge_id, "light_value", value, measured_at)
        return jsonify({"status": "success", "sensor": "light"}), 200
    
    results = get_sensor_data("light_intensity", "light_value")
    return jsonify(results)

# 空气温度 (/air_temp)
@app.route('/air_temp', methods=['POST', 'GET'])
def air_temp_sensor():
    if request.method == 'POST':
        data = request.json
        fog_id = data["fog_device_id"]
        edge_id = data["edge_device_id"]
        measured_at = data.get("measured_at", datetime.now().isoformat())
        value = data["temperature_value"]

        check_or_insert_devices(fog_id, edge_id, "air_temperature")
        insert_sensor_data("air_temperature", fog_id, edge_id, "temperature_value", value, measured_at)
        return jsonify({"status": "success", "sensor": "air_temp"}), 200
    
    results = get_sensor_data("air_temperature", "temperature_value")
    return jsonify(results)

# 空气湿度 (/air_humidity)
@app.route('/air_humidity', methods=['POST', 'GET'])
def air_humidity_sensor():
    if request.method == 'POST':
        data = request.json
        fog_id = data["fog_device_id"]
        edge_id = data["edge_device_id"]
        measured_at = data.get("measured_at", datetime.now().isoformat())
        value = data["humidity_value"]

        check_or_insert_devices(fog_id, edge_id, "air_humidity")
        insert_sensor_data("air_humidity", fog_id, edge_id, "humidity_value", value, measured_at)
        return jsonify({"status": "success", "sensor": "air_humidity"}), 200
    
    results = get_sensor_data("air_humidity", "humidity_value")
    return jsonify(results)

# 空气气压 (/air_pressure)
@app.route('/air_pressure', methods=['POST', 'GET'])
def air_pressure_sensor():
    if request.method == 'POST':
        data = request.json
        fog_id = data["fog_device_id"]
        edge_id = data["edge_device_id"]
        measured_at = data.get("measured_at", datetime.now().isoformat())
        value = data["pressure_value"]

        check_or_insert_devices(fog_id, edge_id, "air_pressure")
        insert_sensor_data("air_pressure", fog_id, edge_id, "pressure_value", value, measured_at)
        return jsonify({"status": "success", "sensor": "air_pressure"}), 200
    
    results = get_sensor_data("air_pressure", "pressure_value")
    return jsonify(results)

# 土壤湿度 (/soil)
@app.route('/soil', methods=['POST', 'GET'])
def soil_moisture_sensor():
    if request.method == 'POST':
        data = request.json
        fog_id = data["fog_device_id"]
        edge_id = data["edge_device_id"]
        measured_at = data.get("measured_at", datetime.now().isoformat())
        value = data["moisture_value"]

        check_or_insert_devices(fog_id, edge_id, "soil_moisture")
        insert_sensor_data("soil_moisture", fog_id, edge_id, "moisture_value", value, measured_at)
        return jsonify({"status": "success", "sensor": "soil_moisture"}), 200
    
    results = get_sensor_data("soil_moisture", "moisture_value")
    return jsonify(results)

# 用户数据接口
@app.route('/user', methods=['POST', 'GET'])
def user_data():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')

        cursor.execute("""
            INSERT INTO users (username, password, email)
            VALUES (%s, %s, %s)
        """, (username, password, email))
        conn.commit()

        cursor.execute("SELECT LAST_INSERT_ID() AS user_id")
        user_id = cursor.fetchone()['user_id']

        cursor.execute("SELECT created_at, updated_at FROM users WHERE user_id = %s", (user_id,))
        timestamps = cursor.fetchone()

        cursor.close()
        conn.close()
        return jsonify({
            'status': 'user added',
            'user_id': user_id,
            'created_at': timestamps['created_at'],
            'updated_at': timestamps['updated_at']
        }), 200

    cursor.execute("SELECT user_id, username, email, created_at, updated_at FROM users ORDER BY created_at DESC")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(users), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        return jsonify({'status': 'success', 'message': 'Login successful', 'user_id': user['user_id']}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)