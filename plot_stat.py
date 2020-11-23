import json_keep as jk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import tkinter as tk
from tkinter import ttk

class WorkingBar:
    """Class for animation of the bars in plot"""
    def __init__(self, bar, annot):
        self.bar = bar
        self.annot = annot

    def connect(self):
        self.motion = self.bar.figure.canvas.mpl_connect('motion_notify_event', self.hover) 

    def update(self):
        x, y = (self.bar.get_x(), self.bar.get_height()) 
        self.annot.xy=(x, y) 
        text = f'{self.bar.get_height()}'
        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_alpha(0.4)
        self.annot.set_visible(True)
        self.bar.set_facecolor('red')

    def hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes != self.bar.axes: return 
        cont, _ = self.bar.contains(event)
        if cont:
            self.update()
            self.bar.figure.canvas.draw_idle()
        else:
            if vis:
                self.annot.set_visible(False)
                self.bar.set_facecolor('c')
                self.bar.figure.canvas.draw_idle()

class BarPlotStat(tk.Frame):
    """The class draws a graph that shows the number of minutes
    that the user focused on their tasks, per day, week, month, and year"""
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        btn_frame = tk.Frame(self)
        plot_frame = tk.Frame(self)
        btn_frame.pack()
        plot_frame.pack()

        btn1 = ttk.Button(btn_frame, text='Pie Plot', command = lambda: controller.switch_page(PiePlotStat))
        btn2 = ttk.Button(btn_frame, text='Table', command = lambda: controller.switch_page(LaunchesTable))
        btn1.pack(side='left', padx=10)
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
        for side in ('top', 'left', 'right'):
            self.ax.spines[side].set_visible(False)
        self.bb = [] # bars-box
        
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.draw()
        x, y = self.get_data('day_hours')
        self.fig.suptitle(f"Today you've been focused {sum(y)} minutes")
        self.create_graph(x, y)
        self.canvas.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def get_data(self, ds:str):
        data = jk.get_bar_data(ds)
        x, y = list(data.keys()), list(data.values())
        return x, y

    def create_graph(self, *data):
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
            annot = self.ax.annotate('', xy=(-1,-10), xytext=(-20, 18), textcoords='offset points',
                                    bbox=dict(boxstyle='round', fc='w'),
                                    arrowprops=dict(arrowstyle='->'))
            new_bar = WorkingBar(bar, annot)
            new_bar.connect()
            self.bb.append(new_bar)

# need to animate this function below
    def change_data(self, event):
        ds = self.combobox.get() #data_string
        dct = {'For a day':'day_hours',
               'For a week':'week_days',
               'For a month':'month_days',
               'For a year':'year_months'}
        self.ax.clear()
        date_string = ds.split()[2]
        x, y = self.get_data(dct[ds])
        if date_string is not 'day':
            self.fig.suptitle(f"This {date_string} you've been focused {sum(y)} minutes")
        else:
            self.fig.suptitle(f"Today you've been focused {sum(y)} minutes")
        self.create_graph(x, y)
        self.canvas.draw()

    def animate_graph(self, i):
        pass

class PiePlotStat(tk.Frame):
    '''The graph shows the percentage of tags selected by the user for any task'''
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
        self.ax.pie(perc, labels=labels, autopct='%1.1f%%')

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

        hiden_lbl = tk.Label(plot_frame, text='')
        hiden_lbl.pack(side='top', pady=10)

        cols = ('one','two','three','four')
        col_names = ('Minutes','Interval', 'Task', 'Tag')
        cols_width = (60, 70, 200, 70)
        table = ttk.Treeview(plot_frame, columns=cols, height=19)
        table.column('#0', width=100)
        for col, col_name, col_width in zip(cols, col_names, cols_width):
            table.column(col, width=col_width, anchor=tk.N)
            table.heading(col, text=col_name)
        self.get_data(table)
        table.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        btn1.pack(side='left', padx=10)
        btn2.pack(side='left')

    def get_data(self, table):
        working_dct = jk.get_lauch_data()
        sorted_date = sorted(working_dct, reverse=True)
        id = 1
        for date in sorted_date:
            folder = table.insert('', id, text=date.strftime('%d, %b'))
            for values in working_dct[date]:
                table.insert(folder, 'end', values=values)
            
