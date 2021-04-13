import cv2

# (не)профессиональный надор функций для вычисления координат маркера

# старые знакомые декорации
ANY = "ANY"
HAND = "HAND"
READ_MODE = {ANY: 0, HAND: 1}

# найди максимальный контур
def find_max_cont(contours):
    if len(contours) == 0:
        return []
    maxArea = max([cv2.contourArea(c) for c in contours])
    #print(maxArea)
    if maxArea < 3000:
        return []
    for c in contours:
        if cv2.contourArea(c) == maxArea:
            return c

# дай пж координаты пальца, если можешь
def find_finger(img,x_n,y_n,w,h):
    #print(contur)
    rect = img[x_n:x_n+w, y_n:y_n+h]
    x_up = [-1,-1]
    x_right = [-1,-1]
    x_left = [-1,-1]
    # поиск верхней точки контура в прямоугольнике
    for i in range(y_n,y_n + h-2,1):
        for j in range(x_n,x_n + w-2,1):
            if img[i][j] == 255:
                x_up = [i,j]
                break
    #поиск левой и правой выбор максимальной по у. Длина высоты и основания
    for i in range(x_n,min(x_n + w - 2,len(img[0])) ,1):
        for j in range(y_n,min(y_n + h - 2,len(img)),1):
            if img[j][i] == 255:
                x_left = [j,i]
                break

    for i in range(x_n + w-2,x_n,-1):
        for j in range(y_n,y_n + h-2,1):
            if img[j][i] == 255:
                x_right = [j,i]
                break
    #выбираем максимально высокий
    if x_right != [-1, -1] and x_left!= [-1, -1] :
        if x_right[1] > x_left[1]:
            opt = x_right
        else:
            opt = x_left

        hig = abs(opt[1] - x_up[1])
        wig = abs(opt[0] - x_up[0])
        if hig / wig >= 1:# если >=45 верну как есть, меньше, то не дам
            return x_up[0], x_up[1]
    return -1, -1

# дай координаты, если можешь, если нет дай (-1, -1)
def getCoord(img,calibr_mode):
    x = -1
    y = -1
    contours, hierarchy = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    # найти контур с наибольшей площадью и в этом прямоугольнике искать
    max_cont = find_max_cont(contours)
    if len(max_cont) > 0:
        x_n, y_n, w, h = cv2.boundingRect(max_cont)
        if (x_n != 0) and (y_n != 0):
            if calibr_mode == READ_MODE[HAND]:
                x, y = find_finger(img, x_n, y_n, w, h)
            if calibr_mode == READ_MODE[ANY]:
                x = x_n + w // 2
                y = y_n + h // 2
    return x,y

#go to ImgTransform.py

# написанный ниже комментарий не обладает смысловой ценностью для понимания кода (поэтому и написан в конце),
# а так же не является действующей частью (просто мысли недовольного автора) и при прочтении может быть пропущен

# У меня создаётся впечатление, что всё что тут написано это набор систулек и погремушей (Дейкстра).
# "А имеет ли это отношение к процессу решения задачи, а не к самой задаче?"
# Возможно, что это уже совсем не ТО САМОЕ программирование