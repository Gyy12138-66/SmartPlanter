import mysql.connector
from mysql.connector import Error

# 替换成你自己的数据库配置
db_config = {
    'host': '127.0.0.1',         # 或你的数据库服务器 IP
    'user': 'root',      # 通常是 root
    'password': 'GYYgyy123', # 你设置的密码
    'database': 'plant_data_db',   # 你的数据库名
    'port': 3306
}

try:
    conn = mysql.connector.connect(**db_config)
    if conn.is_connected():
        print("✅ 数据库连接成功！")
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = cursor.fetchall()
        print("📋 当前数据库中有这些表：")
        for table in tables:
            print("-", table[0])
        cursor.close()
        conn.close()
    else:
        print("❌ 数据库连接失败")
except Error as e:
    print("❌ 出错啦：", e)