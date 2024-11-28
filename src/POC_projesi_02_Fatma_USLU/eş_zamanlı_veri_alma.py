import time
import numpy as np
import matplotlib.pyplot as plt # Pixhawk'a bağlantı kurmak için
from pymavlink import mavutil  # MAVLink, çeşitli drone'lar, uydular ve robotik sistemlerde iletişim için yaygın olarak kullanılan bir mesajlaşma protokolüdür

# Pixhawk bağlantısı (seri port veya UDP üzerinden)
connection = mavutil.mavlink_connection('/dev/ttyUSB0', baud=57600)  
# baud: Veri iletim hızını belirler

# Veriyi almak için süreyi belirleyin
start_time = time.time()

# Bu kod ile bir figür ve o figür içinde 2 farklı grafik alanı (ekseni) oluşturulmuş olur
plt.ion()  # İnteraktif modda çizim yapar (grafikler anlık olarak güncellenir)
fig, ax = plt.subplots(4, 1, figsize=(10, 12))
# plt.subplots() komutu, bir figür (grafik penceresi) ve bu figür üzerinde çizim yapılacak eksenleri (axes) oluşturur.
# 2, 1: Bu parametre, 2 satır ve 1 sütundan oluşan bir 2D eksen düzeni yaratır. 
# Yani, figürde 2 tane grafik olacak ve her biri farklı bir satırda yer alacak.
# figsize=(10, 6): Bu parametre, figürün (grafik alanının) boyutlarını belirler.
# fig: Bu, tüm grafik penceresini temsil eder. Bir anlamda, tüm çizimleri içinde barındıran konteynırdır.
# ax1 ve ax2: Bunlar, fig içinde oluşturulmuş iki farklı eksendir (grafik alanlarıdır).
# ax1: Birinci grafiği (örneğin GPS verilerini) çizer.
# ax2: İkinci grafiği (örneğin ATTITUDE verilerini) çizer.

# Veri listeleri
time_list = []
roll_list = [] # Roll (uçağın veya cihazın sağa/sola eğimi)
pitch_list = [] # Pitch (çağın burun yukarı/aşağı hareketi)
yaw_list = [] # Yaw (uçağın yön değiştirmes)
lat_list = [] # Enlem
lon_list = [] # Boylam
alt_list = [] # İrtifa

while True:
    # Pixhawk'tan ATTITUDE mesajını alın
    msg = connection.recv_match(type='ATTITUDE', blocking=False)
    if msg:
        roll = np.degrees(msg.roll)
        pitch = np.degrees(msg.pitch)
        yaw = np.degrees(msg.yaw)
    
    # Pixhawk'tan GPS verisi alın
    msg_gps = connection.recv_match(type='GPS_RAW_INT', blocking=False)
    if msg_gps:
        lat = msg_gps.lat / 1e7  # 10^7
        lon = msg_gps.lon / 1e7  
        alt = msg_gps.alt / 1000 

        # Zaman ve veriyi listeye ekleyin
        # Amaç: O anki geçen zamanı hesaplamak
        elapsed_time = time.time() - start_time # time.time() fonksiyonu, Unix zaman damgasını döndürür
        time_list.append(elapsed_time)
        roll_list.append(roll)
        pitch_list.append(pitch)
        yaw_list.append(yaw)
        lat_list.append(lat)
        lon_list.append(lon)
        alt_list.append(alt)
        
        # Grafik üzerinde çizim yapın
        # Roll verileri
        ax[0].cla()  # Eski grafikleri temizle, böylece yeni çizim üzerine eklenmez
        ax[0].plot(time_list, roll_list, label='Roll', color='r') # Roll değerlerini (roll_list) zamana (time_list) karşı çizer.
        ax[0].set_title('Roll') # grafiğin başlığı
        ax[0].set_xlabel('Time (s)') # X eksenini "Time (s)" olarak etiketle
        ax[0].set_ylabel('Degrees') # Y eksenini "Degrees" olarak etiketle

        # Pitch verileri
        ax[1].cla()
        ax[1].plot(time_list, pitch_list, label='Pitch', color='g')
        ax[1].set_title('Pitch') 
        ax[1].set_xlabel('Time (s)')
        ax[1].set_ylabel('Degrees')

        # Yaw
        ax[2].cla()
        ax[2].plot(time_list, yaw_list, label='Yaw', color='b')
        ax[2].set_title('Yaw')
        ax[2].set_xlabel('Time (s)')
        ax[2].set_ylabel('Degrees')

        # GPS verileri
        ax[3].cla()
        ax[3].plot(time_list, lat_list, label='Latitude', color='c')
        ax[3].plot(time_list, lon_list, label='Longitude', color='m')
        ax[3].set_title('GPS Data (Latitude and Longitude)')
        ax[3].set_xlabel('Time (s)')
        ax[3].set_ylabel('Degrees')
        ax[3].legend() # 

        # Altitude(irtifa) çizimi
        fig2, ax2 = plt.subplots(figsize=(10, 4)) # plt.subplots(): Bir grafik figürü (fig2) ve buna bağlı bir eksen (ax2) oluşturur. Figsize=(10, 4): Grafiğin boyutunu ayarlar
        ax2.plot(time_list, alt_list, label='Altitude', color='orange') # ax2.plot(): Verileri çizer
        ax2.set_title('Altitude over Time')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Altitude (m)')
        ax2.legend()

        # Grafiği güncelle
        plt.pause(0.1)

    time.sleep(0.1)  # Verileri çok sık almayı engellemek için biraz bekleyin
