import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 1. Adım: Örnek veri seti oluşturma
# Zaman dilimi (saniye cinsinden)
time = np.arange(0, 120, 1)  # 0'dan 120'ye kadar saniyeler

# Rastgele hız, yükseklik ve batarya verileri
speed = np.random.uniform(20, 100, len(time))  # 20-100 km/h arası hız
altitude = np.random.uniform(100, 3000, len(time))  # 100-3000 metre arası yükseklik
battery = np.random.uniform(20, 100, len(time))  # 20-100% arasında batarya durumu

# Verileri bir araya getirip bir DataFrame oluşturuyoruz
data = pd.DataFrame({
    'Time': time,
    'Speed': speed,
    'Altitude': altitude,
    'Battery': battery
})

# 2. Adım: Veri işleme (örneğin hız değişimini filtreleyelim)
# Burada hızın 50 km/h altında olduğu anları filtreleyebiliriz
filtered_data = data[data['Speed'] > 50]

# 3. Adım: Grafik oluşturma
plt.figure(figsize=(10, 6))

# Hız Grafiği
plt.subplot(3, 1, 1)
plt.plot(data['Time'], data['Speed'], label='Speed (km/h)', color='blue')
plt.xlabel('Time (s)')
plt.ylabel('Speed (km/h)')
plt.title('Speed Over Time')
plt.grid(True)

# Yükseklik Grafiği
plt.subplot(3, 1, 2)
plt.plot(data['Time'], data['Altitude'], label='Altitude (m)', color='green')
plt.xlabel('Time (s)')
plt.ylabel('Altitude (m)')
plt.title('Altitude Over Time')
plt.grid(True)

# Batarya Grafiği
plt.subplot(3, 1, 3)
plt.plot(data['Time'], data['Battery'], label='Battery (%)', color='red')
plt.xlabel('Time (s)')
plt.ylabel('Battery (%)')
plt.title('Battery Level Over Time')
plt.grid(True)

# Grafikleri gösterme
plt.tight_layout()
plt.show()
