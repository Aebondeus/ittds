import json_keep as jk
from plot_stat import WorkingBar, BarPlotStat, PiePlotStat, LaunchesTable
import datetime
import os.path
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import ttk
import PIL
from PIL import Image, ImageTk
import winsound

FONT_FOR_TIMER = ('Times New Roman', 20)
TIMER_BUTTON = jk.get_pic()
STOP_SOUND = jk.get_sound()

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

        self.frames = {}

        self.time_hour = int()
        self.time_minute = int()
        self.time_second = int() # will be deleted

        self.time = datetime.datetime.now().replace(hour=0, minute=0, second=0) # this time is only used for timer
        self.after_id = None # id for after_cancel
        self.stop_val = 0

        self.timer_check = False 
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

        self.start_time = ''
        self.stop_time = ''
        self.timer_task = ''
        self.act = ''
        self.min_total = ''

        for fr in (TopButtonsFrame, TimerButtonFrame, TimerFrame):
            frame = fr(self.main_frame, self)
            self.frames[fr] = frame
            frame.pack()

    def set_geometry(self):
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        w = w//2 - 180
        h = h//2 - 200
        return w, h

    def set_new_pic(self, frame):
        frame = self.frames[frame]
        TIMER_BUTTON = jk.get_pic()
        frame.set_lbl(TIMER_BUTTON)

    def set_new_sound(self):
        STOP_SOUND = jk.get_sound()

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
            self.l_tuple = (self.min_total, f'{self.start_time}-{self.stop_time}', self.timer_task, self.act)
            self.jk_data(year, month, day, week_num, week_day, self.time_counter, self.act, self.l_tuple)
            self.time_counter = {}
            self.min_total = 0
            self.cur_hour = 0
            print(self.time_counter)
            
        self.after(1000, self.time_check)

    def new_hour_check(self):
        if self.time_minute == 59:
            if self.time_second == 0:
                self.cur_hour = self.time_hour
                self.cur_res_val = self.res_val.seconds
                self.new_hour_flag = True

    def jk_data(self, year:int, month:tuple, day:str, week_num:int, week_day:int, day_hours:dict, act:str, l_tuple:tuple):
        print('update data')
        if self.stop_val:
            data_lst = [year, month, day, week_num, week_day, day_hours]
        else:
            data_lst = [year, month, day, week_num, week_day, day_hours, act, l_tuple]
        jk.update_data(data_lst)

    def start_count(self, contr):
        frame = self.frames[contr]
        if not self.min_total or self.timer_check:
            return
        self.timer_check = True
        self.start_time = datetime.datetime.now().strftime('%H:%M')
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
            self.stop_time = datetime.datetime.now().strftime('%H:%M')
            self.timer_check = False
            self.time_counter[str(self.time_hour)] = self.minutes_val
            print(self.time_counter)
            self.another_fucking_flag = True
            self.minutes_val = 0
            print('доходит')
            winsound.PlaySound(STOP_SOUND, winsound.SND_NOSTOP)

    def update_timer(self, time, task, act, min_total, restart=False):
        """
        Function that set up time value on main screen.
        Restart flag is used for checking if we try to restart already working timer
        """
        frame = self.frames[TimerFrame]
        frame.change_time(time.hour, time.minute, time.second)
        if  restart:
            self.after_cancel(self.after_id) # after_cancel get after-function id and stop after
            self.timer_check = False
            self.minutes_val = 0
            self.time_counter = {}
        self.time = frame.get_time
        self.fixed_val = self.time
        self.new_val = self.fixed_val - self.delta
        print(self.time)
        self.timer_task = task
        self.act = act
        self.min_total = min_total

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
            elif cur_res_val >= 30:
                if self.time_hour - self.cur_hour:
                    self.time_counter[str(self.cur_hour)] = self.minutes_val
                    self.minutes_val = 0
                    self.new_hour_flag = False
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
        btn3 = ttk.Button(self, text='Settings',
                          command = lambda: self.create_new_window(SettingsWindow, controller))
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
        self.lbl = None 
        self.set_lbl(TIMER_BUTTON)
        # # here i bind label with function
        self.lbl.bind('<Button-1>', lambda event: controller.start_count(TimerFrame))
        # # lambda just to remind me that this type of work is great too
        self.lbl.pack(pady=30)

    def set_lbl(self, pic_link):
        # in this step i made Label with picture
        # this how it is work with PIL, in four steps
        data = Image.open(pic_link).resize((128, 128)) # 1
        photo = ImageTk.PhotoImage(data) # 2
        if self.lbl:
            self.lbl.configure(image=photo)
            self.lbl.image = photo
        else:
            self.lbl = tk.Label(self, image=photo) # 3
            self.lbl.image = photo # 4

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
        min_total = int(time[:2]) * 60 + int(time[3:5])
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
            if controller.timer_check: # если таймер запущен
                if messagebox.askyesno('Restart timer',
                                        'Do you want to restart timer?',
                                        parent=self):
                    print('Here we restart')
                    controller.update_timer(time, task, act, min_total, True) ######
            else:
                controller.update_timer(time, task, act, min_total)  #####
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

class SettingsWindow(tk.Toplevel):
    total = 0
    def __init__(self, parent):
        SettingsWindow.total += 1
        tk.Toplevel.__init__(self)
        self.title('Settings')
        self.geometry('250x200')
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", func=lambda: self.close())

        self.sound = None
        self.pic = None
        self.par = parent

        container = tk.Frame(self)
        sub_container = tk.Frame(self)
        container.pack()
        sub_container.pack()

        pic_container = ttk.Frame(container, borderwidth=4, relief='groove')
        btn_container = ttk.Frame(container)
        smt_container = ttk.Frame(sub_container)
        pic_container.pack(side='left', pady=10, padx=3)
        btn_container.pack(side='left')
        smt_container.pack(side='top')

        self.pic_lbl = tk.Label(pic_container, text='\t\t\n\t\t\n\t\t\n\t\t\n\t\t\n')
        btn1 = ttk.Button(btn_container, text='Change tomato', command = self.change_tomato)
        btn2 = ttk.Button(btn_container, text='Change sound', command = self.change_sound)
        self.smt_btn = ttk.Button(smt_container, text='Submit', command= self.submit)

        self.pic_lbl.pack(fill='both', expand=True)
        btn1.pack(fill='both', expand=True)
        btn2.pack(fill='both', expand=True)
        self.smt_btn.pack()

# i'll try to do something with gif-files

    def change_tomato(self):
        pic = fd.askopenfilename(initialdir=os.path.dirname(os.path.abspath(__file__))+'\\pics')
        try:
            data = Image.open(pic)
            data = data.resize((128,128))
            photo = ImageTk.PhotoImage(data)
            self.pic_lbl['image']= photo     
            self.pic_lbl.image = photo
            self.pic = pic
        except PIL.UnidentifiedImageError:
            messagebox.showerror(title='Not an Image!', message='This file is not an image!')
        except AttributeError:
            pass

    def change_sound(self):
        sound = fd.askopenfilename(initialdir=os.path.dirname(os.path.abspath(__file__))+'\\sounds')
        try:
            fmt = sound.split('.')[1]
            if fmt == 'wav':
                winsound.PlaySound(sound, winsound.SND_NOSTOP)
                self.sound = sound
            else:
                messagebox.showinfo('Wrong sound-format!', message='File must be in WAV-format!')
        except IndexError:
            pass

    def submit(self):
        if self.sound or self.pic:
            if self.sound:
                jk.change_sound(self.sound)
                self.par.set_new_sound()
            if self.pic:
                jk.change_pic(self.pic)
                self.par.set_new_pic(TimerButtonFrame)
            self.close()
        else:
            messagebox.showwarning(title='Nothing is selected', message="You didn't choose anything")

    def close(self):
        SettingsWindow.total = 0
        self.destroy()

app = MainApp()
app.mainloop()