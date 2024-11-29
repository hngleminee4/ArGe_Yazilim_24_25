import cv2
import numpy as np

# Renklerin HSV aralıklarını tanımlayın
colors = {
    "Kırmızı": ([0, 120, 70], [10, 255, 255]),
    "Turuncu": ([11, 100, 100], [25, 255, 255]),
    "Sarı": ([26, 100, 100], [35, 255, 255]),
    "Yeşil": ([36, 50, 50], [85, 255, 255]),
    "Mavi": ([86, 50, 50], [125, 255, 255]),
    "Mor": ([126, 50, 50], [170, 255, 255]),
    "Beyaz": ([0, 0, 200], [180, 50, 255])
}

selected_color_name = None  # Varsayılan seçili renk yok

# Kamerayı başlat
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Kamera açılamadı!")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Kare alınamadı!")
        break

    # HSV uzayına dönüştür
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Seçili renk varsa maske oluştur
    if selected_color_name:
        lower_bound, upper_bound = colors[selected_color_name]
        lower_bound = np.array(lower_bound)
        upper_bound = np.array(upper_bound)

        # Maske oluştur ve görüntüye uygula
        mask = cv2.inRange(hsv_frame, lower_bound, upper_bound)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            if cv2.contourArea(contour) > 100:
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Yeşil dikdörtgen

        white_pixels = np.sum(mask == 255)
        total_pixels = mask.size
        percentage = (white_pixels / total_pixels) * 100

        if key == ord('1'):
            print(f"Kırmızı renk ekranın {percentage:.2f}% kaplıyor.")
        elif key == ord('2'):
            print(f"Turuncu renk ekranın {percentage:.2f}% kaplıyor.")
        elif key == ord('3'):
            print(f"Sarı renk ekranın {percentage:.2f}% kaplıyor.")
        elif key == ord('4'):
            print(f"Yeşil renk ekranın {percentage:.2f}% kaplıyor.")
        elif key == ord('5'):
            print(f"Mavi renk ekranın {percentage:.2f}% kaplıyor.")
        elif key == ord('6'):
            print(f"Mor renk ekranın {percentage:.2f}% kaplıyor.")
        elif key == ord('7'):
            print(f"Beyaz renk ekranın {percentage:.2f}% kaplıyor.")

        # Maskeyi ve sonucu göster
        cv2.imshow("Mask", mask)
        cv2.imshow("Filtered Result", result)

    # Ana görüntüyü göster
    cv2.imshow("Frame", frame)

    # Klavye girişi ile renk seçimi
    key = cv2.waitKey(1) & 0xFF
    if key == ord('1'):
        selected_color_name = "Kırmızı"
    elif key == ord('2'):
        selected_color_name = "Turuncu"
    elif key == ord('3'):
        selected_color_name = "Sarı"
    elif key == ord('4'):
        selected_color_name = "Yeşil"
    elif key == ord('5'):
        selected_color_name = "Mavi"
    elif key == ord('6'):
        selected_color_name = "Mor"
    elif key == ord('7'):
        selected_color_name = "Beyaz"
    elif key == ord('q'):  # Çıkış tuşu
        break



cap.release()
cv2.destroyAllWindows()
