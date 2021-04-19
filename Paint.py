
import tkinter as tk
import ApClass
import cv2

from tkinter import filedialog as fd

RED = "RED"
ORANGE = "ORANGE"
YELLOW = "YELLOW"
GREEN = "GREEN"
CYAN = "CYAN"
BLUE = "BLUE"
PURPLE = "PURPLE"
WHITE = "WHITE"
ERASER = "ERASER"

#просто всё строки-цвета в списке
COLOR_LIST = [RED, ORANGE, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE]
#цвета для рисования кнопок (удивительно,конечно, но тут цвета rgb -_- )
COLORS = {RED: '#ff0000', ORANGE : '#ff8800', \
          YELLOW : '#ffff00', GREEN:'#00ff00', CYAN:'#00ffff', \
          BLUE : '#0000ff', PURPLE : '#ff00ff', WHITE:'#ffffff', ERASER: '#000000'}
#цвета для рисования кругов
COLORS_RES = {RED: [0,0,255], ORANGE : [0,67,255], \
          YELLOW : [0,255,255], GREEN:[0,255,0], CYAN:[255,255,0], \
          BLUE : [255,0,0], PURPLE : [255,0,255], WHITE:[255,255,255], ERASER: [0,0,0]}


def set_color(color):
    Paint.color = color

def set_size(op):
    if (op == '+') and (Paint.size < 100):
        Paint.size += 2
    if (op == '-') and (Paint.size > 2):
        Paint.size -= 2

def save():
    file_name = fd.asksaveasfilename(defaultextension=".png",
        filetypes=(("PNG files", "*.png"),
                   ("JPG files", "*.jpg"),
                   ("TIF files", "*.tif")))
    if file_name:
        cv2.imwrite(file_name, ApClass.Application.filter_point)

class Paint:

  # Главные герои:
    button = []
    color = WHITE
    size = 5

    @staticmethod
    # вспомогательная функция добавления кнопок
    def easy_add(root, color):
        Paint.button.append(tk.Button(root, command=lambda: set_color(color), width=2, height=1, bg=COLORS[color]))

    @staticmethod
    #создай
    def init(root):
        for c in COLOR_LIST:
            Paint.easy_add(root, c)
        Paint.button.append(tk.Button(root, command=lambda: set_color(ERASER), text='eraser'))
        Paint.button.append(tk.Button(root, command=lambda: set_size('+'), text='+'))
        Paint.button.append(tk.Button(root, command=lambda: set_size('-'), text='-'))
        Paint.button.append(tk.Button(root, command=lambda: save(), text='SAVE', font=16))

    @staticmethod
    #уничтожь
    def destructor():
        for b in Paint.button:
            b.destroy()

    @staticmethod
    #покажи кнопки
    def show_buts():
        for but in Paint.button:
            but.pack( padx=10, pady=10)

    @staticmethod
    #спрячь кнопки
    def hide_buts():
        for but in Paint.button:
            but.pack_forget()

    @staticmethod
    #дай цвет
    def get_color():
        return COLORS_RES[Paint.color]

    @staticmethod
    #дай сайз
    def get_size():
        return Paint.size

#go to Coord.py
