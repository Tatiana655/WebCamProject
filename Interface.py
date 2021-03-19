
#  обем техника таккая кнопки меняют состояние системы, а внутли мы как что-то делаем так и делаем
# мб есть сполоб написать это правильно, но мн е он не извествен (В любом случае мы код пишем не для того, чтобы он работал)
# пока без обработки ошибок
from PIL import Image, ImageTk
import tkinter as tk
import argparse
import datetime
import cv2
import os
import numpy as np

MODE = "NOTHING","READING", "MOVING", "DRAWING"# можно что-то вроде enum

#temp
size = 20  # ребро квадрата-считывателя
# асположение квадрата
X = 200
Y = 100

SHIFT = 100 #ВНИМАНИЕ: болванка
# режим работы калибровка/рисование (мб и больше будет)
mode = False
# погрешность
eps = 0

##потом убрать в отдкльный файл // типа модуль калибровки
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
def find_all_colors(img, X, Y):  # картинка и верхрий левый угол квадрата, в котором искать цвета
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

##То что выше в отдельный файл

class Application:
    Mode = MODE[0]
    #для чтения
    count_click = 0 #количество кликов на читалку
    data = [7,15,21] #blur_coef всегда нечётный #open_coef #close_coef
    min_color = [255, 255, 255]
    max_color = [0, 0, 0]
    button = []
    Scroll = []
    label = []

    def __init__(self, output_path = "./"):
        """ Initialize application which uses OpenCV + Tkinter. It displays
            a video stream in a Tkinter window and stores current snapshot on disk """
        self.vs = cv2.VideoCapture(0) # capture video frames, 0 is your default video camera
        self.output_path = output_path  # store output path
        self.current_image = None  # current image from the camera

        self.root = tk.Tk()  # initialize root window
        self.root.title("Non-contact stylus, alpha")  # set window title
        # self.destructor function gets fired when the window is closed
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)

        self.panel = tk.Label(self.root)  # initialize image panel
        self.panel.pack(padx=10, pady=10,side='left')

        # create a button, that when pressed, will take the current frame and save it to file
        btn_start = tk.Button(self.root, text="START", command=self.reading) # тут кнопки, бегунки? мб через глобальные переменные
        btn_start.pack( side='left', padx=10, pady=10)
        Application.button.append(btn_start)
        Application.button.append(tk.Button(self.root, text="CLICK ME!", command=self.counter))
        Application.button.append(tk.Button(self.root, text="NEXT", command=self.point)) # тут кнопки, бегунки? мб через глобальные переменные
        Application.button.append(tk.Button(self.root, text="RESTART", command=self.reading))

        #create a scrolls and labels
        Application.Scroll.append( tk.Scale(self.root, length=255, orient='horizontal', from_=0, to=255))
        Application.label.append( tk.Label(self.root, text="b_min"))

        Application.Scroll.append(tk.Scale(self.root, length=255, orient='horizontal', from_=0, to=255))
        Application.label.append( tk.Label(self.root, text="g_min"))

        Application.Scroll.append(tk.Scale(self.root, length=255, orient='horizontal', from_=0, to=255))
        Application.label.append(tk.Label(self.root, text="r_min"))

        Application.Scroll.append( tk.Scale(self.root, length=255, orient='horizontal', from_=0, to=255))
        Application.label.append(tk.Label(self.root, text="b_max"))

        Application.Scroll.append(tk.Scale(self.root, length=255, orient='horizontal', from_=0, to=255))
        Application.label.append( tk.Label(self.root, text="g_max"))

        Application.Scroll.append(tk.Scale(self.root, length=255, orient='horizontal', from_=0, to=255))
        Application.label.append( tk.Label(self.root, text="r_max"))


        Application.Scroll.append(tk.Scale(self.root, length=255, orient='horizontal', from_=1, to=50))
        Application.label.append( tk.Label(self.root, text="blur_coef"))

        Application.Scroll.append(tk.Scale(self.root, length=255, orient='horizontal', from_=1, to=50))
        Application.label.append( tk.Label(self.root, text="coef_rect_in"))

        Application.Scroll.append(tk.Scale(self.root, length=255, orient='horizontal', from_=1, to=50))
        Application.label.append( tk.Label(self.root, text="coef_rect_out"))

        # start a self.video_loop that constantly pools the video sensor
        # for the most recently read frame
        self.video_loop()

# тут работа с видео//рисование
    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            frame = cv2.flip(frame, 1)
            #frame = cv2.rectangle(frame, (X,Y), (X+20,Y+20), (255,0,0,), 1)
            x_new = X
            y_new = Y
            #рисование квадратов
            if Application.Mode == MODE[1]:#reading
                if 3 <= Application.count_click < 6:
                    x_new = X + SHIFT                                         #ВНИМАНИЕ: болванка
                if 6 <= Application.count_click < 9:
                    x_new = X
                    y_new = Y + SHIFT
                if Application.count_click >= 9:
                    x_new = X + SHIFT
                    y_new = Y + SHIFT
                frame = cv2.rectangle(frame, (x_new-1, y_new-1), (x_new+20+1, y_new+20+1), (255, 0, 0,), 1)
            #доп настройка
                if Application.count_click == 12:
                    Application.min_color = [Application.Scroll[0].get(), Application.Scroll[1].get(), Application.Scroll[2].get()]
                    Application.max_color = [Application.Scroll[3].get(), Application.Scroll[4].get(), Application.Scroll[5].get()]
                    Application.data = [Application.Scroll[6].get(), Application.Scroll[7].get(), Application.Scroll[8].get()]
                    filter = cv2.inRange(frame, np.array(Application.min_color), np.array(Application.max_color))
                    st1 = cv2.getStructuringElement(cv2.MORPH_RECT, (Application.data[1], Application.data[1]), (-1, -1))
                    st2 = cv2.getStructuringElement(cv2.MORPH_RECT, (Application.data[2], Application.data[2]), (-1, -1))
                    filter = cv2.morphologyEx(filter, cv2.MORPH_CLOSE, st1)
                    filter = cv2.morphologyEx(filter, cv2.MORPH_OPEN, st2)
                    filter = cv2.medianBlur(filter, 2 * Application.data[0] + 1)
                    frame = filter

            #получение координат
            if Application.Mode == MODE[2] :

                filter = cv2.inRange(frame, np.array(Application.min_color), np.array(Application.max_color))
                st1 = cv2.getStructuringElement(cv2.MORPH_RECT, (Application.data[1], Application.data[1]), (-1, -1))
                st2 = cv2.getStructuringElement(cv2.MORPH_RECT, (Application.data[2], Application.data[2]), (-1, -1))
                filter = cv2.morphologyEx(filter, cv2.MORPH_CLOSE, st1)
                filter = cv2.morphologyEx(filter, cv2.MORPH_OPEN, st2)
                filter = cv2.medianBlur(filter, 2 * Application.data[0] + 1)

                moments = cv2.moments(filter, 1)
                dM01 = moments['m01']
                dM10 = moments['m10']
                dArea = moments['m00']
                if dArea > 5:  # тут надо линии нарисовать
                    x = int(dM10 / dArea)
                    y = int(dM01 / dArea)
                    frame = cv2.circle(frame, (x, y), 5, (255, 0, 255), -1)


            if (Application.Mode == MODE[1] and Application.count_click == 12) :
                cv2image = cv2.cvtColor(cv2.bitwise_and(frame, frame, mask=filter), cv2.COLOR_BGR2RGBA)
                #cv2image = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGBA)
            else:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA
            self.current_image = Image.fromarray(cv2image)  # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            self.panel.config(image=imgtk)  # show the image

        self.root.after(15, self.video_loop)  # call the same function after 30 milliseconds

    def point(self):
        Application.Mode = MODE[2]
        Application.button[1].pack_forget()
        Application.button[2].pack_forget()
        Application.button[3].pack(side='left', padx=10, pady=10)
        for s in Application.Scroll:
            s.pack_forget()
        for l in Application.label:
            l.pack_forget()

    def counter(self):
        Application.count_click += 1
        y_new = Y
        x_new = X
        #тут ещё считывание цветов надо запихнуть
        if 3 <= Application.count_click < 6:
            x_new = X + SHIFT  # ВНИМАНИЕ: болванка
        if 6 <= Application.count_click < 9:
            x_new = X
            y_new = Y + SHIFT
        if Application.count_click >= 9:
            x_new = X + SHIFT
            y_new = Y + SHIFT

        ok, frame = self.vs.read()
        frame = cv2.flip(frame, 1)

        min_color1, max_color1 = find_all_colors(frame, x_new + 1, y_new + 1)  # ???
        Application.min_color = find_min_coomp(Application.min_color, min_color1)
        Application.max_color = find_max_coomp(Application.max_color, max_color1)
        #доп настройка
        if Application.count_click == 12:
            for i in range(3):
                Application.Scroll[i].set(Application.min_color[i])
                Application.Scroll[i+3].set(Application.max_color[i])
                Application.Scroll[i+6].set(Application.data[i])
            for i in range(len(Application.Scroll)):
                Application.label[i].pack()
                Application.Scroll[i].pack()
            Application.button[2].pack(side='left', padx=10, pady=10)
            Application.button[1].pack_forget()


    def reading(self):
        Application.Mode = MODE[1]
        Application.count_click = 0
        Application.button[0].pack_forget()
        Application.button[3].pack_forget()
        Application.button[1].pack(side='left', padx=10, pady=10)

    def destructor(self):
        """ Destroy the root object and release all resources """
        #освободить ресурсы
        for s in Application.Scroll:
            s.destroy()
        for b in Application.button:
            b.destroy()
        for l in Application.label:
            l.destroy()

        print("[INFO] closing...")
        self.root.destroy()
        self.vs.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", default="./",
    help="path to output directory to store snapshots (default: current folder")
args = vars(ap.parse_args())

# start the app
print("[INFO] starting...")
pba = Application(args["output"])
pba.root.mainloop()