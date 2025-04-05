import serial
import time
from datetime import datetime
import threading
import requests
from enum import Enum
from collections import deque
import random
# 引入 I2C 和 GPIO 相关库
import board
import busio
import RPi.GPIO as GPIO
from adafruit_bme280 import basic as adafruit_bme280
import adafruit_tcs34725

# =========================
# 配置参数
# =========================

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 115200
DEVICE_ID = "raspberry-01"


# =========================
# 定义传感器类型与对应 URL
# =========================

class SensorType(Enum):
    LIGHT = "light_intensity"
    AIR_TEMP = "air_temp"
    AIR_HUMIDITY = "air_humidity"
    AIR_PRESSURE = "air_pressure"
    SOIL_HUMIDITY = "soil_humidity"


SENSOR_API_URLS = {
    SensorType.LIGHT: "http://your-cloud-endpoint.com/light",
    SensorType.AIR_TEMP: "http://your-cloud-endpoint.com/air_temp",
    SensorType.AIR_HUMIDITY: "http://your-cloud-endpoint.com/air_humidity",
    SensorType.AIR_PRESSURE: "http://your-cloud-endpoint.com/air_pressure",
    SensorType.SOIL_HUMIDITY: "http://your-cloud-endpoint.com/soil"
}

# =========================
# 初始化串口
# =========================

ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

# =========================
# 初始化 I2C 传感器
# =========================

i2c = busio.I2C(board.SCL, board.SDA)

# BME280：获取环境温度、压力和湿度
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x77)  # 根据实际地址修改

# 土壤湿度（或 pH）传感器：数字输出，通过 GPIO 读取
MOISTURE_SENSOR_DO_PIN = 17  # GPIO17（物理引脚11）
GPIO.setmode(GPIO.BCM)
GPIO.setup(MOISTURE_SENSOR_DO_PIN, GPIO.IN)

moisture_window = deque(maxlen=6)
simulated_moisture = None

# =========================
# 数据发送基础函数
# =========================

def build_payload(sensor_type: SensorType, edge_device_id: str, value):
    """根据传感器类型构造 payload 数据"""
    base_payload = {
        "fog_device_id": DEVICE_ID,
        "edge_device_id": edge_device_id,
        "measured_at": datetime.now().isoformat()
    }
    if sensor_type == SensorType.LIGHT:
        base_payload["light_value"] = value
    elif sensor_type == SensorType.AIR_TEMP:
        base_payload["temperature_value"] = value
    elif sensor_type == SensorType.AIR_HUMIDITY:
        base_payload["humidity_value"] = value
    elif sensor_type == SensorType.AIR_PRESSURE:
        base_payload["pressure_value"] = value
    elif sensor_type == SensorType.SOIL_HUMIDITY:
        base_payload["moisture_value"] = value
    return base_payload


def send_sensor_value(sensor_type: SensorType, edge_device_id: str, value):
    """通过对应 URL 将传感器数据发送到云端"""
    payload = build_payload(sensor_type, edge_device_id, value)
    url = SENSOR_API_URLS[sensor_type]
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Successfully sent to cloud:", payload)
        else:
            print("❌ Failed to send to cloud, status code:", response.status_code)
    except Exception as e:
        print("❗ HTTP error:", e)


# =========================
# 各传感器专用数据发送方法
# =========================

def send_time_and_date():
    """发送当前时间和日期到 micro:bit"""
    now = datetime.now()
    time_str = now.strftime("T:%H:%M")
    date_str = now.strftime("D:%m-%d-%Y")
    ser.write((time_str + "\n").encode())
    print("Sent time:", time_str)
    time.sleep(1)
    ser.write((date_str + "\n").encode())
    print("Sent date:", date_str)


def parse_light_value(line):
    """
    从 micro:bit 返回的数据字符串中提取 edge_device_id 和 light_value
    例如： "DID:EDGE-001;L:320"
    """
    edge_device_id = None
    light_value = None
    try:
        parts = line.split(";")
        for part in parts:
            if ":" in part:
                key, value = part.split(":", 1)
                key = key.strip()
                value = value.strip()
                if key == "DID":
                    edge_device_id = value
                elif key == "L":
                    light_value = float(value)
    except Exception as e:
        print("Parse error:", e)
    return edge_device_id, light_value


def send_light_data():
    """从 micro:bit 读取光照数据并上传"""
    try:
        line = ser.readline().decode().strip()
        if line:
            print("Received from micro:bit:", line)
            edge_device_id, light_value = parse_light_value(line)
            if edge_device_id is not None and light_value is not None:
                send_sensor_value(SensorType.LIGHT, edge_device_id, light_value)
                print("Sent light value:", light_value)
            else:
                print("⚠️ Missing data fields, skipping send.")
    except Exception as e:
        print("Read error:", e)


def send_air_temp_data():
    """读取 BME280 温度数据并上传"""
    temperature = bme280.temperature
    send_sensor_value(SensorType.AIR_TEMP, "env-01", temperature)
    print(f"Sent BME280 temperature: {temperature}")


def send_air_humidity_data():
    """读取 BME280 湿度数据并上传"""
    humidity = bme280.humidity
    send_sensor_value(SensorType.AIR_HUMIDITY, "env-01", humidity)
    print(f"Sent BME280 humidity: {humidity}")


def send_air_pressure_data():
    """读取 BME280 压力数据并上传"""
    pressure = bme280.pressure
    send_sensor_value(SensorType.AIR_PRESSURE, "env-01", pressure)
    print(f"Sent BME280 pressure: {pressure}")


def update_simulated_moisture_from_window(window):
    wet_count = window.count('wet')
    if wet_count >= 5:
        return random.randint(80, 95)
    elif wet_count >= 4:
        return random.randint(65, 80)
    elif wet_count >= 3:
        return random.randint(50, 65)
    elif wet_count >= 2:
        return random.randint(35, 50)
    elif wet_count >= 1:
        return random.randint(20, 35)
    else:
        return random.randint(5, 20)


def send_soil_humidity_data():
    # Soil moisture status (DO)
        moisture_status = GPIO.input(MOISTURE_SENSOR_DO_PIN)
        if moisture_status == GPIO.HIGH:
            moisture_window.append('dry')
        else:
            moisture_window.append('wet')

        # Output realistic-looking moisture
        if len(moisture_window) == 6:
            simulated_moisture = update_simulated_moisture_from_window(moisture_window)
            send_sensor_value(SensorType.SOIL_HUMIDITY, "env-01", simulated_moisture)
            print(f"Sent Soil Humidity: {simulated_moisture}")
        else:
            print(f"Soil Moisture = Estimating... ({len(moisture_window)}/6 readings collected)")


# =========================
# 多线程执行函数
# =========================

def microbit_light_thread():
    """线程：不断从 micro:bit 获取并发送光照数据"""
    while True:
        send_light_data()
        time.sleep(1)


def environment_data_thread():
    """线程：定时读取环境传感器数据，并分别调用各自专用的发送方法"""
    while True:
        send_air_temp_data()
        send_air_humidity_data()
        send_air_pressure_data()
        send_soil_humidity_data()
        time.sleep(600)


def time_sender_thread():
    """线程：监测分钟或日期变化，变化时发送时间和日期"""
    last_minute = None
    last_date = None
    while True:
        now = datetime.now()
        current_minute = now.minute
        current_date = now.date()  # 只关注年月日
        if current_minute != last_minute or current_date != last_date:
            send_time_and_date()
            last_minute = current_minute
            last_date = current_date
        time.sleep(1)


# =========================
# 主程序入口
# =========================

if __name__ == "__main__":
    try:
        # 开启多个后台线程，各自负责不同的数据采集和上传任务
        light_thread = threading.Thread(target=microbit_light_thread, daemon=True)
        env_thread = threading.Thread(target=environment_data_thread, daemon=True)
        time_thread = threading.Thread(target=time_sender_thread, daemon=True)

        light_thread.start()
        env_thread.start()
        time_thread.start()

        # 主线程保持运行状态
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        ser.close()
        GPIO.cleanup()
