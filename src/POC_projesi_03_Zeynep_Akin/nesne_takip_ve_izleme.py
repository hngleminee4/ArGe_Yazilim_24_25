import cv2
from ultralytics import YOLO
import cvzone
import supervision as sv
import math
import time

# YOLO modelini yükle
model = YOLO("yolov8n.pt")

# airplane sınıfının ID'sini bulma
plane_class_name = "airplane"
plane_class_id = None
for class_id, class_name in model.model.names.items():
    if class_name.lower() == plane_class_name.lower():
        plane_class_id = class_id
        break

if plane_class_id is None:
    raise ValueError(f"Modelde '{plane_class_name}' sınıfı tanımlı değil. Lütfen doğru bir model kullanın.")

# Video kaynağını aç
cap = cv2.VideoCapture("iha.mp4")  # Video dosyasını işleme

# Video kayıt için ayarlar
cv2_fourcc = cv2.VideoWriter_fourcc(*'mp4v')
success, frame = cap.read()
if not success:
    raise ValueError("Videoyu okuyamıyor.")
size = (frame.shape[1], frame.shape[0])
video_writer = cv2.VideoWriter("output_video.mp4", cv2_fourcc, 24, size)

# Supervision kutu anotatörü
box_annotator = sv.BoxAnnotator(thickness=2)

# FPS hesaplama
prev_frame_time = 0
new_frame_time = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    new_frame_time = time.time()

    # YOLOv8 ile tespit ve takip
    results = model.track(source=frame, show=False, stream=True)

    for result in results:
        detections = sv.Detections(
            xyxy=result.boxes.xyxy.cpu().numpy(),
            confidence=result.boxes.conf.cpu().numpy(),
            class_id=result.boxes.cls.cpu().numpy().astype(int)
        )

        # Takip kimliklerini ekle
        if result.boxes.id is not None:
            detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)

        # Sadece airplane sınıfını filtrele
        detections = detections[detections.class_id == plane_class_id]

        # Görselleştirme ve etiketleme
        for i in range(len(detections.xyxy)):
            x1, y1, x2, y2 = detections.xyxy[i]
            class_id = detections.class_id[i]
            confidence = detections.confidence[i]
            tracker_id = detections.tracker_id[i] if detections.tracker_id is not None else None

            # Görselleştirme
            label = f"{tracker_id} {model.model.names[class_id]} {confidence:0.2f}"
            w, h = int(x2 - x1), int(y2 - y1)
            cvzone.cornerRect(frame, (int(x1), int(y1), w, h))
            cvzone.putTextRect(frame, label, (max(0, int(x1)), max(35, int(y1))),
                               scale=1, thickness=1)

            # Takip çizgileri (Merkez noktalar)
            cx, cy = int(x1 + w // 2), int(y1 + h // 2)
            cx2, cy2 = frame.shape[1] // 2, frame.shape[0] // 2
            cv2.circle(frame, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (cx2, cy2), 5, (255, 0, 255), cv2.FILLED)
            cv2.line(frame, (cx2, cy2), (cx, cy), (255, 0, 0), 2)

    # Video yazma
    video_writer.write(frame)

    # FPS hesaplama
    fps = 1 / (new_frame_time - prev_frame_time)
    prev_frame_time = new_frame_time
    cv2.putText(frame, f"FPS: {int(fps)}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Görüntüyü ekranda göster
    cv2.imshow("YOLOv8 Airplane Detection with Tracking", frame)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC tuşu ile çıkış
        break

cap.release()
video_writer.release()
cv2.destroyAllWindows()
