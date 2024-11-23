import folium
import json
import random
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import pandas as pd

# Uçuş sınırları
ucus_sinirlari = [
    [37.860000, 32.400000],  # Sol alt köşe
    [37.860000, 32.430000],  # Sağ alt köşe
    [37.880000, 32.430000],  # Sağ üst köşe
    [37.880000, 32.400000],  # Sol üst köşe
]

# Rota
rota = [
    [37.866408, 32.411824], [37.868000, 32.415000], [37.870000, 32.420000],
    [37.875424, 32.423035], [37.875175, 32.410410], [37.866408, 32.411824]
]

# Harita oluşturma
harita = folium.Map(location=rota[0], zoom_start=14)

folium.PolyLine(
    locations=rota,
    color="blue",
    weight=2.5,
    opacity=1
).add_to(harita)

# Sınırları çiz
folium.Polygon(
    locations=ucus_sinirlari,
    color="black",
    weight=3,
    opacity=1,
    fill=False
).add_to(harita)

# HSS bölgelerini yükle
with open("hss_bolgeleri.json", "r") as dosya:
    hss_bolgeleri = json.load(dosya)

for hss in hss_bolgeleri:
    koordinat = hss["koordinatlar"]
    yaricap = hss["yaricap"]
    folium.Circle(
        location=koordinat,
        radius=yaricap,
        color="red",
        fill=True,
        fill_opacity=0.4,
        popup=f"HSS Bölgesi {hss['id']} (Yarıçap: {yaricap} m)"
    ).add_to(harita)

# Toplam rota uzunluğunu hesapla
toplam_mesafe = 0
for i in range(len(rota) - 1):
    toplam_mesafe += geodesic(rota[i], rota[i + 1]).meters


batarya = 100  # %
hiz_min = 200 / 3.6  # m/s
hiz_max = 250 / 3.6  # m/s
kalan_mesafe = toplam_mesafe
zaman = 0


plt.ion()
fig, ax = plt.subplots(3, 1, figsize=(10, 8))

zamanlar = []
batarya_seviyeleri = []
hizlar = []
kalan_mesafeler = []

# Telemetri verileri
telemetri_verileri = []

# Ana döngü rota üzerinde gezinme
for i in range(len(rota) - 1):
    nokta1 = rota[i]
    nokta2 = rota[i + 1]
    mesafe = geodesic(nokta1, nokta2).meters

    while mesafe > 0:
        # Hızzı rastgele seç
        hiz = random.uniform(hiz_min, hiz_max)
        yol = hiz
        zaman += 1
        mesafe -= yol
        kalan_mesafe -= yol
        batarya -= 100 / toplam_mesafe * yol

        # Telemetri verisini kaydet
        veri = {
            "zaman": zaman,
            "enlem": nokta1[0],
            "boylam": nokta1[1],
            "hiz": hiz * 3.6,  # km/h
            "batarya": max(batarya, 0),
            "kalan_mesafe": max(kalan_mesafe, 0)
        }
        telemetri_verileri.append(veri)

        # Grafik için verileri güncelle
        zamanlar.append(zaman)
        batarya_seviyeleri.append(veri["batarya"])
        hizlar.append(veri["hiz"])
        kalan_mesafeler.append(veri["kalan_mesafe"])

        # Grafikleri çiz
        ax[0].cla()
        ax[0].plot(zamanlar, batarya_seviyeleri, color="red", label="Batarya (%)")
        ax[0].set_ylabel("Batarya Seviyesi (%)")
        ax[0].legend()
        ax[0].grid()

        ax[1].cla()
        ax[1].plot(zamanlar, hizlar, color="blue", label="Hız (km/h)")
        ax[1].set_ylabel("Hız (km/h)")
        ax[1].legend()
        ax[1].grid()

        ax[2].cla()
        ax[2].plot(zamanlar, kalan_mesafeler, color="green", label="Kalan Mesafe (m)")
        ax[2].set_ylabel("Mesafe (m)")
        ax[2].set_xlabel("Zaman (saniye)")
        ax[2].legend()
        ax[2].grid()

        plt.tight_layout()
        plt.pause(0.01)

        # Haritaya telemetri noktalarını ekle
        folium.Marker(location=nokta1, popup=f"Zaman: {zaman} s\nBatarya: {veri['batarya']}%").add_to(harita)

# Haritayı kaydet
harita.save("rota_ve_hss_bolgeleri.html")

# Telemetri verilerini hson olarak kaydet
with open("telemetri_verileri.json", "w") as dosya:
    json.dump(telemetri_verileri, dosya, indent=4)

plt.ioff()
plt.show()

print(f"Toplam uçuş süresi: {zaman} saniye")
print("Harita 'rota_ve_hss_bolgeleri.html' olarak kaydedildi.")
print("Telemetri verileri 'telemetri_verileri.json' dosyasına kaydedildi.")
