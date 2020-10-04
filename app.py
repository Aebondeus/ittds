import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
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
        self.iconbitmap(r'D:\\ProgShit\\Timer\\pic\\tomato-icon.ico') # later i will fix it with path
        self.delta = datetime.timedelta(seconds=1.0)

        self.main_frame = tk.Frame(self)

        self.main_frame.pack(side='top', fill='both', expand=True)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)

        # Basically, here i create some need attributes for working with external classes
        self.frames = {}
        self.timer_check = False # well now i need to check timer in mainapp, so i deleted is_timer_on in TimerFrame
        self.timer_task = None
        self.time = datetime.datetime.now().replace(hour=0, minute=0, second=0)
        self.after_id = None # id for after_cancel
        self.stop_val = 0
        # i dont like stop_val attr, maybe i'll try to replace it with smth else

        for fr in (TopButtonsFrame, TimerButtonFrame, TimerFrame):
            print(fr)
            frame = fr(self.main_frame, self)
            self.frames[fr] = frame
            frame.pack()

    def set_geometry(self):
        w = self.winfo_screenwidth() # узнаем ширину экрана
        h = self.winfo_screenheight() # узнаем высоту экрана
        # осуществляем центровку, числа 200 подходят для моего экрана лол
        w = w//2 - 180
        h = h//2 - 200
        return w, h

    def start_count(self, contr):
        frame = self.frames[contr]
        if self.timer_check or not self.stop_val:
            return
        self.timer_check = True
        self.change_time(frame)

    def change_time(self, frame):
        self.time -= self.delta
        print(self.time)
        self.stop_val = self.time.hour+self.time.minute+self.time.second
        print(self.stop_val)
        frame.change_time(self.time.hour, self.time.minute, self.time.second)
        self.after_id = self.after(1000, func=lambda: self.change_time(frame))
        if not self.stop_val:
            print('we finally here')
            self.after_cancel(self.after_id)
            self.timer_check = False

    def update_timer(self, time, task, restart=False):
        """Restart flag is used for checking
        if we try to restart already working timer"""
        frame = self.frames[TimerFrame]
        frame.change_time(time.hour, time.minute, time.second)
        if  restart:
            self.after_cancel(self.after_id) # after_cancel get after-function id and stop after
            self.timer_check = False
        self.time = frame.get_time
        self.stop_val = self.time.hour+self.time.minute+self.time.second
        print(self.time)
        self.timer_task = task

class TopButtonsFrame(tk.Frame):
    """Frame that contain 3 buttons, that call some TopLevel-windows"""
    # i will create more functions to these buttons later 
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        btn1 = ttk.Button(self, text='Set up Timer',
                          command = lambda: self.create_new_window(SettingTimerWindow, controller))
        btn1.grid(row=0, column=0, sticky='nsew')
        btn2 = ttk.Button(self, text='Statistics')
        btn2.grid(row=0, column=1, sticky='nsew')
        btn3 = ttk.Button(self, text='Change Tomato')
        btn3.grid(row=0, column=2, sticky='nsew')

    def create_new_window(self, cls, controller):
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
        data = Image.open(r'D:\\ProgShit\\Timer\\pic\\tomato.png') # 1
        photo = ImageTk.PhotoImage(data) # 2
        lbl = tk.Label(self, image=photo) # 3
        lbl.image = photo # 4

        # here i bind label with function
        lbl.bind('<Button-1>', lambda event: controller.start_count(TimerFrame)) # lambda just to remind me that this type of work is great too
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

    total = 0 # with this value we keep number of new windows at 1

    def __init__(self, parent):
        SettingTimerWindow.total = 1
        tk.Toplevel.__init__(self, parent)
        self.title('Set up Timer')
        self.geometry('240x130+%d+%d' % parent.set_geometry())
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", func=lambda: self.close())
        # thing above this comment just add new func to close-button [x]

        inner_frame = tk.Frame(self)
        inner_frame.pack()

        lbl1 = tk.Label(inner_frame, text='How many time do you want to work?')
        lbl2 = tk.Label(inner_frame, text='What is the point of this timer?')
        self.time_field = tk.Entry(inner_frame, width=20)
        self.task_field = tk.Entry(inner_frame, width=20)
        btn1 = ttk.Button(inner_frame,
                          text='To the timer...',
                          command=lambda: self.time_it(parent))

        lbl1.pack()
        self.time_field.pack()
        self.time_field.insert(0,  "00:00:00")
        lbl2.pack()
        self.task_field.pack()
        btn1.pack(pady=10)
        
    def time_it(self, controller):
        time = self.time_field.get()
        task = self.task_field.get()
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
            if controller.timer_check and messagebox.askyesno('Restart timer',
                                                             'Do you want to restart timer?',
                                                              parent=self):
                print('Here we restart')
                controller.update_timer(time, task, True)
            else:
                controller.update_timer(time, task)
            self.close()

    def close(self):
        SettingTimerWindow.total = 0
        self.destroy()

app = MainApp()
app.mainloop()