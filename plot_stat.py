import json_keep as jk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import tkinter as tk
from tkinter import ttk



class WorkingBar:

    def __init__(self, bar, annot):
        self.bar = bar
        self.annot = annot

    def connect(self):
        self.motion = self.bar.figure.canvas.mpl_connect('motion_notify_event', self.hover) # связывает событие прохода курсора над фигурой с определенной функцией класса

    def update(self):
        x, y = (self.bar.get_x(), self.bar.get_height()) # создает определенные значения для аннотации
        self.annot.xy=(x, y) # передает аннотации новые значения xy, которые она принимает, если отсутствует xytext
        text = f'{self.bar.get_height()}' # назначение текста для аннотации
        self.annot.set_text(text) # устанавливает переданный текст
        self.annot.get_bbox_patch().set_alpha(0.4) # устанавливает прозрачность рамки
        self.annot.set_visible(True) # делает аннотацию видимой
        self.bar.set_facecolor('red')

    def hover(self, event):
        vis = self.annot.get_visible() # проверяет видимость аннотации
        if event.inaxes != self.bar.axes: return # если курсор находится на прямоугольнике - работает дальше, нет - нет
        cont, _ = self.bar.contains(event) # проверяет то же самое, возвращает булевое значение
        if cont:
            self.update() # запускает update, который получает необходимые значения и выводит аннотацию
            self.bar.figure.canvas.draw_idle() # что draw, что draw_idle - просто рисуют необходимые значения, в данном случае - с видимой аннотацией
        else:
            if vis:
                self.annot.set_visible(False)
                self.bar.set_facecolor('c')
                self.bar.figure.canvas.draw_idle() # как можно заметить, тут аннотация не видна

class BarPlotStat(tk.Frame):
    pass

class PiePlotStat(tk.Frame):
    pass
   
class LaunchesTable(tk.Frame):
    pass

# root = tk.Tk()

# app = BarPlotStat(root)
# app.pack()
# root.mainloop()