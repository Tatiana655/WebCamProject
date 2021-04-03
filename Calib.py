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
    for i in range(y_n,y_n + h,1):
        for j in range(x_n,x_n + w,1):
            if img[i][j] == 255:
                return  j,i

def find_max_cont(contours):
    maxArea = max([cv2.contourArea(c) for c in contours])
    #print(maxArea)
    if maxArea < 3000:
        return []
    for c in contours:
        if cv2.contourArea(c) == maxArea:
            return c