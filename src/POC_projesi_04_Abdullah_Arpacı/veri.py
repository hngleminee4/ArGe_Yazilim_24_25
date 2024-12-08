from pymavlink import mavutil
import matplotlib.pyplot as plt

#veri dosyası
log_file = "data.bin"
mavlog = mavutil.mavlink_connection(log_file)

#Verilerin tutulacağı listeler
roll = []
pitch = []
yaw = []
time = []
latitudes = []
longitudes = []

#Verileri okuma
while True:
    message = mavlog.recv_match(blocking=False)
    if message is None:
        break

    #Uçuş verilerinin alındığı kısım
    if message.get_type() == "GPS":
        data = message.to_dict()
        latitudes.append(data.get("Lat", 0) / 1e7)  # Enlem, 1e7 ölçeğinde
        longitudes.append(data.get("Lng", 0) / 1e7)  # Boylam, 1e7 ölçeğinde
    if message.get_type() == "ATT":
        data = message.to_dict()
        time.append(data.get("TimeUS", 0) / 1000000*60)  # Mikro saniyeden saniyeye çevir
        roll.append(data.get("Roll", 0))
        pitch.append(data.get("Pitch", 0))
        yaw.append(data.get("Yaw", 0))


#Rota verileri kullanılarak oluşturulan grafik
plt.figure(figsize=(10, 6))
plt.plot(longitudes, latitudes, marker="o", color="blue", label="Uçuş Rotası")
plt.xlabel("Boylam")
plt.ylabel("Enlem")
plt.title("Uçuş Rotası (Koordinatlar)")
plt.grid()
plt.legend()
plt.show()

# Roll, Pitch ve Yaw verilerinin zamana göre grafiği
plt.figure(figsize=(12, 8))
plt.plot(time, roll, label="Roll", color="blue")
plt.plot(time, pitch, label="Pitch", color="green")
plt.plot(time, yaw, label="Yaw", color="red")
plt.xlabel("Zaman (dakika)")
plt.ylabel("Açı (derece)")
plt.title("Roll, Pitch ve Yaw Açılarının Zamana Göre Değişimi")
plt.legend()
plt.grid()
plt.show()