import cv2
import numpy as np

import ApClass
import Reading

# старые знакомые декорации
# ребро квадрата
size = 20

# расположение квадрата
X = 200
Y = 100
SHIFT = 100

PRINT = "PRINT"
READ = "READ"


# Примениние кучи фильтров к картинке и возврат белого пятна
# Команда: ослепи меня, но не сильно
def get_filtered_img(img):
    filter = cv2.inRange(img, np.array(ApClass.Application.min_color), np.array(ApClass.Application.max_color))
    st1 = cv2.getStructuringElement(cv2.MORPH_RECT, (ApClass.Application.coef_data[1],
                                                     ApClass.Application.coef_data[1]), (-1, -1))
    st2 = cv2.getStructuringElement(cv2.MORPH_RECT, (ApClass.Application.coef_data[2],
                                                     ApClass.Application.coef_data[2]), (-1, -1))
    filter = cv2.morphologyEx(filter, cv2.MORPH_CLOSE, st1)
    filter = cv2.morphologyEx(filter, cv2.MORPH_OPEN, st2)
    filter = cv2.medianBlur(filter, 2 * ApClass.Application.coef_data[0] + 1)
    return filter


# ПАРАМЕТРИЗАЦИЯ кода для чтения и рисования в режиме ANY
def do_any(print_read, frame):
    width = len(frame[0])
    height = len(frame)
    y_new = Y
    x_new = X
    if 3 <= ApClass.Application.count_click < 6:
        x_new = width - X
    if 6 <= ApClass.Application.count_click < 9:
        x_new = X
        y_new = height - Y
    if ApClass.Application.count_click >= 9:
        x_new = width - X
        y_new = height - Y
    if print_read == PRINT:
        return cv2.rectangle(frame, (x_new - 1, y_new - 1), (x_new + size + 1, y_new + size + 1),
                             (255, 0, 0), 1)
    if print_read == READ:
        min_color1, max_color1 = Reading.find_all_colors(frame, x_new + 1, y_new + 1)
        ApClass.Application.min_color = Reading.find_min_coomp(ApClass.Application.min_color, min_color1)
        ApClass.Application.max_color = Reading.find_max_coomp(ApClass.Application.max_color, max_color1)


# ПАРАМЕТРИЗАЦИЯ кода для чтения и рисования в режиме HAND
def do_hand(print_read, frame):
    if ApClass.Application.count_click < 12:
        x = len(frame[0]) // 2 - size // 2 - size * 2
        y = len(frame) // 2 - size // 2 - size * 2
        img = frame
        for i in range(0, 6, 2):
            for j in range(0, 9, 3):
                if print_read == PRINT:
                    img = cv2.rectangle(img, (x - 1 + i * size, y - 1 + j * size),
                                        (x + 1 + (i + 1) * size, y + 1 + (j + 1) * size), (255, 0, 0,), 1)

                if print_read == READ:
                    min_color1, max_color1 = Reading.find_all_colors(frame, x + i * size, y + j * size)
                    ApClass.Application.min_color = Reading.find_min_coomp(ApClass.Application.min_color, min_color1)
                    ApClass.Application.max_color = Reading.find_max_coomp(ApClass.Application.max_color, max_color1)

        if print_read == PRINT:
            return img

#go to Reading.py (last file)

# написанный ниже комментарий не обладает смысловой ценностью для понимания кода (поэтому и написан в конце),
# а так же не является действующей частью (просто мысли недовольного автора) и при прочтении может быть пропущен

# параметризация, параметризация, параметризация. Она то она, да не совсем
# в данном контексте имеется ввиду упрощение в виде применеие разного блока-набора функций по одному геометрическому положению
# вообще было бы круто отправить не параметр-число, а параметр-функцию, но в данном случае усложнит читаемость да и понятность кода.
# поэтому параметризация такая какая она есть (Это больше такая метафора параметризации на самом деле)