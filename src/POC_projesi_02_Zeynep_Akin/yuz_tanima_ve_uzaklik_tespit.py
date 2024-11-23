import cv2
import pandas as pd
import matplotlib.pyplot as plt
import time
import folium
from folium.plugins import HeatMap
import numpy as np

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)

# IDleri tutmak için kullanlan veri yapıları
face_data = {}  # mevcut yüzler
final_face_data = []  # saklanacak idler
face_distance_over_time = {}  # zaman ve mesafe tutuyor

face_id = 0
threshold_distance = 70  # benzerlik için kullandık

# kameranın default değeri
camera_lat, camera_lon = 37.866300, 32.419962  # atölyenin konumu (umarım)

print("Kamera çalışıyor. Çıkmak için 'q' tuşuna basın.")

while True:
    success, img = cap.read()
    if not success:
        break

    # gri tonlamalı görüntüye dönüştür ve kontrastı iyileştir
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)  # gürültüyü azaltır
    faces = face_cascade.detectMultiScale(gray, 1.1, 5)

    # aktif yüzlerin takibi için
    current_faces = {}

    for (x, y, w, h) in faces:
        distance = round(6000 / w, 2)  # mesafe tahmini
        cx, cy = x + w // 2, y + h // 2  # yüzün merkezi
        matched_id = None

        # daha önce algılanan yüzlerle karşılaştır
        for fid, data in face_data.items():
            prev_cx, prev_cy = data["position"]
            if abs(cx - prev_cx) < threshold_distance and abs(cy - prev_cy) < threshold_distance:
                matched_id = fid
                break

        if matched_id is None:
            # yeni yüzse kayıt işlemleri gerçekleştir
            matched_id = face_id + 1
            face_data[matched_id] = {"position": (cx, cy), "start_time": time.time(), "distance": distance,
                                     "assigned": False}

        # güncelle
        face_data[matched_id]["position"] = (cx, cy)
        face_data[matched_id]["distance"] = distance
        current_faces[matched_id] = face_data[matched_id]

        # yüz 0.3 saniyeden uzun süre algılanıyorsa id ver (kitap vs tespiti için geliştirdim)
        if not face_data[matched_id]["assigned"]:
            duration = time.time() - face_data[matched_id]["start_time"]
            if duration > 0.3:
                face_id += 1
                face_data[matched_id]["assigned"] = True
                face_data[matched_id]["final_id"] = face_id

        # mesafe ve zamanı kaydet
        current_time = time.time()
        if matched_id not in face_distance_over_time:
            face_distance_over_time[matched_id] = {"time": [], "distance": []}
        face_distance_over_time[matched_id]["time"].append(current_time)
        face_distance_over_time[matched_id]["distance"].append(distance)

        # yüzü dikdörtgen içine al ve mesafeyi yaz
        final_id = face_data[matched_id].get("final_id", "Tespit Ediliyor")
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.putText(img, f'ID:{final_id} {distance}cm', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        # yüz aktif değilse, aktif idlerden silip son listeye ekleme işlemleri gerçekleşir
        for fid in list(face_data.keys()):
            if fid not in current_faces:
                if face_data[fid]["assigned"]:  # kimlik atanmış yüzleri sadece kaydet
                    duration = time.time() - face_data[fid]["start_time"]
                    # Tahmini enlem ve boylam hesapla
                    lat_offset = (np.random.rand() - 0.5) * 0.0002
                    lon_offset = (np.random.rand() - 0.5) * 0.0002
                    final_face_data.append({
                        "Face ID": face_data[fid]["final_id"],
                        "Distance (cm)": face_data[fid]["distance"],
                        "Duration (s)": round(duration, 2),
                        "Latitude": camera_lat + lat_offset,
                        "Longitude": camera_lon + lon_offset,
                    })
                del face_data[fid]  # framede yoksa sil

    # framede algılanan yüzlerin sayısını göster
    face_count = len(current_faces)
    cv2.putText(img, f'Face Count: {face_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow("Face Detection and Tracking", img)

    # çıkış için 'q' tuşuna bas
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# tablo oluştrma
face_timing_data = []

for face_id, data in face_distance_over_time.items():
    start_time = min(data["time"]) - min(data["time"])  # İlk tespit anı
    end_time = max(data["time"]) - min(data["time"])  # Son tespit anı
    distance_mean = round(sum(data["distance"]) / len(data["distance"]), 2)  # Ortalama mesafe

    # Faceid bilgilerini tabloya ekle
    face_timing_data.append({
        "Face ID": face_id,
        "Start Time (s)": round(start_time, 2),
        "End Time (s)": round(end_time, 2),
        "Mean Distance (cm)": distance_mean
    })

# verileri pandas DataFrame'e dönüştür
face_timing_df = pd.DataFrame(face_timing_data)

# Tabloyu konsola yazdır
print("Düzenlenmiş Zaman Tablosu:")
print(face_timing_df)

# harita olusturuldu
m = folium.Map(location=[camera_lat, camera_lon], zoom_start=18)
heat_data = pd.DataFrame(final_face_data)[["Latitude", "Longitude", "Duration (s)"]].values.tolist()
HeatMap(heat_data, radius=15, blur=20, max_zoom=1).add_to(m)

# haritayı kaydettim
map_path = "C:/Users/Zeynep/Desktop/Sprints/Sprint02/haritalandirma.html"
m.save(map_path)
print(f"Harita kaydedildi: {map_path}")

# zaman serisi grafiği
plt.figure(figsize=(12, 6))
for face_id, data in face_distance_over_time.items():
    relative_times = [t - min(data["time"]) for t in data["time"]]  # Zamanı başlatma noktası olarak normalize et
    plt.plot(relative_times, data["distance"], label=f"Face ID {face_id}")

plt.title("Mesafelerin Zamana Göre Değişimi", fontsize=16)
plt.xlabel("Zaman (saniye)", fontsize=12)
plt.ylabel("Mesafe (cm)", fontsize=12)
plt.legend(fontsize=10)
plt.grid(True)
plt.show()

# sütun grafiği
plt.figure(figsize=(12, 6))
for index, row in face_timing_df.iterrows():
    plt.barh(
        row["Face ID"],
        row["End Time (s)"] - row["Start Time (s)"],
        left=row["Start Time (s)"],
        height=0.4,
        label=f"Face {row['Face ID']}"
    )

plt.title("Yüz Tanıma Süreleri (Başlangıç Ve Bitiş Süreleri)", fontsize=16)
plt.xlabel("Time (seconds)", fontsize=12)
plt.ylabel("Face ID", fontsize=12)
plt.yticks(face_timing_df["Face ID"])
plt.grid(axis="x", linestyle="--", alpha=0.7)
plt.legend(title="Face IDs", bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()
