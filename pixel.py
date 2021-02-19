import cv2
import numpy as np
size = 20
X = 200
Y = 100
mode = False

def find_min_coomp(vec1, vec2):
    for i in range(len(vec1)):
        vec1[i] = min(vec1[i], vec2[i])
    return vec1
def find_max_coomp(vec1, vec2):
    for i in range(len(vec1)):
        vec1[i] = max(vec1[i], vec2[i])
    return vec1
def subtract_vectors(v, w):
    res =3*255
    for i in range(len(v)):
        res = min(res, int(v[i])-int(w[i]))
    return res

#ищет два вектора цвета в квадратике(это буквально квадрат)
def find_all_colors(img):
    min_color = [255, 255, 255]
    max_color = [0, 0, 0]
    # мне кажется, тут можно написать и короче. Я не знаток питона :(. тогда мб функция не нужна
    for i in range(Y, Y + size):
        for j in range(X, X + size):
            for k in range(3):
                min_color[k] = min(img[i][j][k], min_color[k])
                max_color[k] = max(img[i][j][k], min_color[k])
    return min_color, max_color

#ищет точку(пиксель)
def find_point(img, min_color, max_color):
    for i in range(len(img) // (size // 15)):  # y
        for j in range(len(img[0]) // (size // 15)):  # x
            if ((subtract_vectors(img[i][j], min_color)) >= 0) and ((subtract_vectors(max_color, img[i][j])) >= -100):

                return j*(size // 15), i*(size // 15)
    return -1, -1

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

ret, old_frame = cap.read()
mask = np.zeros_like(old_frame)
mask = cv2.flip(mask, 1)

min_color = [255, 255, 255]
max_color = [0, 0, 0]
f = 0
while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    start_point = (X-1, Y-1)
    end_point = (X + size+1, Y + size+1)
    color = (255, 0, 0)
    thickness = 1
    if mode == False:
        frame = cv2.rectangle(frame, start_point, end_point, color, thickness)

    if cv2.waitKey(10) == ord('a'):
        min_color1, max_color1 = find_all_colors(frame)
        min_color = find_min_coomp(min_color, min_color1)
        max_color = find_max_coomp(max_color, max_color1)
        f += 1
        if f == 1:
            mode = True
            x0 = -1############
            y0 = -1########

    if (mode):
        x1, y1 = find_point(frame, min_color, max_color) #возвращает какую-то точку на сетке, т.е. надо ещё сам квадрат-маркер найти и усреднить координату
        #print(x1,y1)
        if x0 >= 0 and y0 >= 0:
            mask = cv2.line(mask, (x0, y0), (x1, y1), [255, 0, 0], 2)#раз уж можно не отрисовывать каждый раз все
        x0 = x1
        y0 = y1

    img = cv2.add(frame, mask)
    cv2.imshow("Cam", img)
    if cv2.waitKey(10) == 27: # Клавиша Esc
        break
    if not cv2.getWindowProperty('Cam', 0) >= 0:
        break

cap.release()
cv2.destroyAllWindows()
#FindMask - функция получает изображение и цвет который надо найти, строит сетку и возвращает координаты. Тут шум мб проблема. КАК ОКАЗАЛОСЬ это глобальная проблема
#FindAllObj - функция получает цвет и координату пикселя и смотрит есть ли такие же пиксели вокруг, возвращает двумерный массив
#Из этого двумерного массива достать среднее значение координату - сохранить в массив точек(?)// можно не усреднять, а просто переносить
# соеденить точки вектором, напечатать куда-то //нарисовать линию. line(x1,y1,x2,y2)
#Найди рядом пиксели. функция проверяет цвет текущего пикселя или ищет рядом по спирали(...) FindAllObj снова
