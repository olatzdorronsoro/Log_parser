import matplotlib
from pyparsing import Word, alphas, Suppress, Combine, nums, string, Optional, Regex
from time import strptime
from datetime import datetime
import re 
import calendar
import tkinter as tk
from tkinter import font as tkfont
from tkinter import Text, Listbox, Label, Scrollbar, END, RIGHT, Y, LEFT
from tkcalendar import Calendar, DateEntry
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

class LogParser(tk.Tk):

    def __init__(self, sorted_logs, alert_logs, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Parseador de Logs")
        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic") 
    
        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, Timeline, Analyze, Devices, Alerts):
            page_name = F.__name__
            frame = F(parent=container, controller=self, sorted_logs=sorted_logs, alert_logs=alert_logs)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

class StartPage(tk.Frame):

    def __init__(self, parent, controller, sorted_logs, alert_logs):
        self.sorted_logs = sorted_logs
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Bienvenid@ al parseador de logs", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = tk.Button(self, text="Timeline",
                            command=lambda: controller.show_frame("Timeline"))
        button2 = tk.Button(self, text="Análisis estadístico",
                            command=lambda: controller.show_frame("Analyze"))
        button3 = tk.Button(self, text="Información sobre dispositivos",
                            command=lambda: controller.show_frame("Devices"))
        button4 = tk.Button(self, text="Alertas",
                            command=lambda: controller.show_frame("Alerts"))
        button1.pack(fill=tk.BOTH,expand=1)
        button2.pack(fill=tk.BOTH,expand=1)
        button3.pack(fill=tk.BOTH,expand=1)
        button4.pack(fill=tk.BOTH,expand=1)


class Timeline(tk.Frame):

    def __init__(self, parent, controller, sorted_logs, alert_logs):
        self.sorted_logs = sorted_logs
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Timeline", font=controller.title_font)
        label.pack()
        from_text = Label(self,text="Desde:").pack()
        self.from_calendar = DateEntry(self, state='readonly',width=15)
        self.from_calendar.pack()
        to_text=Label(self,text="Hasta:").pack()        
        self.to_calendar = DateEntry(self, state='readonly',width=15)
        self.to_calendar.pack()
        timefilter_button = tk.Button(self, text="Filtrar por fecha", command=self.filter_date)
        timefilter_button.pack()
        self.devicetext = Text(self,width=15,height=1)
        self.devicetext.pack()
        devicefilter_button = tk.Button(self, text="Filtrar por equipo o módulo", command=self.filter_device)
        devicefilter_button.pack()
        rmfilter_button = tk.Button(self, text="Borrar filtros", command=self.rm_filters)
        rmfilter_button.pack()
        scrollbar=Scrollbar(self)
        scrollbar.pack(side=RIGHT,fill=Y)
        self.text = Listbox(self,yscrollcommand=scrollbar.set)
        self.text.insert(END, "")
        self.text.pack(fill=tk.BOTH,expand=1)
        self.rm_filters()
        scrollbar.config(command=self.text.yview)
        return_button = tk.Button(self, text="Return",
                           command=lambda: controller.show_frame("StartPage"))
        return_button.pack()

    def filter_date(self):
        self.text.delete(0, END)
        for line in self.sorted_logs:
            if (strptime(line.timestampstring,"%Y %b %d %H:%M:%S") >= strptime(self.from_calendar.get_date().strftime("%a %b %d %H:%M:%S %Y")) and 
            strptime(line.timestampstring,"%Y %b %d %H:%M:%S") <= strptime(self.to_calendar.get_date().strftime("%a %b %d %H:%M:%S %Y"))):
                self.text.insert(END, line.timestampstring + " " + line.hostname + " " + line.appname + ": " + line.message)
        self.text.pack(fill=tk.BOTH,expand=1)
        
    def filter_device(self):
        self.text.delete(0, END)
        for line in self.sorted_logs:
            if  self.devicetext.get(1.0, "end-1c") == line.hostname or self.devicetext.get(1.0, "end-1c") == line.appname:
                self.text.insert(END, line.timestampstring + " " + line.hostname + " " + line.appname + ": " + line.message)
        self.text.pack(fill=tk.BOTH,expand=1)

    def rm_filters(self):
        self.text.delete(0,END)
        for line in sorted_logs:
            self.text.insert(END, line.timestampstring + " " + line.hostname + " " + line.appname + ": " + line.message)
        self.text.pack(fill=tk.BOTH,expand=1)

class Analyze(tk.Frame):

    def __init__(self, parent, controller, sorted_logs, alert_logs):
        self.sorted_logs = sorted_logs
        self.alert_logs = alert_logs
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Análisis estadístico", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        self.time=tk.IntVar()
        self.device=tk.IntVar()
        self.alert=tk.IntVar()
        time_button = tk.Checkbutton(self, text='Diagrama de tiempo', variable=self.time, onvalue=1, offvalue=0)
        device_button = tk.Checkbutton(self, text='Diagrama de equipos', variable=self.device, onvalue=1, offvalue=0)
        alert_button = tk.Checkbutton(self, text='Diagrama de alertas', variable=self.alert, onvalue=1, offvalue=0)
        choose_button = tk.Button(self, text="Dibujar diagrama", command=self.choose_analysis)
        time_button.pack()
        device_button.pack()
        alert_button.pack()
        choose_button.pack()

        f = Figure(figsize=(5,4), dpi=100)
        self.canvas=FigureCanvasTkAgg(f,self)
        self.canvas.get_tk_widget().destroy()

        self.button = tk.Button(self, text="Return",
                           command=lambda: controller.show_frame("StartPage"))
        self.button.pack()

    def choose_analysis(self):
        if self.time.get()==1 and self.device.get()==0 and self.alert.get()==0:
            self.analyze_time()
        elif self.device.get()==1 and self.time.get()==0 and self.alert.get()==0:
            self.analyze_device()
        elif self.alert.get()==1 and self.device.get()==0 and self.time.get()==0:
            self.analyze_alert()

    def analyze_time(self):
        self.month_dict = {"Jan": 0, "Feb": 0, "Mar": 0, "Apr": 0, "May": 0,"Jun": 0, "Jul": 0,
                  "Aug": 0, "Sep": 0, "Oct": 0, "Nov": 0, "Dec": 0}
        for log in sorted_logs:
            month = log.timestampstring.split(" ")[1]
            for e in self.month_dict.keys():
                if e == month:
                    self.month_dict[e] = self.month_dict[e] + 1

        x = list(self.month_dict.keys())
        y = list(self.month_dict.values())

        self.button.pack_forget()
        self.canvas.get_tk_widget().destroy()
        f = Figure(figsize=(5,4), dpi=100)
        self.canvas = FigureCanvasTkAgg(f,self)
        ax = f.add_subplot(111)
        ax.bar(x, y)
        ax.set_title("LOGS POR MESES")
        ax.set_xlabel("Mes")
        ax.set_ylabel("Nº de logs")
        for i in range(len(x)):
            ax.text(i, y[i], y[i], ha = 'center')
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.button = tk.Button(self, text="Return",
                           command=lambda: self.controller.show_frame("StartPage"))
        self.button.pack()

    def analyze_device(self):
        devices = list()
        for line in self.sorted_logs:
            if line.hostname != " - ":
                devices.append(line.hostname)
        devices = sorted(list(set(devices)), key=str.lower)
        dev_dict = {device: 0 for device in devices}
        for log in self.sorted_logs:
            device = log.hostname
            for e in dev_dict.keys():
                if e == device:
                    dev_dict[e] = dev_dict[e] + 1

        x = list(dev_dict.keys())
        y = list(dev_dict.values())

        self.button.pack_forget()
        self.canvas.get_tk_widget().destroy()
        f = Figure(figsize=(4,3), dpi=100)
        self.canvas = FigureCanvasTkAgg(f,self)
        ax = f.add_subplot(111)
        ax.bar(x, y)
        ax.set_title("LOGS POR EQUIPOS")
        ax.set_xlabel("Equipos")
        ax.set_ylabel("Nº de logs")
        ax.tick_params(axis='x', labelrotation = 58, labelsize=7)
        for i in range(len(x)):
            ax.text(i, y[i], y[i], ha = 'center')
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.button = tk.Button(self, text="Return",
                           command=lambda: self.controller.show_frame("StartPage"))
        self.button.pack()

    def analyze_alert(self):
        login_index = self.alert_logs.index("MÁS DE 3 INTENTOS FALLIDOS DE LOGIN A LA MISMA IP")
        directory_index = self.alert_logs.index("ACCESO A DIRECTORIO PROHIBIDO")
        blacklist_index = self.alert_logs.index("CONEXIÓN DESDE UNA IP DE LA BLACKLIST")
        last_item_index = len(alert_logs)

        login_logs = directory_index - login_index - 2
        directory_logs = blacklist_index - directory_index - 2
        blacklist_logs = last_item_index - blacklist_index - 1

        x = ["Intento de login fallido a la misma IP", "Acceso a directorio prohibido", "Blacklist"]
        y = [login_logs, directory_logs, blacklist_logs]

        self.button.pack_forget()
        self.canvas.get_tk_widget().destroy()     
        f = Figure(figsize=(4,3), dpi=100)
        self.canvas = FigureCanvasTkAgg(f,self)
        ax = f.add_subplot(111)
        ax.bar(x, y)
        ax.set_title("LOGS ALERTAS")
        ax.set_xlabel("Alertas")
        ax.set_ylabel("Nº de logs")
        for i in range(len(x)):
            ax.text(i, y[i], y[i], ha = 'center')
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        self.button = tk.Button(self, text="Return",
                           command=lambda: self.controller.show_frame("StartPage"))
        self.button.pack()

class Devices(tk.Frame):

    def __init__(self, parent, controller, sorted_logs, alert_logs):
        self.sorted_logs = sorted_logs
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Información sobre dispositivos", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        devices_button=tk.Button(self, text="Equipos", command=self.devices)
        devices_button.pack()
        modules_button=tk.Button(self, text="Módulos", command=self.modules)
        modules_button.pack()
        scrollbar=Scrollbar(self)
        scrollbar.pack(side=RIGHT,fill=Y)
        self.text = Listbox(self,yscrollcommand=scrollbar.set)
        self.text.insert(END, " ")
        self.text.pack(fill=tk.BOTH,expand=1)
        scrollbar.config(command=self.text.yview)
        button= tk.Button(self, text="Return",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack()

    def devices(self):
        self.text.delete(0, END)
        devices = list()
        for line in self.sorted_logs:
            if line.hostname != " - ":
                devices.append(line.hostname)
        devices = sorted(list(set(devices)), key=str.lower)
        disp_dict = {device: 0 for device in devices}
        for log in self.sorted_logs:
            device = log.hostname
            for e in disp_dict.keys():
                if e == device:
                    disp_dict[e] = disp_dict[e] + 1      
        
        for device, value in disp_dict.items():
            if device != " - ":
                self.text.insert(END, device + ": " + str(value))
        self.text.pack(fill=tk.BOTH,expand=1)
 
    def modules(self):
        self.text.delete(0, END)
        modules = list()
        for line in self.sorted_logs:
            modules.append(line.appname)
        modules = sorted(list(set(modules)), key=str.lower)
        module_dict = {module: 0 for module in modules}
        for log in self.sorted_logs:
            module = log.appname
            for e in module_dict.keys():
                if e==module:
                    module_dict[e] = module_dict[e] + 1

        for module,value in module_dict.items():
            if module != " - ":
                self.text.insert(END, module + ": " + str(value))
        self.text.pack(fill=tk.BOTH,expand=1)

class Alerts(tk.Frame):

    def __init__(self, parent, controller, sorted_logs, alert_logs):
        self.sorted_logs = sorted_logs
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Alertas", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        scrollbar=Scrollbar(self)
        scrollbar.pack(side=RIGHT,fill=Y)
        text = Listbox(self,yscrollcommand=scrollbar.set)
        
        for line in alert_logs:
            if line == "":
                text.insert(END,line)
            elif line == "MÁS DE 3 INTENTOS FALLIDOS DE LOGIN A LA MISMA IP" or line == "ACCESO A DIRECTORIO PROHIBIDO" or line == "CONEXIÓN DESDE UNA IP DE LA BLACKLIST":
                text.insert(END, line)
                text.itemconfig(text.size()-1,{'bg':'OrangeRed3'})
            else:
                text.insert(END, line.timestampstring + " " + line.hostname + " " + line.appname + ": " + line.message)
        
        text.pack(fill=tk.BOTH,expand=1)
        scrollbar.config(command=text.yview)
        button= tk.Button(self, text="Return",
                           command=lambda: controller.show_frame("StartPage"))
        button.pack() 

class Syslog:

    def __init__(self):
        ints = Word(nums)
        _month = Word(string.ascii_uppercase , string.ascii_lowercase, exact=3)
        _day   = ints
        _hour  = Combine(ints + ":" + ints + ":" + ints)
        _timestamp = _month + _day + _hour
        _hostname =Word(alphas + nums + "_" + "-" + ".")
        _appname = Combine(Optional(Word(" " + "-")) + Word(alphas +  "/" + "-" + "_" + ".") + Optional(Word(" " + nums + ".")) + Optional(Word( "(" + alphas  + nums + "_" + "-" + "." + ")")) + Optional(Word( "[" + nums + "]") ) + Suppress(":"))
        _message = Regex(".*")
        self.__pattern = _timestamp + _hostname + _appname + _message
        self.parsed = None
        self.timestamp = None
        self.hostname = None
        self.appname = None
        self.message = None
    
    def parse(self, line):
        parsed = self.__pattern.parseString(line)
        self.parsed = parsed
        self.timestampstring = "2021 " + parsed[0] + " " +  parsed[1] + " "  + parsed[2]
        self.timestampdate = strptime(self.timestampstring, "%Y %b %d %H:%M:%S")
        self.hostname = parsed[3]
        self.appname = parsed[4]
        self.message = parsed[5]
        

class Apache:

    def __init__(self):
        ints = Word(nums)
        _dayweek = Combine(Suppress("[")+Word(string.ascii_uppercase , string.ascii_lowercase, exact=3))
        _month = Word(string.ascii_uppercase , string.ascii_lowercase, exact=3)
        _day = ints
        _hour = Combine(ints + ":" + ints + ":" + ints)
        _year = Combine(ints + Suppress("]"))
        _timestamp = _dayweek + _month + _day + _hour + _year
        _level = Combine(Suppress("[") + Word(alphas) + Suppress("]"))
        _appname = Optional(Word(alphas + nums + "_" + "." + "(" + ")"))
        _hostname = Optional(Combine(Suppress("[") + Suppress(Word(alphas+" ")) + Word(nums + ".") + Suppress("]")))
        _message = Regex(".*")
        self.__pattern = _timestamp + _level + _appname + _hostname + _message
        self.parsed = None
        self.timestamp = None
        self.hostname = None
        self.appname = None
        self.message = None

    def parse(self, line):
        parsed = self.__pattern.parseString(line)
        self.parsed = parsed
        self.timestampstring = "2021 " + parsed[1] + " " + parsed [2] + " " + parsed[3]
        self.timestampdate = strptime(self.timestampstring, "%Y %b %d %H:%M:%S")
        if bool(re.match(r"^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$",parsed[6])):
            self.hostname = parsed[6]
            self.appname = " - "
        else:
            self.appname = parsed[6]
            self.hostname = " - "
        self.message = parsed [7]

class Proxifier:

    def __init__(self):
        ints = Word(nums)
        _month = Combine(Suppress("[") + ints + Suppress("."))
        _day = ints
        _hour = Combine(ints + ":" + ints + ":" + ints + Suppress("]"))
        _timestamp = _month + _day + _hour
        _appname = Combine(Word(alphas + nums + "." + "-" + "_") + Optional(" " + "*" + Word(nums)))
        _id = Word(nums + "-")
        _ip = Word(alphas + nums + ":" + "." + "-")
        _status = Word(alphas)
        _message = Regex(".*")
        _message = _ip + _status + _message
        self.__pattern = _timestamp + _appname + _id + _message
        self.parsed = None
        self.timestamp = None
        self.hostname = None
        self.appname = None
        self.message = None

    def parse(self, line):
        parsed = self.__pattern.parseString(line)
        self.parsed = parsed
        _month = calendar.month_name[int(parsed[0])]
        _month = _month [0:3]
        self.timestampstring = "2021 " + _month + " " + parsed[1] + " " + parsed [2]
        self.timestampdate = strptime(self.timestampstring, "%Y %b %d %H:%M:%S")
        self.hostname = " - "
        self.appname = parsed[3]
        self.message = parsed[5] + " " + parsed[6] + " " + parsed[7]

class Android:

    def __init__(self):
        ints = Word(nums)
        _month = Combine(ints + Suppress("-"))
        _day = ints
        _hour = Combine(ints + ":" + ints + ":" + ints + Suppress("." + ints))
        _timestamp = _month + _day + _hour
        _pid = ints
        _tid = ints
        _priority = Word(alphas)
        _appname = Combine(Word(alphas + "_" + " " + "-" + "." + nums + "(" + ")") + Suppress(":"))
        _message = Regex(".*")
        self.__pattern = _timestamp + _pid + _tid + _priority + _appname + _message
        self.parsed = None
        self.timestamp = None
        self.hostname = None
        self.appname = None
        self.message = None

    def parse(self,line):
        parsed = self.__pattern.parseString(line)
        self.parsed = parsed
        _month = calendar.month_name[int(parsed[0])]
        _month = _month [0:3]
        self.timestampstring = "2021 " +  _month + " " + parsed[1] + " " + parsed[2]
        self.timestampdate = strptime(self.timestampstring, "%Y %b %d %H:%M:%S")
        self.hostname = " - "
        self.appname = parsed[6]
        self.message = parsed[7]

def parse():
   
    file_linux = "/home/olatz/repos/loghub/Linux/Linux.log"
    file_ssh = "/home/olatz/repos/loghub/OpenSSH/SSH.log"
    file_apache = "/home/olatz/repos/loghub/Apache/Apache.log"
    file_proxifier = "/home/olatz/repos/loghub/Proxifier/Proxifier.log"
    file_android = "/home/olatz/repos/loghub/Android/Android.log"
        
    with open(file_linux) as _file:
        lines_linux = _file.readlines()
        lines_linux = [line.rstrip() for line in lines_linux]

    with open(file_ssh) as _file:
        lines_ssh = _file.readlines()
        lines_ssh = [line.rstrip() for line in lines_ssh]
    
    with open(file_apache) as _file:
        lines_apache = _file.readlines()
        lines_apache = [line.rstrip() for line in lines_apache]
    
    with open(file_proxifier) as _file:
        lines_proxifier = _file.readlines()
        lines_proxifier = [line.rstrip() for line in lines_proxifier]
    
    with open(file_android) as _file:
        lines_android = _file.readlines()
        lines_android = [line.rstrip() for line in lines_android]

    linux = []
    for line in lines_linux:
        _linux = Syslog()
        _linux.parse(line)
        linux.append(_linux)
    
    ssh = []
    for line in lines_ssh:
        _ssh = Syslog()
        _ssh.parse(line)
        ssh.append(_ssh)
    
    apache = []
    for line in lines_apache:
        _apache = Apache()
        _apache.parse(line)
        apache.append(_apache)
    
    proxifier = []
    for line in lines_proxifier:
        _proxifier = Proxifier()
        _proxifier.parse(line)
        proxifier.append(_proxifier)
    
    android = []
    for line in lines_android:
        _android = Android()
        _android.parse(line)
        android.append(_android)

    _logs= linux+ssh+apache+proxifier+android
    _sorted = sorted(_logs, key=lambda x: x.timestampdate)

    file = open("Sorted_logs.log", "w")
    for log in _sorted:
        file.write(log.timestampstring + " " + log.hostname + " " + log.appname + ": " + log.message + " \n")
    file.close()

    return _sorted

def alerts(sorted_logs):
    alerts = list()
    alerts.append("MÁS DE 3 INTENTOS FALLIDOS DE LOGIN A LA MISMA IP")
    
    devices = list()
    for line in sorted_logs:
        if line.hostname != " - ":
            devices.append(line.hostname)
    devices = sorted(list(set(devices)), key=str.lower)

    ips = list()
    for line in sorted_logs:
        message_split=line.message.split(" ")
        for word in message_split:
            if word.startswith("rhost="):
                if word!= "rhost=":
                    ipstring=re.split('=', word)
                    ips.append(ipstring[1])
    ips = list(set(ips))

    for device in devices:
        for ip in ips:
            count=0
            logs = list()
            for line in sorted_logs:
                if line.message.startswith("authentication failure;") and device==line.hostname:
                    if ip in line.message:
                        count=count+1
                        logs.append(line)
            if count>=3:
                for line in logs:
                    alerts.append(line)
    
    alerts.append("")
    alerts.append("ACCESO A DIRECTORIO PROHIBIDO")
    
    for line in sorted_logs:
        if line.message.startswith("Directory index forbidden by rule:"):
            alerts.append(line)
    
    alerts.append("")
    alerts.append("CONEXIÓN DESDE UNA IP DE LA BLACKLIST")

    blacklist = ["24.54.76.216","82.68.222.194","217.187.83.139"]

    for ip in blacklist:
        for line in sorted_logs:
            if line.message.startswith("connection from") and (ip in line.message):
                alerts.append(line)
    
       
    return alerts

if __name__ == '__main__':
    sorted_logs = parse() 
    alert_logs = alerts(sorted_logs)
    app = LogParser(sorted_logs, alert_logs)
    app.mainloop()
