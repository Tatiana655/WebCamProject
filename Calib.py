import cv2

# temp
size = 20  # ребро квадрата-считывателя
# асположение квадрата

def find_min_coomp(vec1, vec2):
    for i in range(len(vec1)):
        vec1[i] = min(vec1[i], vec2[i])
    return vec1

# вычисляет min/max комполенты двух цветов-векторов

def find_max_coomp(vec1, vec2):
    for i in range(len(vec1)):
        vec1[i] = max(vec1[i], vec2[i])
    return vec1


# ищет два вектора цвета на маркере
def find_all_colors(img, x, y):  # картинка и верхрий левый угол квадрата, в котором искать цвета
    min_color = [255, 255, 255]
    max_color = [0, 0, 0]
    # мне кажется, тут можно написать и короче
    for i in range(y, y + size):
        for j in range(x, x + size):
            for k in range(3):
                min_color[k] = min(img[i][j][k], min_color[k])
                if min_color[k] >= 0:
                    min_color[k] -= 0
                max_color[k] = max(img[i][j][k], min_color[k])
                if max_color[k] <= 255 - 0:
                    max_color[k] += 0
    return min_color, max_color

def find_finger(img,x_n,y_n,w,h):
    #print(contur)
    rect = img[x_n:x_n+w, y_n:y_n+h]

    x_up = [-1,-1]
    x_right = [-1,-1]
    x_left = [-1,-1]
    # поиск верхней точки контура в прямоугольнике
    for i in range(y_n,y_n + h,1):
        for j in range(x_n,x_n + w,1):
            if img[j][i] == 255:
                x_up = [j,i]
                break
    #поиск левой и правой выбор максимальной по у. Длина высоны и основания
    for i in range(x_n,x_n + w,1):
        for j in range(y_n,y_n + h,1):
            if img[i][j] == 255:
                x_left = [i,j]
                break

    for i in range(x_n + w,x_n,-1):
        for j in range(y_n,y_n + h,1):
            if img[i][j] == 255:
                x_right = [i,j]
                break
    if x_right != [-1, -1] and x_left!= [-1, -1] :
        if x_right[1] > x_left[1]:
            opt = x_right
        else:
            opt = x_left

        hig = abs(opt[1] - x_up[1])
        wig = abs(opt[0] - x_up[0])
        if hig / wig > 1:
            return x_up[0], x_up[1]
    return -1, -1


def find_max_cont(contours):
    maxArea = max([cv2.contourArea(c) for c in contours])
    #print(maxArea)
    if maxArea < 3000:
        return []
    for c in contours:
        if cv2.contourArea(c) == maxArea:
            return c