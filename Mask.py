import cv2
import numpy as np
size = 20
X = 200
Y = 100
mode = False
delt = 0

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
                if min_color[k]>=delt:
                    min_color[k] -= delt
                max_color[k] = max(img[i][j][k], min_color[k])
                if max_color[k] <=255-delt:
                    max_color[k]+=delt;
    return min_color, max_color


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
x_vec = []
y_vec = []
min_color = [255, 255, 255]
max_color = [0, 0, 0]
f = 0
ret, img = cap.read()
Marker = np.zeros_like(img)
Point = np.zeros_like(img)

mask = np.zeros_like(img)
mask = cv2.flip(mask, 1)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(10,10))
fgbg = cv2.createBackgroundSubtractorKNN(50, 200.0, False)

while True:
    ret, img = cap.read()
    img = cv2.flip(img, 1)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    start_point = (X-1, Y-1)
    end_point = (X + size+1, Y + size+1)
    color = (255, 0, 0)
    thickness = 1
    Marker = np.zeros_like(img)
    if mode == False:
        img = cv2.rectangle(img, start_point, end_point, color, thickness)
        cv2.imshow("WM", img)

    # here something like: "place the item(?) in the circle and qlick "q""//To define a marker//что-то типа калибровки, но как это в КЗ называется - пас
    if cv2.waitKey(10) == ord('a'):#на самом деле я просто других укв не знаю//посмотреть другие буквы//возможно стоит калибровать на нескольких кадрах, там даже так погрешность большая что-то
        #тут надо найти максимальную разность цветов//вернуть 2 RGB
        min_color1, max_color1 = find_all_colors(img)
        min_color = find_min_coomp(min_color,min_color1)
        max_color = find_max_coomp(max_color,max_color1)
        f+=1
        if f == 4:
            mode = True
    if (mode):
        #поиск в диапазоне цветов
        L1 = np.array(min_color)
        U1 = np.array(max_color)

        hsv_min = np.array(min_color, np.uint8)
        hsv_max = np.array(max_color, np.uint8)

        thresh = cv2.inRange(hsv, hsv_min, hsv_max)
        m1 = cv2.inRange(img, L1, U1)
        #user reqaierment
        Marker = cv2.add(Marker, cv2.bitwise_and(img, img, mask=m1))
        kernel1 = np.ones((2, 2), np.float32) / 25
        Marker = cv2.medianBlur(Marker, 15)
        #hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        #gray_image = cv2.cvtColor(m1, cv2.COLOR_BGR2GRAY)
        moments = cv2.moments(m1, 1)
        dM01 = moments['m01']
        dM10 = moments['m10']
        dArea = moments['m00']

        if dArea > 5:
            x = int(dM10 / dArea)
            y = int(dM01 / dArea)
            mask = cv2.circle(mask, (x, y), 5, (50, 100, 255), -1)
            Point = cv2.add(Point, mask)
        #обработка изображения с маркером, современная обработка изображений
        #ик камера
        #обмен симвоолами, первый спринт + документация алгоритмов. как выбирать алг, фильтры
        #linka, ,kfujhjlyfz wtkm ? или развлекалово
        fgmask = fgbg.apply(Marker)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

        cv2.imshow("WM", np.hstack([img, Marker, Point]))
    #cv2.imshow("Cam", img)
    if cv2.waitKey(10) == 27: # Клавиша Esc
        break
    if not cv2.getWindowProperty('WM', 0) >= 0: #крестик
        break

cap.release()
cv2.destroyAllWindows()
