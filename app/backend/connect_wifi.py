from machine import Pin, ADC, PWM
import time
import network

# --- ข้อมูลสำคัญ ---
WIFI_SSID = "Beautiful SKY"
WIFI_PASS = "nainainai"

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    # reset interface ก่อน
    wlan.active(False)
    time.sleep(1)
    wlan.active(True)
    time.sleep(1)
    if wlan.isconnected():
        print("Already connected:", wlan.ifconfig()[0])
        return True
    print("Connecting to WiFi...")
    try:
        wlan.connect(WIFI_SSID, WIFI_PASS)
    except Exception as e:
        print("connect error:", e)
        return False
    timeout = 15
    start = time.time()
    while not wlan.isconnected():
        if time.time() - start > timeout:
            print("WiFi connection timeout")
            return False
        time.sleep(0.5)
    print("WiFi Connected! IP:", wlan.ifconfig()[0])
    return True

connect_wifi()