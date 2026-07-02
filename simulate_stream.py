import time
import requests
import random

BASE_URL = "http://127.0.0.1:8000"
DEVICE_ID = "factory_motor_01"

def register_device_if_needed():
    """Tells the backend database registry that this hardware device exists"""
    print(f"📡 Registering device '{DEVICE_ID}' with the API gateway...")
    try:
        response = requests.post(f"{BASE_URL}/devices", json={
            "device_id": DEVICE_ID,
            "name": "Primary Conveyor Assembly Motor",
            "location": "Production Floor A",
            "device_type": "Industrial Rotary Motor"  # <-- Satisfied the final required field!
        })
        if response.status_code == 201:
            print("✅ Device successfully registered in PostgreSQL database!")
        elif response.status_code == 400:
            print("ℹ️ Device already exists in the registry. Proceeding to stream...")
        else:
            print(f"❌ Server rejected device registration with Status Code: {response.status_code}")
            print(f"📝 Server Error Details: {response.text}\n")
            print("✋ Stopping simulation because the device could not be registered.")
            exit(1)
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to FastAPI. Is your uvicorn server running?")
        exit(1)

def stream_telemetry():
    """Generates 20 data points: steady baseline values followed by an artificial heat spike"""
    print("\n🚀 Starting real-time telemetry streaming simulation...")
    normal_temp = 42.0
    humidity = 55.0
    voltage = 230.0

    for idx in range(1, 21):
        temp_variance = random.uniform(-0.5, 0.5)
        current_temp = normal_temp + temp_variance

        if idx in [11, 12, 13]:
            current_temp += random.uniform(15.0, 20.0)
            print(f"\n⚠️ [SIMULATOR ALERT] Simulating critical hardware friction! Injecting heat spike.")

        payload = {
            "device_id": DEVICE_ID,
            "temperature": round(current_temp, 2),
            "humidity": round(humidity + random.uniform(-1, 1), 2),
            "voltage": round(voltage + random.uniform(-2, 2), 2)
        }

        try:
            res = requests.post(f"{BASE_URL}/readings", json=payload)
            if res.status_code == 201:
                data = res.json()
                if data.get("is_anomaly"):
                    print(f"🔥 [ANOMALY DETECTED] Cycle {idx}: Sent Temp={payload['temperature']}°C | Z-Score={round(data['z_score'], 2)}")
                else:
                    print(f"🟢 [NORMAL] Cycle {idx}: Sent Temp={payload['temperature']}°C")
            else:
                print(f"❌ Server rejected reading cycle {idx} with Status Code: {res.status_code}")
                print(f"📝 Server Response: {res.text}")
                
        except Exception as e:
            print(f"❌ Failed to transmit payload: {e}")

        time.sleep(1)

if __name__ == "__main__":
    register_device_if_needed()
    stream_telemetry()