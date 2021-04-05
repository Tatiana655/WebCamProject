#  В общем работает так: кнопки меняют состояние системы, а внутри заходим в разные if


from PIL import Image, ImageTk
import tkinter as tk

import cv2
import numpy as np
import Calib
import Paint

# объявление констант (в питоне нельзя их в отдельный файл вынести:( )
NOTHING = "NOTHING"
READING = "READING"
MOVING = "MOVING"
DRAWING = "DRAWING"
# доступные режимы
MODE = {NOTHING: 0, READING: 1, MOVING: 2, DRAWING: 3}
# режимы калибровки
ANY = "ANY"
HAND = "HAND"
CALIB = {ANY: 0, HAND:1}
# temp
size = 20  # ребро квадрата-считывателя
# расположение квадрата
X = 200
Y = 100
SHIFT = 100
SEP = 3000

# реакция на резкий переход на чтение при нажатии С на клавиатуре
def event_info(event):
    Application.reading(Application)

class Application:
    # состояние системы
    cur_mode = MODE[NOTHING] #екуущий режим
    cur_calib = CALIB[ANY]
    count_click = 0  # количество кликов для читалки (цвета с квадрата)
    coef_data = [1, 1, 1]  # blur_coef - 0  # open_coef - 1 # close_coef - 2 # всегда нечётные
    min_color = [255, 255, 255] #bgr
    max_color = [0, 0, 0] #bgr
    button = []  # кнопки сисетмы-приложения
    scroll = []  # скроллы калибровки
    label = []  # лэйблы кнопок (удивительно, но они и правда существуют отдельно)
    filter_point = [] # это картинка, которая хранит рисонок
    info_label = []  # поясняющие лэйблы

    def __init__(self, output_path="./"):
        """ Initialize application which uses OpenCV + Tkinter. It displays
            a video stream in a Tkinter window and stores current snapshot on disk """
        self.vs = cv2.VideoCapture(0)  # capture video frames, 0 is your default video camera
        self.output_path = output_path  # store output path
        self.current_image = None  # current image from the camera
        ok, frame = self.vs.read() # reading opencv
        Application.filter_point = np.zeros_like(frame) # start saving picture
        # size of picture
        self.picture_height = len(frame)
        self.picture_weight = len(frame[0])

        self.root = tk.Tk()  # initialize root window
        self.root.geometry("910x600") # size of window
        self.root.title("beta")  # set window title
        # self.destructor function gets fired when the window is closed
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)  # destroy behavior

        self.panel = tk.Label(self.root)  # initialize image panel
        self.panel.pack(padx=10, pady=10, side='left') # show panel

        # size of window display
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # create a buttons and remembering they in list-button, that when pressed the command is called
        btn_start = tk.Button(self.root, text="Click to START", font=100, command=self.reading)
        btn_start.pack(padx=10, pady=10, ipadx=900, ipady=600) # show BIG START button
        Application.button.append(btn_start)
        Application.button.append(tk.Button(self.root, text="CLICK ME!", command=self.counting))  # сччтает клики СLICK_ME
        Application.button.append(tk.Button(self.root, text="NEXT",command=self.moving))  # меняет состояние на рисование|движение. Тот самый пэинт в общем-то
        Application.button.append(tk.Button(self.root, text="RESTART", command=self.reading))  # меняет состояние на чтение-калибровку
        Application.button.append(tk.Button(self.root, text="CHANGE_CALIB", command=self.change_calib))

        # кнопка отмены, о которой забыли сообщить пользоввателю. Потом напиши
        self.root.bind('c' or 'C' or 'с' or 'С', event_info)

        # create a scrolls and labels-scrolls
        Application.scroll.append(tk.Scale(self.root, length=255, orient='horizontal', from_=0, to=255))
        Application.label.append(tk.Label(self.root, text="b_min"))

        Application.scroll.append(tk.Scale(self.root, length=255, orient='horizontal', from_=0, to=255))
        Application.label.append(tk.Label(self.root, text="g_min"))

        Application.scroll.append(tk.Scale(self.root, length=255, orient='horizontal', from_=0, to=255))
        Application.label.append(tk.Label(self.root, text="r_min"))

        Application.scroll.append(tk.Scale(self.root, length=255, orient='horizontal', from_=0, to=255))
        Application.label.append(tk.Label(self.root, text="b_max"))

        Application.scroll.append(tk.Scale(self.root, length=255, orient='horizontal', from_=0, to=255))
        Application.label.append(tk.Label(self.root, text="g_max"))

        Application.scroll.append(tk.Scale(self.root, length=255, orient='horizontal', from_=0, to=255))
        Application.label.append(tk.Label(self.root, text="r_max"))

        Application.scroll.append(tk.Scale(self.root, length=255, orient='horizontal', from_=1, to=50))
        Application.label.append(tk.Label(self.root, text="blur_coef"))

        Application.scroll.append(tk.Scale(self.root, length=255, orient='horizontal', from_=1, to=50))
        Application.label.append(tk.Label(self.root, text="coef_rect_in"))

        Application.scroll.append(tk.Scale(self.root, length=255, orient='horizontal', from_=1, to=50))
        Application.label.append(tk.Label(self.root, text="coef_rect_out"))

        # inform labels
        Application.info_label.append(tk.Label(self.root,
                                               text="Place the marker object\nin the area of the square\n and click the button.\nSRUARE changes position\n(12 button clicks)",
                                               font=20))
        Application.info_label.append(tk.Label(self.root,
                                               text="Put your hand \n(mb in the glove)\nin the area of the squares\n and click the button.\n(1 button click)",
                                               font=20))
        #инит пэинта
        self.paint = Paint.Paint()
        self.paint.init(self.root)
        # start a self.video_loop that constantly pools the video sensor
        # for the most recently read frame
        self.video_loop()

    # тут работа с видеопотоком
    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, frame = self.vs.read()  # read frame from video stream

        if ok:  # frame captured without any errors
            frame = cv2.flip(frame, 1)
            # стартовые координаты квадрата
            x_new = X
            y_new = Y
            # рисование квадратов-читальщиков (для пользователя, но чтение в reading'e)
            if Application.cur_mode == MODE[READING]:  # reading
                if Application.cur_calib == CALIB[ANY]:
                    if 3 <= Application.count_click < 6:
                        x_new = len(frame[0]) - X
                    if 6 <= Application.count_click < 9:
                        x_new = X
                        y_new = len(frame) - Y
                    if Application.count_click >= 9:
                        x_new = len(frame[0]) - X
                        y_new = len(frame) - Y
                    frame = cv2.rectangle(frame, (x_new-1,y_new-1), (x_new + size + 1, y_new + size + 1), (255, 0, 0), 1)

                if Application.cur_calib == CALIB[HAND]:
                    if Application.count_click < 12:
                        x = self.picture_weight // 2 - size // 2 - size * 2
                        y = self.picture_height // 2 - size // 2 - size * 2
                        for i in range(0,6,2):
                            for j in range(0,9,3):
                                frame = cv2.rectangle(frame,(x-1 + i * size ,y-1 + j * size), (x+1 + (i+1) * size ,y+1 + (j+1) * size), (255,0,0,),1)

                # доп настройка # наложение фильтра
                if Application.count_click == 12:
                    Application.min_color = [Application.scroll[0].get(), Application.scroll[1].get(),
                                             Application.scroll[2].get()]
                    Application.max_color = [Application.scroll[3].get(), Application.scroll[4].get(),
                                             Application.scroll[5].get()]
                    Application.coef_data = [Application.scroll[6].get(), Application.scroll[7].get(),
                                             Application.scroll[8].get()]
                    # приметение фильтров
                    filter = cv2.inRange(frame, np.array(Application.min_color), np.array(Application.max_color))
                    st1 = cv2.getStructuringElement(cv2.MORPH_RECT,
                                                    (Application.coef_data[1], Application.coef_data[1]),
                                                    (-1, -1))
                    st2 = cv2.getStructuringElement(cv2.MORPH_RECT,
                                                    (Application.coef_data[2], Application.coef_data[2]),
                                                    (-1, -1))
                    filter = cv2.morphologyEx(filter, cv2.MORPH_CLOSE, st1)
                    filter = cv2.morphologyEx(filter, cv2.MORPH_OPEN, st2)
                    filter = cv2.medianBlur(filter, 2 * Application.coef_data[0] + 1)
                    contours, hierarchy = cv2.findContours(filter.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                    #найти контур с наибольшей площадью и в этом прямоугольнике искать
                    if (len(contours)> 0):
                        max_cont = Calib.find_max_cont(contours)
                        if len(max_cont)>0:
                            cnt = max_cont[0]
                            cv2.drawContours(filter, [max_cont], 0, (100, 100, 100), 3)
                            x_n, y_n, w, h = cv2.boundingRect(max_cont)
                            if (x_n != 0) and (y_n != 0):
                                x, y = Calib.find_finger( filter, x_n, y_n, w, h)
                                if (h/w>1.4):
                                    filter = cv2.circle(filter, (x, y), 5, 100, -1)
                    frame = filter

            # получение координат и "отрисовка" линии # тут надо связываться с Пэинтом
            if Application.cur_mode == MODE[MOVING]:
                # применение фильтров
                filter = cv2.inRange(frame, np.array(Application.min_color), np.array(Application.max_color))
                st1 = cv2.getStructuringElement(cv2.MORPH_RECT, (Application.coef_data[1], Application.coef_data[1]),
                                                (-1, -1))
                st2 = cv2.getStructuringElement(cv2.MORPH_RECT, (Application.coef_data[2], Application.coef_data[2]),
                                                (-1, -1))
                filter = cv2.morphologyEx(filter, cv2.MORPH_CLOSE, st1)
                filter = cv2.morphologyEx(filter, cv2.MORPH_OPEN, st2)
                filter = cv2.medianBlur(filter, 2 * Application.coef_data[0] + 1)
                # получение координат
                moments = cv2.moments(filter, 1)
                dM01 = moments['m01']
                dM10 = moments['m10']
                dArea = moments['m00']
                contours, hierarchy = cv2.findContours(filter.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                if dArea > 5:  # рисование или другой экшн // тут надо связываться с пэинтом
                    x = -1#int(dM10 / dArea)
                    y = -1#int(dM01 / dArea)
                    # найти контур с наибольшей площадью и в этом прямоугольнике искать
                    max_cont = Calib.find_max_cont(contours)
                    if len(max_cont)>0:
                        x_n, y_n, w, h = cv2.boundingRect(max_cont)
                        if (x_n != 0) and (y_n != 0):
                            if Application.cur_calib == CALIB[HAND]:
                                x, y = Calib.find_finger(filter, x_n, y_n, w, h)
                            if Application.cur_calib == CALIB[ANY]:
                                x = x_n + w//2
                                y = y_n + h//2
                            #filter = cv2.circle(filter, (x, y), 5, 100, -1)
                    if (x !=-1) and (y !=-1) :
                        Application.filter_point = cv2.circle(Application.filter_point, (x, y),self.paint.get_size(), self.paint.get_color(), -1)

                frame = cv2.add(frame, Application.filter_point)
                    # движение курсора
                    # x_screen = x * self.screen_width / len(frame[0])
                    # y_screen = y * self.screen_height / len(frame)
                    # pyautogui.moveTo(x_screen, y_screen) # Жутко медленно
                    # if Application.flag:
                    #   pyautogui.mouseDown()

            if Application.cur_mode == MODE[READING] and Application.count_click == 12:
                # в режиме чтения покаывает, что видит фильтр
                cv2image = cv2.cvtColor(cv2.bitwise_and(frame, frame, mask=filter), cv2.COLOR_BGR2RGBA)
            else:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)  # convert colors from BGR to RGBA

            # перевод координат ЦВЕТА и рисование в окно
            self.current_image = Image.fromarray(cv2image)  # convert image for PIL
            imgtk = ImageTk.PhotoImage(image=self.current_image)  # convert image for tkinter
            self.panel.imgtk = imgtk  # anchor imgtk so it does not be deleted by garbage-collector
            if Application.cur_mode != MODE[NOTHING]:
                self.panel.config(image=imgtk)  # show the image

        self.root.after(15, self.video_loop)  # call the same function after 30 milliseconds

    #тут инит кнопок пэинта
    def moving(self):
        Application.cur_mode = MODE[MOVING]
        Application.button[1].pack_forget()
        Application.button[2].pack_forget()
        Application.button[4].pack_forget()
        Application.info_label[0].pack_forget()
        Application.info_label[1].pack_forget()
        Application.button[3].pack( padx=10, pady=10)

        for s in Application.scroll:
            s.pack_forget()
        for lab in Application.label:
            lab.pack_forget()
        self.paint.show_buts()

    def counting(self):
        Application.count_click += 1
        ok, frame = self.vs.read()
        frame = cv2.flip(frame, 1)
        # цветовая читалка
        if Application.cur_calib == CALIB[ANY]:
            y_new = Y
            x_new = X
            # тут считывание цветов
            if 3 <= Application.count_click < 6:
                x_new = self.picture_weight - X  # ВНИМАНИЕ: болванка
            if 6 <= Application.count_click < 9:
                x_new = X
                y_new = self.picture_height - Y
            if Application.count_click >= 9:
                x_new = self.picture_weight - X
                y_new = self.picture_height - Y

            min_color1, max_color1 = Calib.find_all_colors(frame, x_new + 1, y_new + 1)  # ???
            Application.min_color = Calib.find_min_coomp(Application.min_color, min_color1)
            Application.max_color = Calib.find_max_coomp(Application.max_color, max_color1)

        if Application.cur_calib == CALIB[HAND]:
            x = self.picture_weight//2 - size//2 - size * 2
            y = self.picture_height//2 - size//2 - size * 2

            for i in range(0,6,2):
                for j in range(0,9,3):
                    min_color1, max_color1 = Calib.find_all_colors(frame, x + i * size, y + j * size)  # ???
                    Application.min_color = Calib.find_min_coomp(Application.min_color, min_color1)
                    Application.max_color = Calib.find_max_coomp(Application.max_color, max_color1)
            Application.count_click = 12
        # доп настройка
        if Application.count_click == 12:
            for i in range(3):
                Application.scroll[i].set(Application.min_color[i])
                Application.scroll[i + 3].set(Application.max_color[i])
                Application.scroll[i + 6].set(Application.coef_data[i])
            for i in range(len(Application.scroll)):
                Application.label[i].pack()
                Application.scroll[i].pack()
            Application.button[2].pack(side='left', padx=1, pady=1)
            Application.button[1].pack_forget()
            Application.info_label[0].pack_forget()
            Application.info_label[1].pack_forget()
            Application.button[4].pack_forget()


    def reading(self):
        Application.cur_mode = MODE[READING]
        Application.count_click = 0
        Application.button[1].pack(side='top', padx=10, pady=10)
        Application.button[4].pack(side='top', padx=10, pady=10)

        if Application.cur_calib == CALIB[ANY]:
            Application.info_label[1].pack_forget()
            Application.info_label[0].pack(side = "left")

        if Application.cur_calib == CALIB[HAND]:
            Application.info_label[0].pack_forget()
            Application.info_label[1].pack(side = "left")


        Application.button[0].pack_forget()
        Application.button[2].pack_forget()
        Application.button[3].pack_forget()

        self.paint.hide_buts()

        # Application.button[4].pack_forget()
        for s in Application.scroll:
            s.pack_forget()
        for lab in Application.label:
            lab.pack_forget()


    def change_calib(self):
        if Application.cur_calib == CALIB[ANY]:
            Application.cur_calib = CALIB[HAND]
        else:
            Application.cur_calib = CALIB[ANY]

        if Application.cur_calib == CALIB[ANY]:
            Application.info_label[1].pack_forget()
            Application.info_label[0].pack(side = "left")

        if Application.cur_calib == CALIB[HAND]:
            Application.info_label[0].pack_forget()
            Application.info_label[1].pack(side = "left")




    def destructor(self):
        """ Destroy the root object and release all resources """
        # освободить ресурсы
        for s in Application.scroll:
            s.destroy()
        for b in Application.button:
            b.destroy()
        for lab in Application.label:
            lab.destroy()
        self.paint.destructor()

        print("[INFO] closing...")
        self.root.destroy()
        self.vs.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application
