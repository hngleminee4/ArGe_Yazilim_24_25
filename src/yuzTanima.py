import cv2

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
#Haar Cascade, yüz tanıma için eğitilmiş hazır bir model olduğu için kullandık
#"cv2.data.haarcascades" dosya yolunun adı
#"haarcascade_frontalface_default.xml" yüz algılama için özel olarak eğitilmiş bir Haar Cascade modelidir.

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    #renk skalasını değiştirp nesne tespitini kolaylaştırıyor
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Yüzleri algıla
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Tespit edilen yüzlerin etrafına dikdörtgen çiz
    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)

    # Yüz sayısını ekrana yazdır
    face_count = len(faces)
    cv2.putText(img, f'Face Count: {face_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Görüntüyü göster
    cv2.imshow("Face Detection", img)

    # 'q' tuşuna basıldığında döngüyü kır ve çık
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kaynakları serbest bırak
cap.release()
cv2.destroyAllWindows()