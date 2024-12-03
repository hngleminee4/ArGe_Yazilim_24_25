import cv2  # Görüntü işleme ve nesne tespiti için kullanılır.
import numpy as np  # Sayısal hesaplamalar ve matris işlemleri için kullanılır.
import threading  # Çoklu işlem (multithreading) için kullanılır.
import folium  # Harita oluşturmak ve GPS koordinatlarını göstermek için kullanılır.
import serial  # Gerçek GPS verisini almak için kullanılır.

# YOLO modelini yükle (nesne tespiti yapmamızı sağlar).
net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)  # GPU hızlandırması.
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)  # GPU ile çalışması için hedef belirleme.

# COCO sınıflarını yükle
# with ifadesi, dosyayı otomatik olarak açar ve işlem tamamlanınca kapatır.
with open("coco.names", "r") as f:  # "r": Dosya okuma modu.
    classes = [line.strip() for line in f.readlines()]  # Sınıf isimlerini bir listeye yükle.

# Video akışı ve kaydedici.
cap = cv2.VideoCapture(0)  # Kameradan video akışı başlatılır.
fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Video sıkıştırma algoritması tanımlanır.
out = cv2.VideoWriter("output.avi", fourcc, 20.0, (640, 480))  # Çıktı videosu kaydedilir.

# Çıkış durdurma kontrolü
stop_threads = False  # Thread'lerin çalışmayı durdurup durdurmayacağını kontrol eder.

# Frame (video karesi) ve nesne tespit sonuçlarını paylaşacak global değişkenler.
frame = None  # Kameradan alınan video karelerini saklar.
detections = None  # YOLO modelinin yaptığı nesne tespitlerini saklar.

# Harita oluştur ve başlangıç konumunu belirle.
map_center = [39.9334, 32.8597]  # Başlangıç GPS koordinatları (örneğin, Ankara).
drone_map = folium.Map(location=map_center, zoom_start=15)  # Başlangıç haritasını oluşturur.

# GPS verisini gerçek bir cihazdan almak için seri port ayarları.
gps_serial = serial.Serial(port="COM3", baudrate=9600, timeout=1)  # GPS cihazının bağlı olduğu port.

# Gerçek GPS verilerini al.
def get_gps_coordinates():
    while True:
        line = gps_serial.readline().decode("ascii", errors="ignore").strip()  # Seri porttan GPS verisi oku.
        if line.startswith("$GPGGA"):  # NMEA protokolüne uygun olarak GPGGA verisini işliyoruz.
            data = line.split(",")
            if data[2] and data[4]:  # Enlem ve boylam verisi mevcut mu?
                latitude = float(data[2]) / 100  # GPS verisini enlemi alacak şekilde dönüştür.
                longitude = float(data[4]) / 100  # GPS verisini boylamı alacak şekilde dönüştür.
                return latitude, longitude  # Gerçek GPS koordinatlarını döndür.

# Kameradan kare yakalama.
def capture_video():
    global frame, stop_threads  # Fonksiyon içinde global değişkenlere erişim sağlanır.

    while not stop_threads:
        ret, new_frame = cap.read()  # Kameradan yeni bir kare oku.
        if not ret:
            stop_threads = True
            break
        frame = new_frame  # Yeni kare, global değişken "frame" ile güncellenir.

# Video akışındaki her kareyi işleyerek nesne tespiti yapar.
def process_objects():
    global detections, frame, stop_threads  # Global değişkenlere erişim sağlanır.

    while not stop_threads:
        if frame is not None:
            # YOLO modeli için giriş görüntüsünü hazırlama.
            blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
            net.setInput(blob)  # YOLO'ya giriş olarak blob verilir.
            detections = net.forward(net.getUnconnectedOutLayersNames())  # YOLO nesne tespit sonuçlarını döndürür.

# Nesne tespiti sonuçlarını ekrana çiz ve GPS koordinatlarını haritaya ekle.
def save_and_display():
    global detections, frame, stop_threads, drone_map  # Global değişkenlere erişim sağlanır.

    while not stop_threads:
        if frame is not None:  # Bir kare mevcutsa işlem yap.
            display_frame = frame.copy()  # Orijinal kareyi korumak için kopyasını al.

            # Tespit edilen nesneleri işle.
            if detections is not None:  # Tespit sonuçları varsa döngüye gir.
                for out in detections:
                    for detection in out:
                        scores = detection[5:]  # Tespit edilen sınıfların olasılıklarını al.
                        class_id = np.argmax(scores)  # En yüksek olasılıklı sınıfı bul.
                        confidence = scores[class_id]  # En yüksek olasılık değerini al.
                        
                        # Yalnızca "person" sınıfı için işlem yap.
                        if classes[class_id] == "person" and confidence > 0.5:
                            x, y, w, h = detection[0:4]
                            x, y, w, h = int(x * frame.shape[1]), int(y * frame.shape[0]), int(w * frame.shape[1]), int(h * frame.shape[0])
                            label = f"{classes[class_id]} {confidence:.2f}"
                            gps_coords = get_gps_coordinates()  # Gerçek GPS koordinatlarını al.

                            # Haritaya işaretleme yap.
                            folium.Marker(gps_coords, popup=label).add_to(drone_map)

                            # Tespit edilen nesneyi çiz.
                            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                            cv2.putText(display_frame, label, (x, y - 10),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            # Görüntüyü kaydet ve göster.
            out.write(display_frame)  # Görüntüyü video dosyasına kaydet.
            cv2.imshow("Tracking", display_frame)  # İşlenmiş görüntüyü ekranda göster.

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Kullanıcı 'q' tuşuna basarsa çık.
                stop_threads = True
                break

# Thread'leri başlat.
threads = [
    threading.Thread(target=capture_video),  # Kamera akışını yakalar.
    threading.Thread(target=process_objects),  # Nesne tespiti yapar.
    threading.Thread(target=save_and_display)  # Sonuçları ekrana ve haritaya çizer.
]

for thread in threads:
    thread.start()  # Her bir thread'i başlat.

# Thread'leri durdur.
for thread in threads:
    thread.join()  # Tüm thread'lerin işleminin bitmesini bekle.

# Çıkış işlemleri.
cap.release()  # Kamera kaynağını serbest bırak.
out.release()  # Video kaydını serbest bırak.
cv2.destroyAllWindows()  # Tüm açık pencereleri kapat.

# Haritayı kaydet.
drone_map.save("drone_map.html")  # Haritayı HTML dosyasına kaydet.
print("Tespit edilen konumlar haritaya kaydedildi: drone_map.html")
