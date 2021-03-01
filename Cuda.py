import numpy as np
import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(10,10))
fgbg = cv2.createBackgroundSubtractorKNN(50, 400.0, False)

while(1):
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    min_color = [0, 0, 137]
    max_color = [194, 29, 254]
    #frame = cv2.inRange(frame, np.array(min_color, np.uint8), np.array(max_color,np.uint8))
    hsv = cv2.cvtColor(frame,cv2.COLOR_HSV2BGR_FULL)
    #fgmask = fgbg.apply(frame)
    #fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
    hsv = cv2.inRange(hsv, np.array(min_color, np.uint8), np.array(max_color,np.uint8))

    hsv = cv2.GaussianBlur(hsv, (5, 5), 2)
    st1 = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10), (-1, -1))
    st2 = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10), (-1, -1))
    hsv = cv2.morphologyEx(hsv, cv2.MORPH_CLOSE, st1)
    hsv = cv2.morphologyEx(hsv, cv2.MORPH_OPEN, st2)



    circles = cv2.HoughCircles(hsv, cv2.HOUGH_GRADIENT, 2, 5, np.array([]), 80, 50, 5, 0)
    if circles is not None:
        maxRadius = 0
        x = 0
        y = 0
        found = False

        print(circles)
    cv2.imshow('frame',hsv )
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()