"""
Welcome to use PyToka.
This is a Python Editor.
Made by 是真的Win12Home
Free and Lite.
"""
#*~* coding=utf-8 *~*
from ttkbootstrap import *
from tkinter.messagebox import showinfo, showerror
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import Label
from tkinter.font import Font
from subprocess import Popen
from PIL import ImageTk, Image
from ctypes import windll
from json import loads, dump
from idlelib.percolator import Percolator
from idlelib.colorizer import ColorDelegator, color_config
from threading import RLock, Thread

windll.shcore.SetProcessDpiAwareness(True)


def PNGImage(file: str = ...):
    a = Image.open(file)
    return ImageTk.PhotoImage(image=a)


k = None
p = None
language = None


def initialize():
    global k, p, language
    try:
        with open("settings.json", "r", encoding="utf-8") as f:
            p = loads(f.read())
    except IOError:
        with open("settings.json", "w", encoding="utf-8") as f:
            p = {
                "info": {"PyToka_name": "PyToka v0.0.2-rc1", "language_name": "en_us", "pip_name": "pip"},
                "gui": {"window_size": "1280x768+100+50"},
                "run": {"run_command": "PyToka_console.exe", "python_prompt": "pykw"}
            }
            dump(p, f, ensure_ascii=False)

    with open("language.json", "r", encoding="utf-8") as f:
        language = loads(f.read())
    k = language[p["info"]["language_name"]]
    return p, k


k = initialize()
json_data = k[0]
my_language = k[1]


def _set_python(root, path):
    root.destroy()
    json_data["run"]["python_prompt"] = path
    with open("settings.json", "w") as f:
        dump(json_data, f, ensure_ascii=False)


class PyToka(Window):
    def __init__(self, string):
        self.myentry = None
        self.filename = None
        self.file = None
        self.thread_lock = RLock()
        self.txt = ""
        self.photo = None
        self.setpython = None
        self.pythonfile = None
        self.saved = False
        global json_data
        super().__init__(themename="yeti")
        self.i = None
        self.wm_geometry(json_data["gui"]["window_size"])
        self.wm_title("PyToka")
        self.wm_iconbitmap("PyToka.ico")
        self.scrollbar = Scrollbar(self)
        self.scrollbar.pack(fill=Y, side=RIGHT)
        self.scrollbar.configure(command=self.scroll)
        self.line_text = Text(self, width=7, height=1600, spacing3=6,
                              bg="#DCDCDC", bd=0, takefocus=0, state="disabled",
                              cursor="arrow", font=("Courier New", 11), spacing1=2, spacing2=7)
        self.line_text.pack(side="left", expand=NO)
        self.text = Text(self, height=114514, width=1919810, font=("Courier New", 11), spacing3=6, spacing1=2,
                         spacing2=7, wrap=NONE)
        self.text.pack(side="left", fill="both")
        self.text.bind("<Return>", self.enter)
        self.text.insert(END,
                         "#Define Function 'hello'\ndef hello(name):\n    print('Hello,{pyname}.'.format(pyname=name))\n\nhello('PyToka') #Print Hello,PyToka\n\n#You can write more code in there")
        self.text.configure(yscrollcommand=self.scrollbar.set)
        color_config(self.text)
        self.text.focus_set()
        self.menu = Menu(self, tearoff=False)
        self.file_menu = Menu(self.menu, tearoff=False)
        self.file_menu.add_command(label=string["gui_open_file"], command=lambda: self.OpenFile(string))
        self.file_menu.add_command(label=string["gui_save_file"],
                                   command=lambda: self.SaveFile(self.text.get(1.0, END), string))
        self.file_menu.add_command(label=string["gui_save_as_file"],
                                   command=lambda: self.SaveAsFile(self.text.get(1.0, END), string))
        self.file_menu.add_separator()
        self.file_menu.add_command(label=string["gui_exit_pytoka"],
                                   command=lambda: self.destroy())
        self.run_menu = Menu(self.menu, tearoff=False)
        self.run_menu.add_command(label=string["gui_run_python"],
                                  command=lambda: self.runcommand(self.text.get(1.0, END),
                                                                  json_data["run"]["python_prompt"]))
        self.run_menu.add_command(label=string["gui_run_and_save_python"],
                                  command=lambda: self.RunAndSave(self.text.get(1.0, END), string))
        self.setting_menu = Menu(self.menu, tearoff=False)
        self.setting_menu.add_cascade(label=string["gui_about"],
                                      command=lambda: self._window_about(string["window_about"]))
        self.setting_menu.add_cascade(label=string["gui_setting"],
                                      command=lambda: self._window_setting(string["window_setup"], string))
        self.info_menu = Menu(self.menu, tearoff=False)
        self.info_menu.add_command(label=string["gui_info_words"],
                                   command=lambda: showinfo(string["message_info_title"],
                                                            "{0} {1}{2} {3}KB".format(string["message_info_words"],
                                                                                      len(self.text.get(1.0, END)),
                                                                                      string["message_info_kilometers"],
                                                                                      int(len(self.text.get(1.0,
                                                                                                            END)) / 1024) + 1)))
        self.menu.add_cascade(label=string["gui_menu_file"], menu=self.file_menu)
        self.menu.add_cascade(label=string["gui_run_python_menu"], menu=self.run_menu)
        self.menu.add_cascade(label=string["gui_setting"], menu=self.setting_menu)
        self.menu.add_cascade(label=string["gui_info_menu"], menu=self.info_menu)
        Percolator(self.text).insertfilter(ColorDelegator())
        self.configure(menu=self.menu)
        self.line_text.bind("<MouseWheel>", self.wheel)
        self.text.bind("<MouseWheel>", self.wheel)
        self.text.bind("<Control-v>", lambda e: self.get_txt_thread())
        self.text.bind("<Control-V>", lambda e: self.get_txt_thread())
        self.text.bind("<Key>", lambda e: self.get_txt_thread())
        if json_data["run"]["python_prompt"] == "pykw":
            self.SetPython(string)
        self.show_line()
        self.get_txt_thread()

    def _window_setting(self, mystring, realstring):
        self.settings = Toplevel(self)
        self.settings.wm_title(mystring["title"])
        self.settings.wm_iconbitmap("PyToka.ico")
        self.settings.wm_geometry("640x480+100+50")
        self.settings.settings_notebook = Notebook(self.settings)
        self.settings.settings_language = Frame(self.settings.settings_notebook)
        self.settings.settings_language.pack()
        self.settings.settings_language_chinese = Button(self.settings.settings_language,
                                                         text=mystring["language_zh_cn"],
                                                         command=lambda: self._window_settings_edit_json_to_setup_some_value(
                                                             "info",
                                                             "language_name",
                                                             "zh_cn",
                                                             [realstring["message_info_title"],
                                                              mystring["message_info_restart"]]))
        self.settings.settings_language_chinese.pack(fill=X)
        self.settings.settings_language_english = Button(self.settings.settings_language,
                                                         text=mystring["language_en_us"],
                                                         command=lambda: self._window_settings_edit_json_to_setup_some_value(
                                                             "info",
                                                             "language_name",
                                                             "en_us",
                                                             [realstring["message_info_title"],
                                                              mystring["message_info_restart"]]))
        self.settings.settings_language_english.pack(fill=X)

        self.settings.settings_path = Frame(self.settings.settings_notebook)
        self.settings.settings_path.pack()
        self.settings.settings_path_entry = Entry(self.settings.settings_path)
        self.settings.settings_path_entry.pack(fill=X)
        self.settings.settings_path_done = Button(self.settings.settings_path, text=realstring["done"],
                                                  command=lambda: self._window_settings_edit_json_to_setup_some_value(
                                                      "run",
                                                      "python_prompt",
                                                      self.settings.settings_path_entry.get(),
                                                      [realstring["message_info_title"],
                                                       mystring["message_info_restart"]]
                                                  ))
        self.settings.settings_path_done.pack()
        self.settings.settings_notebook.pack(fill=BOTH, padx=5, pady=2, expand=True)
        self.settings.settings_notebook.add(self.settings.settings_language, text=mystring["language_notebook"])
        self.settings.settings_notebook.add(self.settings.settings_path, text=mystring["path_notebook"])
        self.settings.wm_resizable(0, 0)

    def _window_settings_edit_json_to_setup_some_value(self, name1, name2, newvalue, stringlist):
        global json_data
        self.settings.destroy()
        json_data[name1][name2] = newvalue
        with open("settings.json", "w+", encoding="utf-8") as f:
            dump(json_data, f, ensure_ascii=False)
        showinfo(title=stringlist[0], message=stringlist[1])

    def _window_about(self, mystring):
        self.aboutwindow = Toplevel(self)
        self.aboutwindow.wm_iconbitmap("PyToka.ico")
        self.aboutwindow.wm_title(mystring["about_title"])
        self.aboutwindow.image = PNGImage("PyToka.png")
        self.aboutwindow.aboutwindow_img = Label(self.aboutwindow, image=self.aboutwindow.image)
        self.aboutwindow.aboutwindow_img.pack()
        self.aboutwindow.aboutwindow_info = Label(self.aboutwindow,
                                                  text="PyToka {version}\nAuthors:{author1},{author2}\nLicense:{license}\nMade in China".format(
                                                      license=mystring["about_license"],
                                                      author1=mystring["about_author"][0],
                                                      author2=mystring["about_author"][1],
                                                      version=mystring["about_version"]))
        self.aboutwindow.aboutwindow_info.pack()
        self.aboutwindow.aboutwindow_font = Font(family="Segoe UI", underline=True)
        self.aboutwindow.aboutwindow_license = Label(self.aboutwindow, text="License...",
                                                     font=self.aboutwindow.aboutwindow_font, foreground="blue",
                                                     cursor="hand2")
        self.aboutwindow.aboutwindow_license.pack()
        self.aboutwindow.aboutwindow_license.bind("<Button-1>", lambda e: self._license())
        self.aboutwindow.wm_resizable(0, 0)

    def _license(self):
        self.license = Toplevel(self)
        self.license.wm_state("zoomed")
        self.license.wm_title("License")
        self.license.wm_iconbitmap("PyToka.ico")
        with open("LICENSE.txt", "r", encoding="utf-8") as f:
            self.mpl2 = f.read()
        self.license.text = Text(self.license, width=11451, height=19198)
        self.license.text.pack()
        self.license.text.insert(END, self.mpl2)
        self.license.text["state"] = DISABLED

    def enter(self, *args):
        self.get_txt_thread()
        self.i = 0
        a = self.text.index("insert")
        a = float(a)
        aa = int(a)
        b = self.text.get(float(aa), a).replace("\n", "")
        c = b
        if b[-1:] == ":" or b[-1:] == "[" or b[-1:] == "{" or b[-1:] == "(":
            i = 0
            while True:
                if b[:4] == "    ":
                    b = b[4:]
                    i += 1
                else:
                    break
            self.i = i + 1
        else:
            i = 0
            while True:
                if b[:4] == "    ":
                    b = b[4:]
                    i += 1
                else:
                    break
            self.i = i
            if c.strip() == "break" or c.strip() == "return" or c.strip() == "pass" or c.strip() == "continue" or c.strip() == "]" or c.strip() == "}" or c.strip() == "]":
                self.i -= 1
        self.text.insert("insert", "\n")
        for j in range(self.i):
            self.text.insert("insert", "    ")
        return "break"

    def SetPython(self, mystring):
        self.setpython = Toplevel()
        self.photo = PNGImage("PyToka.png")
        Label(self.setpython, image=self.photo, compound=TOP, text=mystring["set_python_path"]).pack()
        self.myentry = Entry(self.setpython)
        self.setpython.wm_resizable(False, False)
        self.setpython.wm_title(mystring["set_python_path"])
        self.setpython.wm_iconbitmap("PyToka.ico")
        self.myentry.pack(fill=X)
        self.setpython.protocol("WM_DELETE_WINDOW", self._none)
        Button(self.setpython, text=mystring["done"],
               command=lambda: _set_python(self.setpython, self.myentry.get())).pack()

    @staticmethod
    def _open_python(path):
        Popen(r"start {0} temp.py".format(path), shell=True)

    def _none(self):
        pass

    def OpenFile(self, mystring):
        self.filename = askopenfilename(filetypes=[("Python File", "*.py"), ("Python Stage Files", "*.pyw")],
                                        title=mystring["message_info_title"])
        if self.filename:
            self.pythonfile = self.filename
            self.wm_title("PyToka-{}".format(self.filename))
            self.text.delete(1.0, END)
            with open(r"{0}".format(self.filename), "r", encoding="utf-8") as f:
                self.file = f.read()
            self.text.insert(END, self.file)
            self.get_txt_thread()
        else:
            showerror(title=mystring["message_info_title"], message=mystring["message_warning_filewarning"])

    def wheel(self, event):
        self.line_text.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self.text.yview_scroll(int(-1 * (event.delta / 120)), "units")
        return "break"

    def scroll(self, *xy):
        self.line_text.yview(*xy)
        self.text.yview(*xy)

    def get_txt_thread(self):
        if self.pythonfile is not None:
            self.wm_title("PyToka-{}*".format(self.pythonfile))
        Thread(target=self.get_txt).start()

    def get_txt(self):
        self.thread_lock.acquire()
        if self.txt != self.text.get("1.0", "end")[:-1]:
            self.txt = self.text.get("1.0", "end")[:-1]
            self.show_line()
        else:
            self.thread_lock.release()

    def show_line(self):
        sb_pos = self.scrollbar.get()
        self.line_text.configure(state="normal")
        self.line_text.delete("1.0", "end")
        txt_arr = self.txt.split("\n")
        if len(txt_arr) == 1:
            self.line_text.insert("1.1", " 1")
        else:
            for i in range(1, len(txt_arr) + 1):
                self.line_text.insert("end", " " + str(i))
                if i != len(txt_arr):
                    self.line_text.insert("end", "\n")
        if len(sb_pos) == 4:
            self.line_text.yview_moveto(0.0)
        elif len(sb_pos) == 2:
            self.line_text.yview_moveto(sb_pos[0])
            self.text.yview_moveto(sb_pos[0])
        self.line_text.configure(state="disabled")
        try:
            self.thread_lock.release()
        except RuntimeError:
            pass

    def SaveAsFile(self, text, mystring):
        # Awwman
        self.saved = True
        self.wm_title("PyToka-{}".format(self.pythonfile))
        filename = asksaveasfilename(filetypes=[("Python File", "*.py"), ("Python Stage Files", "*.pyw")],
                                     title=mystring["message_info_title"])
        if filename:
            self.pythonfile = filename
            self.wm_title("PyToka-{}".format(self.pythonfile))
            with open(r"{}".format(filename), "w+", encoding="utf-8") as f:
                f.write(text)
        else:
            showerror(title=mystring["message_info_title"], message=mystring["message_warning_filewarning"])

    def SaveFile(self, text, mystring):
        # Awwman
        self.saved = True
        self.wm_title("PyToka-{}".format(self.pythonfile))
        if self.pythonfile is None:
            self.SaveAsFile(text, mystring)
        else:
            with open(r"{}".format(self.pythonfile), "w+", encoding="utf-8") as f:
                f.write(text)

    def runcommand(self, text, pypath):
        with open(r"PyRun.py", "w", encoding="utf-8") as f:
            f.write("from ctypes import OleDLL\nOleDLL('shcore').SetProcessDpiAwareness(1)\n{}".format(text))
        with open(r"start.bat", "w", encoding="utf-8") as f:
            f.write("@echo off\ntitle PyToka-Console\n{} PyRun.py\npause\nexit".format(pypath))
        Popen(r"start start.bat", shell=True)

    def RunAndSave(self, text, mystring):
        if self.pythonfile is None:
            self.saved = True
            self.wm_title("PyToka-{}".format(self.pythonfile))
            self.pythonfile = asksaveasfilename(filetypes=[("Python File", "*.py"), ("Python Stage Files", "*.pyw")],
                                                title=mystring["message_info_title"])
            if self.pythonfile:
                self.wm_title("PyToka-{}".format(self.pythonfile))
                with open(r"{}".format(self.pythonfile), "w+", encoding="utf-8") as f:
                    f.write(text)
                self.runcommand(text, json_data["run"]["python_prompt"])
            else:
                showerror(title=mystring["message_info_title"], message=mystring["message_warning_filewarning"])
        else:
            with open(r"{}".format(self.pythonfile), "w+", encoding="utf-8") as f:
                f.write(text)
            self.runcommand(text, json_data["run"]["python_prompt"])

    def _pip_installer(self, command, name):
        with open("start.bat", "w", encoding="utf-8") as f:
            f.write(
                "@echo off\ntitle PyToka-PIP\n{0} {1} {2}\npause\nexit".format(json_data["info"]["pip_name"], command,
                                                                               name))
        Popen("start start.bat", shell=True)


PyToka(my_language).mainloop()
