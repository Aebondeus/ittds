import json_keep as jk
from plot_stat import WorkingBar, BarPlotStat, PiePlotStat, LaunchesTable
import datetime
import os.path
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk

FONT_FOR_TIMER = ('Times New Roman', 20)

class MainApp(tk.Tk):
    
    """Root part of the app. It is create all main things and contain some logic
       for other classes. But i think that this is bad for OOP, so :("""
    def __init__(self):
        tk.Tk.__init__(self)
        self.title('Pomodorro Timer')
        self.geometry('300x300+%d+%d' % self.set_geometry())
        self.resizable(False, False)
        self.iconbitmap(os.path.dirname(os.path.abspath(__file__))+'\\pics\\tomato-icon.ico')
        self.delta = datetime.timedelta(seconds=1.0)

        self.main_frame = tk.Frame(self)

        self.main_frame.pack(side='top', fill='both', expand=True)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        # Basically, here i create some attributes for working with external classes
        self.frames = {}
        self.timer_check = False # well now i need to check timer in mainapp, so i deleted is_timer_on in TimerFrame
        self.timer_task = ''
        self.act = ''
        self.time = datetime.datetime.now().replace(hour=0, minute=0, second=0) # this time is only used for timer
        self.after_id = None # id for after_cancel
        self.stop_val = 0
        # but it wasn't the end. He couldn't stop, oh no, not him. Sick bastard

        # most hated but significant attrs and funcs are coming right now
        self.time_hour = int()
        self.time_minute = int()
        self.time_second = int()
        self.new_hour_flag = False
        self.another_fucking_flag = False
        self.time_counter = {} # dict for collecting time
        self.time_check() # checking current time
        self.cur_hour = int() # attr that catch value of running time
        self.cur_res_val = 0 # attr that catch curent value of difference between fixed_val and new_val
        self.minutes_val = 0 # attr that gets minutes, then passing them to the time_counter
        self.fixed_val = None # fixed_value - attr that catch initial value of minutes set
        self.new_val = None # new_value - attr for accumulating elapsed seconds. Accum occurs by subtstracting this value from the fixed_val
        self.res_val = datetime.timedelta() # result_value - attr that accumulate elapsed seconds
        


        for fr in (TopButtonsFrame, TimerButtonFrame, TimerFrame):
            print(fr)
            frame = fr(self.main_frame, self)
            self.frames[fr] = frame
            frame.pack()

    def set_geometry(self):
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        w = w//2 - 180
        h = h//2 - 200
        return w, h


    def time_check(self):
        '''
        Here we checking time for our timer and update data for json-file
        '''
        time = datetime.datetime.now()
        date = datetime.date(time.year, time.month, time.day)
        self.time_hour = time.hour
        self.time_minute = time.minute
        self.time_second = time.second
        if not self.new_hour_flag:
            self.new_hour_check()
        year, month, day = time.year, (time.month, time.strftime('%b')) , str(time.day)
        week_num, week_day = date.isocalendar()[1:]
        if self.another_fucking_flag:
            print('RISE UP FUCKING FLAG I HATE U')
            self.another_fucking_flag = False
            self.jk_data(year, month, day, week_num, week_day, self.time_counter, self.act)
            if not self.cur_hour:
                del self.time_counter[str(self.time_hour)]
            else:
                del self.time_counter[str(self.cur_hour)]
                self.cur_hour = 0
            print(self.time_counter)
            
        self.after(1000, self.time_check)

    def new_hour_check(self):
        if self.time_minute == 59:
            if self.time_second == 0:
                self.cur_hour = self.time_hour
                self.cur_res_val = self.res_val.seconds
                self.new_hour_flag = True

    def jk_data(self, year:int, month:tuple, day:str, week_num:int, week_day:int, day_hours:dict, act:str):
        print('update data')
        if self.stop_val:
            data_lst = [year, month, day, week_num, week_day, day_hours]
        else:
            data_lst = [year, month, day, week_num, week_day, day_hours, act]
        jk.update_data(data_lst)

    def start_count(self, contr):
        frame = self.frames[contr]
        if self.timer_check:
            return
        self.timer_check = True
        if not self.time_counter.get(str(self.time_hour), None):
            self.time_counter[str(self.time_hour)] = 0
        self.change_time(frame)

    def change_time(self, frame):
        self.time -= self.delta
        self.res_val = self.fixed_val - self.new_val
        self.stop_val = self.time.minute + self.time.second

        if not self.new_hour_flag:
            if self.res_val.seconds == 60:
                self.logging_time()

        elif self.new_hour_flag:
            if self.res_val.seconds == 60:
                self.logging_time(cur_res_val = self.cur_res_val)

        self.new_val -= datetime.timedelta(seconds=1)

        frame.change_time(self.time.hour, self.time.minute, self.time.second)
        self.after_id = self.after(1000, func=lambda: self.change_time(frame))

        if not self.stop_val:
            print('we finally here')
            self.after_cancel(self.after_id)
            self.timer_check = False
            self.time_counter[str(self.time_hour)] = self.minutes_val
            print(self.time_counter)
            self.another_fucking_flag = True
            self.minutes_val = 0
            print('доходит')

    def update_timer(self, time, task, act, restart=False):
        """
        Function that set up time value on main screen.
        Restart flag is used for checking if we try to restart already working timer
        """
        frame = self.frames[TimerFrame]
        frame.change_time(time.hour, time.minute, time.second)
        if  restart:
            self.after_cancel(self.after_id) # after_cancel get after-function id and stop after
            self.timer_check = False
        self.time = frame.get_time
        self.fixed_val = self.time
        self.new_val = self.fixed_val - self.delta
        print(self.time)
        self.timer_task = task
        self.act = act

    def logging_time(self, cur_res_val=0):
        """
        Add minutes values in attr. If the hour ends distributes 
        the received minutes to the corresponding hours.
        """
        print('apparently res_val is 60')
        self.fixed_val = self.new_val
        self.minutes_val += 1
        print(f'Now fixed-val = {self.fixed_val}, minutes-val = {self.minutes_val}')
        if cur_res_val:
            if self.cur_hour == 23:
                self.time_counter[str(0)] = 0
            else:
                self.time_counter[str(self.cur_hour+1)] = 0
            print(f'cur_res_val is equal {cur_res_val}')
            if cur_res_val < 30:
                self.time_counter[str(self.time_hour)] = self.minutes_val
                self.minutes_val = 0
                self.new_hour_flag = False
                self.another_fucking_flag = True
            elif cur_res_val >= 30:
                if self.time_hour - self.cur_hour:
                    self.time_counter[str(self.cur_hour)] = self.minutes_val
                    self.minutes_val = 0
                    self.new_hour_flag = False
                    self.another_fucking_flag = True
            print(self.time_counter)



class TopButtonsFrame(tk.Frame):
    """Frame that contain 3 buttons, that call some TopLevel-windows"""
    # i will create more functions to these buttons later 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        btn1 = ttk.Button(self, text='Set up Timer',
                          command = lambda: self.create_new_window(SettingTimerWindow, controller))
        btn1.grid(row=0, column=0, sticky='nsew')
        btn2 = ttk.Button(self, text='Statistics',
                          command = lambda: self.create_new_window(StatisticWindow, controller))
        btn2.grid(row=0, column=1, sticky='nsew')
        btn3 = ttk.Button(self, text='Change Tomato')
        btn3.grid(row=0, column=2, sticky='nsew')

    def create_new_window(self, cls, controller):
        print(cls.total)
        if cls.total:
            return
        new_window = cls(controller)
        # attributes('-topmost', 'true') added to get TopLevel appear in fron of tk.Tk
        new_window.attributes('-topmost', 'true')


class TimerButtonFrame(tk.Frame):
    """Frame for start the timer by pushing big juicy button"""
    
    def __init__(self, parent, controller): 
        tk.Frame.__init__(self, parent)

        # in this step i made Label with picture
        # this how it is work with PIL, in four steps
        data = Image.open(os.path.dirname(os.path.abspath(__file__)) + '\\pics\\tomato.png') # 1
        photo = ImageTk.PhotoImage(data) # 2
        lbl = tk.Label(self, image=photo) # 3
        lbl.image = photo # 4

        # here i bind label with function
        lbl.bind('<Button-1>', lambda event: controller.start_count(TimerFrame))
        # lambda just to remind me that this type of work is great too
        lbl.pack(pady=30)


class TimerFrame(tk.Frame):
    """
    Frame for illustrating of the timer """
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # buffer time is just a useful attribute for getting datetime-value
        # there is no need to type something like (datetime.datetime(year=2020, month=12 etc))
        # just use .now and .replace it attributes
        self.buffer_time = datetime.datetime.now().replace(hour=0, minute=0, second=0)
        self.timer_var = tk.StringVar()
        self.timer_var.set(self.buffer_time.strftime("%H:%M:%S"))
        self.timer_lbl = tk.Label(self, textvariable=self.timer_var, font=FONT_FOR_TIMER)
        self.timer_lbl.pack()
 
    @property
    def get_time(self):
        return self.buffer_time

    def change_time(self, hour:int, minute:int, second:int):
        self.buffer_time = self.buffer_time.replace(hour=hour, minute=minute, second=second)
        self.timer_var.set(self.buffer_time.strftime("%H:%M:%S"))


class SettingTimerWindow(tk.Toplevel):
    """
    Creating TopLevel Window for setting the timer,
    adding a task and some tags for your timer
    """
    total = 0 # with this value we keep number of new windows at 1

    def __init__(self, parent):
        SettingTimerWindow.total = 1
        tk.Toplevel.__init__(self, parent)
        self.title('Set up Timer')
        self.geometry('260x200+%d+%d' % parent.set_geometry())
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", func=lambda: self.close())
        # thing above this comment just add new func to close-button [x]

        inner_frame = tk.Frame(self)
        inner_frame.pack()

        lbl1 = tk.Label(inner_frame, text='How many time do you want to work?')
        lbl2 = tk.Label(inner_frame, text='What is the point of this timer?')
        lbl3 = tk.Label(inner_frame, text='Tags')
        self.time_field = tk.Entry(inner_frame, width=20)
        self.task_field = tk.Entry(inner_frame, width=20)
        self.time_field.insert(0,  "00:00:00")

        lbl1.pack(side='top')
        self.time_field.pack(side='top')

        lbl2.pack(side='top')
        self.task_field.pack()
        lbl3.pack(side='top')

        radio_frame = tk.Frame(inner_frame)
        radio_frame_2 = tk.Frame(inner_frame)
        radio_frame.pack()
        radio_frame_2.pack()
        
        self.activities = ['Work', 'Study', 'Chill', 'Sport', 'Games', 'Read', 'Cooking', 'Nothing']
        self.act_val = tk.IntVar()
        work = tk.Radiobutton(radio_frame,
                              text = self.activities[0],
                              variable=self.act_val,
                              value = 0)

        study = tk.Radiobutton(radio_frame,
                              text = self.activities[1],
                              variable=self.act_val,
                              value = 1)

        chill = tk.Radiobutton(radio_frame,
                              text = self.activities[2],
                              variable=self.act_val,
                              value = 2)

        sport = tk.Radiobutton(radio_frame,
                              text = self.activities[3],
                              variable=self.act_val,
                              value = 3)

        games = tk.Radiobutton(radio_frame_2,
                              text = self.activities[4],
                              variable=self.act_val,
                              value = 4)

        reading = tk.Radiobutton(radio_frame_2,
                              text = self.activities[5],
                              variable=self.act_val,
                              value = 5)

        cook = tk.Radiobutton(radio_frame_2,
                              text = self.activities[6],
                              variable=self.act_val,
                              value = 6)

        nothing = tk.Radiobutton(radio_frame_2,
                              text = self.activities[7],
                              variable=self.act_val,
                              value = 7)

        for i in (work, study, chill, sport):
            i.pack(side='left')
        for i in (games, reading, cook, nothing):
            i.pack(side='left')

        btn1 = ttk.Button(inner_frame,
                          text='To the timer...',
                          command=lambda: self.time_it(parent))
        btn1.pack(side='top', pady=10)

        
    def time_it(self, controller):
        '''
        It collect all needed data and give it to the MainApp 
        '''
        time = self.time_field.get()
        task = self.task_field.get()
        act = self.activities[self.act_val.get()]
        print(act)
        if not task:
            task = 'Just for fun!'
        try:
            time = datetime.datetime.strptime(time, '%H:%M:%S')
        except ValueError:
            # parent argument for the messagebox is added to get box appear in front of toplevel
            messagebox.showerror('Wrong Data/Time Format',
                                 'You need to enter time in HH:MM:SS-format',
                                  parent=self) 
            self.time_field.delete(0, 'end')
            self.time_field.insert(0, "00:00:00")
        else:
            if controller.timer_check:
                if messagebox.askyesno('Restart timer',
                                        'Do you want to restart timer?',
                                        parent=self):
                    print('Here we restart')
                    controller.update_timer(time, task, act, True)
            else:
                controller.update_timer(time, task, act)
            self.close()

    def close(self):
        SettingTimerWindow.total = 0
        self.destroy()


class StatisticWindow(tk.Toplevel):

    """Here we will show some graphs and statistics about launches of timer"""

    total = 0 # with this value we keep number of new windows at 1

    def __init__(self, parent):
        StatisticWindow.total = 1
        tk.Toplevel.__init__(self, parent)
        self.title('Stats and Graphs')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", func=lambda: self.close())
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        inner_frame = tk.Frame(self)
        inner_frame.pack()

        self.frames = {}

        for F in (BarPlotStat, PiePlotStat, LaunchesTable):
            fr = F(inner_frame, self)
            self.frames[F] = fr
            fr.grid(row=0, column=0, sticky='nsew')
        
        self.switch_page(BarPlotStat)

    def switch_page(self, cont):
        fr = self.frames[cont]
        fr.tkraise()

    def close(self):
        StatisticWindow.total = 0
        self.destroy()

app = MainApp()
app.mainloop()