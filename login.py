from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# 数据库配置
db_config = {
    'host': '127.0.0.1',         # 或你的数据库服务器 IP
    'user': 'root',      # 通常是 root
    'password': 'GYYgyy123', # 你设置的密码
    'database': 'plant_data_db',   # 你的数据库名
    'port': 3306
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

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
    app.run(port=8081)
