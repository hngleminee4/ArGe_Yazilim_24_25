import RPi.GPIO as GPIO
from time import sleep
import dht11
import time
import csv
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import platform
import psutil
import subprocess

def cpu_sicakligini_oku():
    sistem = platform.system()

    if sistem == "Linux":
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as dosya:
                sicaklik = float(dosya.read()) / 1000.0  # Millicelsius'dan Celsius'a dönüştür
            return sicaklik
        except FileNotFoundError:
            print("CPU sıcaklık verisi bulunamadı!")
            return None
    elif sistem == "Windows":
        try:
            sıcaklıklar = psutil.sensors_temperatures()
            if "coretemp" in sıcaklıklar:
                return sıcaklıklar["coretemp"][0].current
            else:
                print("CPU sıcaklık verisi alınamadı!")
                return None
        except Exception as e:
            print(f"Hata: {e}")
            return None
    elif sistem == "Darwin":  # macOS
        try:
            sicaklik = subprocess.check_output(["osx-cpu-temp"]).decode("utf-8").strip()
            return float(sicaklik.replace("°C", ""))
        except Exception as e:
            print(f"Hata: {e}")
            return None
    else:
        print("Bilinmeyen işletim sistemi.")
        return None


def sensor_verisi_oku():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    sıcaklık = dht11.DHT11(pin=2)
    değer = sıcaklık.read()

    if değer.is_valid():
        return değer.temperature, değer.humidity
    else:
        return None, None


# Canlı veri depoları
zamanlar = []
celsius_verileri = []
nem_verileri = []
cpu_sicaklik_verileri = []

# Çizim ayarları
fig, ax = plt.subplots()
line1, = ax.plot([], [], label="Celsius Temp (°C)", color="blue")
line2, = ax.plot([], [], label="Humidity (%RH)", color="green")
line3, = ax.plot([], [], label="CPU Temp (°C)", color="red")

def baslangic():
    """Grafiğin başlangıç ayarlarını yapar."""
    ax.set_xlim(0, 60)  # X ekseni için 60 saniyelik pencere
    ax.set_ylim(0, 100)  # Y ekseni için 0-100 aralığı
    ax.set_xlabel("Zaman (Saniye)")  # X eksenini etiketle
    ax.set_ylabel("Değer")  # Y eksenini etiketle
    ax.legend()  # Etiketleri göster
    return line1, line2, line3


def guncelle(frame):
    """Grafiği her yeni veri ile günceller."""
    global zamanlar, celsius_verileri, nem_verileri, cpu_sicaklik_verileri

    celsius_sicaklik, nem = sensor_verisi_oku()
    cpu_sicaklik = cpu_sicakligini_oku()

    if celsius_sicaklik is not None and cpu_sicaklik is not None:
        # Verileri güncelle
        zamanlar.append(len(zamanlar))
        celsius_verileri.append(celsius_sicaklik)
        nem_verileri.append(nem)
        cpu_sicaklik_verileri.append(cpu_sicaklik)

        # Son 60 veriyi grafikte göster
        line1.set_data(zamanlar[-60:], celsius_verileri[-60:])
        line2.set_data(zamanlar[-60:], nem_verileri[-60:])
        line3.set_data(zamanlar[-60:], cpu_sicaklik_verileri[-60:])

        # X ve Y eksenlerini güncelle
        ax.set_xlim(max(0, len(zamanlar) - 60), len(zamanlar))
        ax.set_ylim(0, max(max(celsius_verileri[-60:], default=0),
                           max(nem_verileri[-60:], default=0),
                           max(cpu_sicaklik_verileri[-60:], default=0)) + 10)
    return line1, line2, line3


# Canlı animasyonu başlat
ani = FuncAnimation(fig, guncelle, init_func=baslangic, interval=2000, blit=False)

# Grafiği göster
plt.show()