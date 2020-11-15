import json_keep as jk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import tkinter as tk
from tkinter import ttk

class WorkingBar:
    """Class for anomation of the bars in plot"""
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
    
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        btn_frame = tk.Frame(self)
        plot_frame = tk.Frame(self)
        btn_frame.pack()
        plot_frame.pack()

        btn1 = ttk.Button(btn_frame, text='Pie Plot', command = lambda: controller.switch_page(PiePlotStat))
        btn2 = ttk.Button(btn_frame, text='Table', command = lambda: controller.switch_page(LaunchesTable))
        btn1.pack(side='left', padx=20)
        btn2.pack(side='left')

        self.combobox = ttk.Combobox(plot_frame,
                                     values = ['For a day',
                                                'For a week',
                                                'For a month',
                                                'For a year']
                                    )
        self.combobox.bind('<<ComboboxSelected>>', self.change_data)
        self.combobox.current(0)
        self.combobox.pack(side='top', pady=10)

        self.fig = Figure(figsize=(5,4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.bb = [] # bars-box
        
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.draw()

        self.create_graph(self.get_data('day_hours'))
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def get_data(self, ds:str):
        data = jk.get_bar_data(ds)
        x, y = list(data.keys()), list(data.values())
        return x, y

    def create_graph(self, data:tuple):
        x, y = data
        bars = self.ax.bar(x, y, color='c')
        if len(x) > 12:
            if len(x) == 31:
                arr = np.arange(0, 32, 7)
                self.ax.set_xticks(arr)
            elif len(x) == 30:
                arr = np.arange(1, 32, 6)
                self.ax.set_xticks(arr)
            elif len(x) == 24:
                arr = np.concatenate((np.array([0]), np.arange(0, 19, 6), np.array([23])))
                self.ax.set_xticks(arr)
        for bar in bars:
            annot = self.ax.annotate('', xy=(-1,-10), xytext=(-20, 23), textcoords='offset points',
                                    bbox=dict(boxstyle='round', fc='w'),
                                    arrowprops=dict(arrowstyle='->'))
            new_bar = WorkingBar(bar, annot)
            new_bar.connect()
            self.bb.append(new_bar)

    def change_data(self, event):
        ds = self.combobox.get() #datastring
        dct = {'For a day':'day_hours',
               'For a week':'week_days',
               'For a month':'month_days',
               'For a year':'year_months'}
        self.ax.clear()
        self.create_graph(self.get_data(dct[ds]))
        self.canvas.draw()

class PiePlotStat(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
   
        btn_frame = tk.Frame(self)
        plot_frame = tk.Frame(self)
        btn_frame.pack()
        plot_frame.pack()

        btn1 = ttk.Button(btn_frame, text='Bar Plot', command = lambda: controller.switch_page(BarPlotStat))
        btn2 = ttk.Button(btn_frame, text='Table', command = lambda: controller.switch_page(LaunchesTable))
        btn1.pack(side='left', padx=10)
        btn2.pack(side='left')

        hiden_lbl = tk.Label(plot_frame, text='')
        hiden_lbl.pack(side='top', pady=10)

        self.fig = Figure(figsize=(5,4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.draw()

        labels, perc = self.get_data()
        self.ax.pie(perc, labels=labels, autopct='%1.1f%%', shadow=True)

        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def get_data(self):
        data = jk.get_pie_data()
        lab, perc = [], []
        for i in data:
            if data[i]:
                lab.append(i)
                perc.append((data[i]/sum(list(data.values())) * 100))
        return lab, perc

class LaunchesTable(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        btn_frame = tk.Frame(self)
        plot_frame = tk.Frame(self)
        btn_frame.pack()
        plot_frame.pack()

        btn1 = ttk.Button(btn_frame, text='Bar Plot', command = lambda: controller.switch_page(BarPlotStat))
        btn2 = ttk.Button(btn_frame, text='Pie Plot', command = lambda: controller.switch_page(PiePlotStat))
        btn1.pack(side='left', padx=10)
        btn2.pack(side='left')


# root = tk.Tk()

# app = BarPlotStat(root)
# app.pack()
# root.mainloop()