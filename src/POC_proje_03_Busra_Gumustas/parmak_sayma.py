import cv2
import numpy as np

# Cilt rengini tanımak için HSV renk aralığı
lower_skin = np.array([0, 20, 70], dtype=np.uint8)  # Alt sınır
upper_skin = np.array([20, 255, 255], dtype=np.uint8)  # Üst sınır

# Kamerayı başlat
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    
    # Görüntüyü HSV formatına çevir
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Cilt rengini maskele
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    
    # Maskeyi açma ve kapama işlemi
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=4)
    mask = cv2.erode(mask, kernel, iterations=2)
    
    # Konturları bul
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour) < 5000:  # Küçük alanları ihmal et
            continue
        
        # Konturu etrafına bir dikdörtgen çiz
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Parmağın uç noktasını tespit et
        hull = cv2.convexHull(contour)
        defects = cv2.convexityDefects(contour, cv2.convexHull(contour, returnPoints=False))

        if defects is not None:
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(contour[s][0])
                end = tuple(contour[e][0])
                cv2.line(frame, start, end, [0, 0, 255], 2)  # parmakların uç noktaları arasına çizgi

        # Parmağın sayısını sayma (konveksiyet arızaları)
        finger_count = 0
        for i in range(len(contours)):
            if cv2.contourArea(contours[i]) > 1000:
                finger_count += 1
        
        cv2.putText(frame, f'Fingers: {finger_count}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

    # Görüntüyü göster
    cv2.imshow("Hand Detection", frame)

    # 'q' tuşuna basılınca çık
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
