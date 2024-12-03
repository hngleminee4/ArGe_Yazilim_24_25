# -*- coding: utf-8 -*-
"""
Created on Thu Nov 28 12:57:15 2024
@author: emine
"""
import cv2
import mediapipe as mp
"""
import RPi.GPIO as GPIO
from gpiozero import LED
"""
mp_hands = mp.solutions.hands #eli izlemek için kullanılır.
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.5)
mp_draw = mp.solutions.drawing_utils #el bağlantılarını gösterir
"""
GPIO.setmode(GPIO.BCM)


green= LED(5)
green2= LED(6)
green3= LED(13)
green4= LED(19)
green5= LED(26)



led_pins=[5,6,13,19,26]
"""
def control_leds(finger_states):#finger states parmakların durumunu belirtir. Yani aşağıda mı yukarı da mı bilgisini verir.
    finger_names = ["Thumb", "Index", "Middle", "Ring", "Pinky"]
    for i, state in enumerate(finger_states):
        if not state:
            led_pins[i].on()
        else:
            led_pins[i].off()


def check_fingers_down(hand_landmarks, width, height):
    fingers = []

    #mantığı anladığım kadarıyla 1 elde toplam 21 nokta var her parmakta 4 tane ve merkezde de bir tane nokta var. Oyüzden 4 er artıyor.
    finger_tip_ids = [4, 8, 12, 16, 20]

    #baş parmağın durumunu algılamak için parmak ucu ile orta eklemi kıyaslar. Uç ortadaki eklemden aşağıdaysa parmak indirilmiş durumundadır.
    thumb_tip = hand_landmarks.landmark[finger_tip_ids[0]]
    thumb_ip = hand_landmarks.landmark[3]
    fingers.append(thumb_tip.y > thumb_ip.y)

    #diğer parmaklar için kontrol de aynı şekilde sağlanır ama bu kısımda idsten 2 çıkarmanın sebebi diğer parmaklarda indirdiğimizde parmak ucu parmağı el gövdesine bağlayan eklemin hizasının altında oluyor.
    for i in range(1, 5):
        fingertip = hand_landmarks.landmark[finger_tip_ids[i]]
        pip_joint = hand_landmarks.landmark[finger_tip_ids[i] - 2]
        fingers.append(fingertip.y > pip_joint.y)

    return fingers

cap = cv2.VideoCapture(0)

while True:
     success, img = cap.read()
     if not success:
         print("Goruntu yakalanamadi.")
         break
     #BGRden RGBye geçiş
     img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
     results = hands.process(img_rgb)

     height, width, _ = img.shape

     if results.multi_hand_landmarks:
         for hand_landmarks in results.multi_hand_landmarks:
             #parmak durumunu kontrol
             finger_states = check_fingers_down(hand_landmarks, width, height)

             #parmak durumuna göre led kontrolü yapıyoruz.
             control_leds(finger_states)

             mp_draw.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

     cv2.imshow("el algılama", img)

     if cv2.waitKey(1) & 0xFF == ord('q'):
         break

cap.release()
cv2.destroyAllWindows()
