import folium
import random
import json
import math

# Uçuş sınırları
ucus_sinirlari = [
    [37.860000, 32.400000],  # Sol alt köşe
    [37.860000, 32.430000],  # Sağ alt köşe
    [37.880000, 32.430000],  # Sağ üst köşe
    [37.880000, 32.400000],  # Sol üst köşe
]

# Uçuş sınırları içinde mi kontrolü
def ucus_sinirlari_icinde(lat, lon):
    return (
        ucus_sinirlari[0][0] <= lat <= ucus_sinirlari[2][0]
        and ucus_sinirlari[0][1] <= lon <= ucus_sinirlari[1][1]
    )

# İki nokta arasındaki mesafeyi hesaplama (Haversine formülü kullanmadan basit yöntem)
def mesafe_hesapla(lat1, lon1, lat2, lon2):
    return math.sqrt((lat1 - lat2) ** 2 + (lon1 - lon2) ** 2)

# HSS bölgelerinin çakışmasını önleme
def cakisma_var_mi(yeni_koordinat, yeni_yaricap, mevcut_bolgeler):
    for bolge in mevcut_bolgeler:
        eski_koordinat = bolge["koordinatlar"]
        eski_yaricap = bolge["yaricap"]
        if mesafe_hesapla(*yeni_koordinat, *eski_koordinat) < (yeni_yaricap + eski_yaricap) / 100000:
            return True
    return False

# Rastgele HSS bölgeleri oluşturma
hss_bolgeleri = []
hss_sayisi = 5
while len(hss_bolgeleri) < hss_sayisi:
    lat = random.uniform(37.860000, 37.880000)
    lon = random.uniform(32.400000, 32.430000)
    yaricap = random.randint(50, 150)  # Daha küçük yarıçaplar

    if ucus_sinirlari_icinde(lat, lon) and not cakisma_var_mi([lat, lon], yaricap, hss_bolgeleri):
        hss_bolgeleri.append({"id": len(hss_bolgeleri) + 1, "koordinatlar": [lat, lon], "yaricap": yaricap})

# HSS bölgelerini JSON dosyasına kaydetme
with open("hss_bolgeleri.json", "w") as dosya:
    json.dump(hss_bolgeleri, dosya, indent=4)
print("HSS bölgeleri JSON dosyasına kaydedildi.")

# Harita oluşturma (Konya Köyceğiz çevresi)
harita = folium.Map(location=[37.866408, 32.411824], zoom_start=14)

# JSON dosyasından HSS bölgelerini okuma
with open("hss_bolgeleri.json", "r") as dosya:
    hss_bolgeleri = json.load(dosya)

# HSS bölgelerini haritaya ekleme
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

# Sınırları çiz (Siyah renkli dikdörtgen)
folium.Polygon(
    locations=ucus_sinirlari,
    color="black",
    weight=3,
    opacity=1,
    fill=False
).add_to(harita)

# Haritayı kaydet
harita.save("hss_bolgeleri_kontrol_edilen.html")
print("Harita oluşturuldu ve hss_bolgeleri_kontrol_edilen.html dosyasına kaydedildi.")
