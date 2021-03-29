import numpy as np
import cv2
import math as m

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(10,10))
#fgbg = cv2.createBackgroundSubtractorKNN(50, 400.0, False)

while(1):
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    min_color = [200, 200, 200]
    max_color = [255, 255, 255]
    frame = cv2.inRange(frame, np.array(min_color, np.uint8), np.array(max_color,np.uint8))
    st1 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3), (-1, -1))
    st2 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3), (-1, -1))
    frame = cv2.morphologyEx(frame, cv2.MORPH_CLOSE, st1)
    frame = cv2.morphologyEx(frame, cv2.MORPH_OPEN, st2)
    frame = cv2.medianBlur(frame, 3)

    circles = cv2.HoughCircles(frame, cv2.HOUGH_GRADIENT, 1, 1, np.array([]), 80, 50, 5, 0)
    if circles is not None and len(circles)>0:
        maxRadius = 0
        x = 0
        y = 0
        found = False
        p = circles[0]
        #print(circles[0][:, [0, 1]])
        p_new = []
        for el in p:
            if (m.pi * el[2] ** 2) > 20:
                p_new.append(el)
        print(len(p_new))
        #p = p_new[:, [0, 1]]
        #print(p[0])
        p_new = np.array(p_new)
        for el in p_new:
            frame = cv2.circle(frame, (el[0], el[1]), 5, 100, -1)
        np.median(p_new.transpose()[0])
        frame = cv2.circle(frame, (np.median(p_new.transpose()[0]), np.median(p_new.transpose()[1])), 10, 200, -1)
        frame = cv2.circle(frame, (np.mean(p_new.transpose()[0]), np.mean(p_new.transpose()[1])), 5, 10, -1)
        mat = np.array([[((p[i][0] - p[j][0]) ** 2 + (p[i][1] - p[j][1]) ** 2) ** 0.5 for i in range(len(p))] for j in range(len(p))])
        #print(mat)
        #print(min(map(min, circles[0][:, [0, 1]])))
        cv2. imwrite('img.jpg', frame)
        #break

    cv2.imshow('frame', frame)
    k = cv2.waitKey(30) & 0xff
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()