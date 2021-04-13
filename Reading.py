# уже совсем потрёпанные декорации (всё что от них осталось)
# Я тут подумала, можно уже и класс констант создать, чтобы такого не было
size = 20  # ребро квадрата-считывателя


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
def find_all_colors(img, x, y):  # картинка и верхний левый угол квадрата, в котором искать цвета
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

# the end of the code
# Заключение.
# Конец. Начало.
# Опять кругом круг пойдёт
# Спать пора уже D: