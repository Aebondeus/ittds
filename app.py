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

        # Basically, here i will create some need attributes for working with external classes
        self.frames = {}
        # self.new_windows = {} # specially added dict to keep watching that we open just one TopLevel-window from every button
        self.timer_check = False # well now i need to check timer in mainapp, so i deleted is_timer_on in TimerFrame
        self.timer_task = None

        for fr in (TopButtonsFrame, TimerButtonFrame, TimerFrame):
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
        time = datetime.datetime.strptime(frame.timer_var.get(), '%H:%M:%S')
        if self.timer_check:
            return
        self.timer_check = True
        self.change_time(frame, time)

    def change_time(self, frame, time):
        if time.hour + time.minute + time.second <= 0: self.timer_check = False; return
        time -= self.delta
        frame.timer_var.set(time.strftime('%H:%M:%S'))
        self.after(1000, func=lambda: self.change_time(frame, time))

    def update_timer(self, time_data, restart=False):
        """Restart flag is used for checking
        if we try to restart already working timer"""
        frame = self.frames[TimerFrame]
        print(frame.buffer_time, frame.timer_var)
        if not restart:
            frame.timer_var.set(time_data.strftime("%H:%M:%S"))
        else:
            pass
    

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
        # print(controller.new_windows)
        # here we check if we have already open windows
        # if controller.new_windows.get(cls):
        #     return
        # controller.new_windows[cls] = self
        # new_window = cls(controller)
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



class SettingTimerWindow(tk.Toplevel):

    total = 0

    def __init__(self, parent):
        SettingTimerWindow.total += 1
        tk.Toplevel.__init__(self, parent)
        self.title('Set up Timer')
        self.geometry('240x130+%d+%d' % parent.set_geometry())
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", func=lambda: self.close(parent))
        # that thing above this comment just add new func to close-button [x]

        inner_frame = tk.Frame(self)
        inner_frame.pack()

        lbl1 = tk.Label(inner_frame, text='How many time do you want to work?')
        lbl2 = tk.Label(inner_frame, text='What is the point of this timer?')
        self.test_field_1 = tk.Entry(inner_frame, width=20)
        self.test_field_2 = tk.Entry(inner_frame, width=20)
        btn1 = ttk.Button(inner_frame, text='To the timer...', command=lambda: self.time_it(parent))

        lbl1.pack()
        self.test_field_1.pack()
        lbl2.pack()
        self.test_field_2.pack()
        btn1.pack(pady=10)
        
    def time_it(self, controller):
        if controller.timer_check and not messagebox.askyesno('Restart timer', 'Do you want to restart timer?', parent=self):
            return
        time = self.test_field_1.get()
        task = self.test_field_2.get()
        if not task:
            task = 'Just for fun!'
        try:
            time = datetime.datetime.strptime(time, '%H:%M:%S')
        except ValueError:
            # parent argument for the messagebox is added to get box appear in front of toplevel -----------here
            messagebox.showerror('Wrong Data/Time Format', 'You need to enter time in HH:MM:SS-format', parent=self) 
            self.test_field_1.delete(0, 999999)
            self.test_field_1.insert(0, "00:00:00")
        else:
            SettingTimerWindow.total = 0
            controller.timer_task = task
            controller.update_timer(time)
            self.close(controller)


    def close(self, controller):
        # well with type(x) i finally can delete key-clsss in my dict and don't touch attr directly :)
        # del controller.new_windows[type(self)] 
        self.destroy()

app = MainApp()
app.mainloop()

# Today, 01.10, i find nice error - i can't open TopLevel when i set timer, but don't start it
# i need to find out how open it
# I was wrong. The error was when i closed TopLevel with [x]. So, i use self.protocol('WM_DELETE_WINDOW, my_func)
# and now it is work well

# today i end my journey. I will try to fix restart timer tomorrow
