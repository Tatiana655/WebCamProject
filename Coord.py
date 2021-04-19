import cv2
import numpy as np
import Definitions as Def
from sklearn.metrics import pairwise

ANY = Def.ANY
HAND = Def.HAND
READ_MODE = Def.READ_MODE


# найди максимальный контур
def find_max_cont(contours):
    if len(contours) == 0:
        return []
    maxArea = max([cv2.contourArea(c) for c in contours])
    # print(maxArea)
    if maxArea < 3000:
        return []
    for c in contours:
        if cv2.contourArea(c) == maxArea:
            return c


# дай пж координаты пальца, если можешь
def find_finger(img, max_cont):
    conv_hull = cv2.convexHull(max_cont)
    top = tuple(conv_hull[conv_hull[:, :, 1].argmin()][0])
    bottom = tuple(conv_hull[conv_hull[:, :, 1].argmax()][0])
    left = tuple(conv_hull[conv_hull[:, :, 0].argmin()][0])
    right = tuple(conv_hull[conv_hull[:, :, 0].argmax()][0])
    cx = (left[0] + right[0]) // 2  # тут посмотри потом
    cy = (top[1] + bottom[1]) // 2

    dist = pairwise.euclidean_distances([left, right, bottom, top], [[cx, cy]])[0]
    radi = int(0.80 * dist)

    circular_roi = np.zeros_like(img, dtype='uint8')
    cv2.circle(circular_roi, (cx, cy), radi, 255, 8)

    img2 = img.copy()
    mask = cv2.bitwise_and(img2, img2, mask=circular_roi)
    # mask
    con, hie = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    count = 0
    circumfrence = 2 * np.pi * radi
    for cnt in con:
        (m_x, m_y, m_w, m_h) = cv2.boundingRect(cnt)
        out_wrist_range = (cy + (cy * 0.25)) > (m_y + m_h)
        limit_pts = (circumfrence * 0.25) > cnt.shape[0]
        if limit_pts and out_wrist_range:
            # print(limit_pts,out_wrist_range)
            count += 1
    for cnt in con:
        (m_x, m_y, m_w, m_h) = cv2.boundingRect(cnt)
        out_wrist_range = (cy + (cy * 0.25)) > (m_y + m_h)
        limit_pts = (circumfrence * 0.25) > cnt.shape[0]
        if limit_pts and out_wrist_range:
            # print(limit_pts,out_wrist_range)
            count += 1
    print(count)
    if count <= 3:
        return top[0], top[1]

    return -1, -1


# дай координаты, если можешь, если нет, дай (-1, -1)
def get_coord(img, calibr_mode):
    x = -1
    y = -1
    contours, hierarchy = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # найти контур с наибольшей площадью и в этом прямоугольнике искать
    max_cont = find_max_cont(contours)
    if len(max_cont) > 0 and cv2.contourArea(max_cont) > 5000:
        x_n, y_n, w, h = cv2.boundingRect(max_cont)
        if (x_n != 0) and (y_n != 0):
            if calibr_mode == READ_MODE[HAND]:
                x, y = find_finger(img, max_cont)
            if calibr_mode == READ_MODE[ANY]:
                x = x_n + w // 2
                y = y_n + h // 2
    return x, y

# go to ImgTransform.py
