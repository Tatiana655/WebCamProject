import cv2
import numpy as np

# обработка изображения с маркером, современная обработка изображений
# ик камера
# обмен симвоолами, первый спринт + документация алгоритмов. как выбирать алг, фильтры
# linka, ,kfujhjlyfz wtkm ? или развлекалово
# user requirement

size = 20  # ребро квадрата-считывателя
# асположение квадрата
X = 200
Y = 100
# режим работы калибровка/рисование (мб и больше будет)
mode = False
# погрешность
eps = 0


# вычисляет min/max комполенты двых цветов-векторов
def find_min_coomp(vec1, vec2):
    for i in range(len(vec1)):
        vec1[i] = min(vec1[i], vec2[i])
    return vec1


def find_max_coomp(vec1, vec2):
    for i in range(len(vec1)):
        vec1[i] = max(vec1[i], vec2[i])
    return vec1


# ищет два вектора цвета на маркере
def find_all_colors(img):
    min_color = [255, 255, 255]
    max_color = [0, 0, 0]
    # мне кажется, тут можно написать и короче
    for i in range(Y, Y + size):
        for j in range(X, X + size):
            for k in range(3):
                min_color[k] = min(img[i][j][k], min_color[k])
                if min_color[k] >= eps:
                    min_color[k] -= eps
                max_color[k] = max(img[i][j][k], min_color[k])
                if max_color[k] <= 255 - eps:
                    max_color[k] += eps
    return min_color, max_color


def Scrolls(cap, min_color, max_color):
    cv2.namedWindow("result")  # создаем главное окно
    cv2.namedWindow("settings")  # создаем окно настроек

    # создаем 6 бегунков для настройки начального и конечного цвета фильтра
    cv2.createTrackbar('r_min', 'settings', min_color[0], 255, lambda x:x)
    cv2.createTrackbar('g_min', 'settings', min_color[1], 255, lambda x:x)
    cv2.createTrackbar('b_min', 'settings', min_color[2], 255, lambda x:x)
    cv2.createTrackbar('r_max', 'settings', max_color[0], 255, lambda x:x)
    cv2.createTrackbar('g_max', 'settings', max_color[1], 255, lambda x:x)
    cv2.createTrackbar('b_max', 'settings', max_color[2], 255, lambda x:x)

    while True:
        flag, imgtmp = cap.read()
        imgtmp = cv2.flip(imgtmp, 1)
        trash = np.zeros_like(imgtmp)
        # считываем значения бегунков
        h1 = cv2.getTrackbarPos('r_min', 'settings')
        s1 = cv2.getTrackbarPos('g_min', 'settings')
        v1 = cv2.getTrackbarPos('b_min', 'settings')
        h2 = cv2.getTrackbarPos('r_max', 'settings')
        s2 = cv2.getTrackbarPos('g_max', 'settings')
        v2 = cv2.getTrackbarPos('b_max', 'settings')

        # формируем начальный и конечный цвет фильтра
        h_min = np.array((h1, s1, v1))
        h_max = np.array((h2, s2, v2))

        # накладываем фильтр на кадр
        filter = cv2.inRange(imgtmp, h_min, h_max)
        filter = cv2.medianBlur(filter, 15)
        trash = cv2.add(trash, cv2.bitwise_and(imgtmp, imgtmp, mask=filter))

        cv2.imshow('result', np.hstack([imgtmp, trash]))

        ch = cv2.waitKey(5)
        if ch == 27:# wait for ESC key to exit|| хорошо бы "OK" найти какой-нибудь
            cv2.destroyWindow("result")
            cv2.destroyWindow("settings")
            return [h1, s1, v1], [h2, s2, v2]



# это хорошо бы в мейн
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# x_vec = []
# y_vec = []
min_color = [255, 255, 255]
max_color = [0, 0, 0]
count_col = 0

ret, img = cap.read()
Marker = np.zeros_like(img)
Point = np.zeros_like(img)

mask = np.zeros_like(img)
mask = cv2.flip(mask, 1)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
fgbg = cv2.createBackgroundSubtractorKNN(50, 200.0, False)

while True:
    ret, img = cap.read()
    img = cv2.flip(img, 1)

    start_point = (X - 1, Y - 1)
    end_point = (X + size + 1, Y + size + 1)
    color = (255, 0, 0)
    thickness = 1
    Marker = np.zeros_like(img)
    # режим калибровки
    if not mode:
        img = cv2.rectangle(img, start_point, end_point, color, thickness)
        cv2.imshow("WM", img)

    if cv2.waitKey(10) == ord('a'):
        # найти максимальную разность цветов//вернуть 2 RGB//запихнуть в одну функцию-файл
        min_color1, max_color1 = find_all_colors(img)
        min_color = find_min_coomp(min_color, min_color1)
        max_color = find_max_coomp(max_color, max_color1)
        count_col += 1  # количество щёлчков
        if count_col == 10:
            mode = True
            # бегунки после калибровки для проверки тцут
            min_color, max_color = Scrolls(cap, min_color, max_color)

    # режим рисования
    if mode:
        # поиск в диапазоне цветов, тут можно сократить код

        m1 = cv2.inRange(img, np.array(min_color), np.array(max_color))
        m1 = cv2.medianBlur(m1, 15)

        Marker = cv2.add(Marker, cv2.bitwise_and(img, img, mask=m1))

        moments = cv2.moments(m1, 1)
        dM01 = moments['m01']
        dM10 = moments['m10']
        dArea = moments['m00']

        if dArea > 5:
            x = int(dM10 / dArea)
            y = int(dM01 / dArea)
            mask = cv2.circle(mask, (x, y), 5, (50, 100, 255), -1)
            Point = cv2.add(Point, mask)

        fgmask = fgbg.apply(Marker)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)

        cv2.imshow("WM", np.hstack([img, Marker, Point]))

    if cv2.waitKey(10) == 27:  # Клавиша Esc
        break
    if not cv2.getWindowProperty('WM', 0) >= 0:  # крестик
        break

cap.release()
cv2.destroyAllWindows()
