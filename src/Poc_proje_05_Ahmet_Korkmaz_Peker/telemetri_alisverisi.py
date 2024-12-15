from pymavlink import mavutil

# MAVLink bağlantısı başlatılıyor
connection = mavutil.mavlink_connection('udp:127.0.0.1:14550')  # SITL veya gerçek bir drone bağlantısı

# UAV bağlantısı bekleniyor
print("UAV bağlantısı bekleniyor...")
connection.wait_heartbeat()
print("Bağlantı sağlandı! UAV Heartbeat alındı.")

# Telemetri verilerini almak için sürekli bir döngü
try:
    while True:
        # 'VFR_HUD' mesajını al (örn. hız, yüksekliği içeren veri)
        message = connection.recv_match(type='VFR_HUD', blocking=True)
        if message:
            # Gelen telemetri verilerini yazdır
            print(f"Hız: {message.airspeed} m/s, Yükseklik: {message.alt} m, Tırmanma Hızı: {message.climb} m/s")
        
        # Örnek: UAV'ye bir komut göndermek
        # Aracın modunu 'GUIDED' olarak ayarlamak
        connection.mav.set_mode_send(
            connection.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
            4  # GUIDED mode
        )
except KeyboardInterrupt:
    print("Bağlantı sonlandırılıyor.")
    connection.close()
