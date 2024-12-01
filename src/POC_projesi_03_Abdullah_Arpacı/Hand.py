import cv2 as cv
from cvzone.HandTrackingModule import HandDetector
import pıns

#kamera açma
cap = cv.VideoCapture(0)

detector = HandDetector(staticMode=True, maxHands=1,minTrackCon=0.5,modelComplexity=1,detectionCon=0.5)

#kameranın açılışını kontrol eder eğer açılmadıysa hata verir
if not cap.isOpened:
    print("Error1")
    exit()




while True:
    ret, frame = cap.read()

    if not ret:
        print("Error2")
        break

    #el tespitinin yapılır ve her frame üzerine anlık olarak elin landmarks noktalarının çizilir
    hands, frame = detector.findHands(frame,draw= True,flipType=True)

    #eğer el algılandıysa if bloğuna girer
    if hands:

        hand1 = hands[0]


        #parmak sayısı bulunur
        fingers1 = detector.fingersUp(hand1)
        sumFinger = fingers1.count(1)
        #ledleri kontrol eden fonksiyon
        pıns.blinking(sumFinger)
        sumFinger = str(sumFinger)

        #parmak sayısını frame üzerinde text olarak gösterilir
        cv.putText(frame,sumFinger, (50, 50), cv.FONT_HERSHEY_SIMPLEX, 1, (0 , 255,0), 2)
    cv.imshow('frame', frame)

    if cv.waitKey(1) & 0xFF == ord("q"):
        print("The video file is closed")
        break

cap.release()
cv.destroyAllWindows()
pıns.cleanup_gpio()