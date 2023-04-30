import tkinter
import tkinter.filedialog
import time
import os.path
import os
import datetime
import subprocess
import threading

version = 'v1.0.1 от 16.01.2023 by Dragmor'

class MainWindow():
    def __init__(self):
        self.fields = [] #список полей задач
        self.started = False #флаг, что поток запущен
        self.create_window()
        self.create_ui_elements()
        if self.try_load() == False: #загрузка состояния
	        self.add_field()
        self.window.mainloop()
        
    def create_window(self):
        self.window = tkinter.Tk()
        self.window.title("расписание выполнения задач by Dragmor")
        self.window.wm_iconbitmap("icon.ico")
        # self.window.configure(background='white') #цвет фона окна
        self.fields_frame = tkinter.Frame(self.window) #фрейм полей задач
        
    def create_ui_elements(self):
        #меню
        self.menu = tkinter.Menu(self.window)
        self.cascade_menu = tkinter.Menu(self.menu, tearoff=0)

        self.menu.add_cascade(label='меню', menu=self.cascade_menu)
        self.cascade_menu.add_command(label='Сохранить задачи',
                 command=self.ask_save)
        self.cascade_menu.add_command(label='Загрузить задачи',
                 command=self.ask_load)
        self.cascade_menu.add_separator()
        self.cascade_menu.add_command(label='О программе',
                 command=self.about)
        self.cascade_menu.add_separator()
        self.cascade_menu.add_command(label='Выйти',
                 command=self.exit)

        self.window.config(menu=self.menu)


        #кнопка для добавления нового поля задачи
        self.button_plus = tkinter.Button(text="добавить задачу", bg='lightblue', command=self.add_field, font='bold')
        self.button_plus.pack(fill='both') #кнопка добавления новой задачи
        self.fields_frame.pack() #фрейм задач

        self.button_start = tkinter.Button(text="старт", bg='lightgreen', command=self.start, font='bold')
        self.button_start.pack(side="bottom", fill='both') #кнопка добавления новой задачи

    def try_load(self):
        '''метод пытается загрузить прошлое состояние задач'''
        if os.path.exists('state.sav'):
            self.load_state('state.sav')
            return True
        return False #если не удалось загрузить состояние

    def ask_save(self):
        filename = tkinter.filedialog.asksaveasfilename(defaultextension='sav',
         initialfile='state.sav')
        if filename == '':
            return
        else:
            self.save_state(filename)

    def save_state(self, filename):
        '''метод сохраняет состояние программы'''
        file = open(filename, 'w')
        for obj in self.fields:
            if obj.rb_values.get() == 0:
                file.write('f')
                file.write('\n%s'%obj.choosed_file) #file
            else:
                file.write('c') #command
                if obj.command_enter.get() == '':
                    file.write('\nNone')
                else:
                    file.write('\n%s'%obj.command_enter.get())
            file.write('\n%s:%s'%(obj.hours_enter.get(), obj.minutes_enter.get()))
            file.write('\n\n')
        file.close()

    def ask_load(self):
        filename = tkinter.filedialog.askopenfilename()
        if filename == '':
            return
        else:
            self.load_state(filename)

    def load_state(self, filename):
        '''загрузить состояние'''
        #выполняю парсинг сохранения
        file = open(filename, 'r')
        saved_state = file.read()
        file.close()
        
        saved_state = saved_state.split('\n\n')
        fields = []
        for field in saved_state:
            if field != '':
                fields.append(field.split('\n'))

        for obj in self.fields:
            self.fields = []
            obj.frame.destroy()

        for field in fields:
            self.add_field() #добавляю поле
            if field[0] == 'f':
                self.fields[-1].rb_values.set(0)
                
                if field[1] == 'None':
                    self.fields[-1].button_file_chooser.configure(text="указать файл")
                else:
                    self.fields[-1].select_file(field[1])
            else:
                self.fields[-1].rb_values.set(1)
                self.fields[-1].button_file_chooser.configure(state='disabled')
                self.fields[-1].command_enter.configure(state='normal')
                if field[1] != 'None':
                    command = tkinter.StringVar()
                    command.set(field[1])
                    self.fields[-1].command_enter.configure(textvariable=command)
            time = field[2].split(':')
            hours = tkinter.StringVar()
            if time[0] != '':
                hours.set(time[0])
            else:
                hours.set('0')
            minutes = tkinter.StringVar()
            if time[1] != '':
                minutes.set(time[1])
            else:
                minutes.set('0')
            self.fields[-1].hours_enter.configure(textvariable=hours)
            self.fields[-1].minutes_enter.configure(textvariable=minutes)

    def about(self):
        '''о программе'''
        self.about_window = tkinter.Tk()
        self.about_window.resizable(width=False, height=False)
        # self.about_window.geometry('250x250')
        self.about_window.title("О программе")
        self.about_window.wm_iconbitmap("icon.ico")
        text = '\nПрограмма служит для автоматизации выполнения задач\n'
        text += 'Разработчик: Миролюбов Евгений\n'
        text += 'Программа распространяется бесплатно\n'
        text += 'Fervuld@gmail.com'

        self.about_text = tkinter.Label(self.about_window, text=text, font='calibri')
        self.about_text.pack(side='top')

        self.version = tkinter.Label(self.about_window, text=version)
        self.version.pack(side='bottom')
        self.about_window.mainloop()

    def exit(self):
        '''выход из приложения, созранение состояния'''
        self.save_state('state.sav')
        exit()

    def add_field(self):
        '''метод добавляет поле для создания новой задачи'''
        self.fields.append(FieldFrame(self.fields_frame, len(self.fields)))
        self.fields[-1].button_delete_field = tkinter.Button(self.fields[-1].frame, text="удалить задачу",
        bg='pink',
        command=(lambda self=self, frame_id=self.fields[-1].id: self.delete_field(frame_id)), width=15)
        self.fields[-1].button_delete_field.pack(side="left")
        self.fields[-1].frame.pack()

    def delete_field(self, frame_id):
        '''метод удаляет поле задачи'''
        for obj in self.fields:
            if obj.id == frame_id:
                obj.frame.destroy()
                self.fields.remove(obj)
                break
        for new_id in range(0, len(self.fields)):
            self.fields[new_id].id = new_id
            self.fields[new_id].refresh_colors()
            self.fields[new_id].field_id.configure(text="[%s]"%new_id)
            self.fields[new_id].button_delete_field.configure(command=(lambda self=self, frame_id=new_id: self.delete_field(frame_id)))

    def start(self):
        if self.started == False:
            self.started = True
            self.button_start.configure(text='пауза', bg='lightyellow')
            self.thread = threading.Thread(target=self.timer_thread)
            self.thread.daemon = True
            self.thread.start()
        else:
            self.started = False
            self.button_start.configure(text='старт', bg='lightgreen')


    def timer_thread(self):
        '''поток таймера'''
        while self.started:
            for obj in self.fields:
                if obj.refresh_time() == True:
                    obj.check_start()
            time.sleep(0.3)


class FieldFrame():
    '''класс поля задачи'''
    def __init__(self, main_frame, frame_id):
        self.id = frame_id
        self.choosed_file = None #указанный для запуска файл
        self.executed = False #флаг, что выполнение уже было
        self.main_frame = main_frame
        self.frame = tkinter.Frame(self.main_frame)
        self.create_ui_elements()
        self.refresh_colors()
        self.change_exec_mode()

    def create_ui_elements(self):
        self.rb_values = tkinter.IntVar()
        self.rb_values.set(0)
        #создаю элементы управления
        self.field_id = tkinter.Label(self.frame, text="[%s]"%self.id, width=3, font='system', fg='blue')
        self.text_exec = tkinter.Label(self.frame, text="запустить ", font='system')
        self.file_selector = tkinter.Radiobutton(self.frame, text='файл', value=0, 
            var=self.rb_values, command=self.change_exec_mode, font='arial') #radiobutton
        self.command_selector = tkinter.Radiobutton(self.frame, text='команду', value=1, 
            var=self.rb_values, command=self.change_exec_mode, font='arial') #radiobutton
        self.button_file_chooser = tkinter.Button(self.frame, text="указать файл", command=self.ask_file, width=20)
        self.command_enter = tkinter.Entry(self.frame, borderwidth=5, width=20)
        self.text_in_time = tkinter.Label(self.frame, text="в ", font='system')
        hours_values = list(range(0, 24))
        minutes_values = list(range(0, 60))
        self.hours_enter = tkinter.Spinbox(self.frame, values=hours_values, width=2)
        self.minutes_enter = tkinter.Spinbox(self.frame, values=minutes_values, width=2)
        self.timer = tkinter.Label(self.frame, text="до запуска:", width=20, font='calibri', fg='blue')
        self.execute_now_button = tkinter.Button(self.frame, text="выполнить сейчас", command=self.start_now, bg='lightgreen', width=15)

        #размещаю элементы упарвления
        self.field_id.pack(side="left")
        self.text_exec.pack(side="left")
        self.file_selector.pack(side="left")
        self.command_selector.pack(side="left")
        self.button_file_chooser.pack(side="left")
        self.command_enter.pack(side="left")
        self.text_in_time.pack(side="left")
        self.hours_enter.pack(side="left")
        self.minutes_enter.pack(side="left")
        self.timer.pack(side="left")
        self.execute_now_button.pack(side="left")

    def check_start(self):
        '''метод проверяет, была ли уже выполнена задача'''
        if self.executed == False:
            self.executed = True
            self.start_now()
    
    def refresh_colors(self):
        if self.id%2 == 0:
            self.bg_color = 'white'
        else:
            self.bg_color = 'lightgray'
        self.frame.configure(background=self.bg_color)
        self.field_id.configure(bg=self.bg_color)
        self.text_exec.configure(bg=self.bg_color)
        self.file_selector.configure(bg=self.bg_color)
        self.command_selector.configure(bg=self.bg_color)
        self.timer.configure(bg=self.bg_color)

    def start_now(self):
        '''метод запускает выполнение задачи'''
        if self.rb_values.get() == 0 and self.choosed_file != None: #запускаю файл
            os.startfile(self.choosed_file)
            # subprocess.getoutput('explorer "%s"' %self.choosed_file)
        else:
            subprocess.getoutput('"%s"' %self.command_enter.get())

    def refresh_time(self):
        '''метод обновляет текущее время до выполнения задачи,
        и возвращает True, если настало время выполнения, иначе False'''
        if self.hours_enter.get() == '' or self.minutes_enter.get() == '':
            return False
        exec_time = datetime.timedelta(
         hours=int(self.hours_enter.get()),
         minutes=int(self.minutes_enter.get()),
         seconds=0) 
        now_time = datetime.timedelta(
         hours=time.localtime().tm_hour,
         minutes= time.localtime().tm_min,
         seconds=time.localtime().tm_sec)
        #разница во времени
        delta = str(exec_time-now_time).split()[-1] 
        #вывожу время до запуска
        self.timer.configure(text='до запуска: %s' %(delta))
        #сброс флага, что задача была выполнена
        if exec_time-now_time < datetime.timedelta(hours=0, minutes=0, seconds=0) and self.executed == True:
            self.executed = False
        #проверка, подошло-ли время запуска
        if exec_time-now_time == datetime.timedelta(hours=0, minutes=0, seconds=0):
            return True
        else:
            return False

    def ask_file(self):
        '''метод для выбора файла для выполнения'''
        file = tkinter.filedialog.askopenfilename()
        self.select_file(file)

    def select_file(self, file):
        
        if file != '':
            self.choosed_file = os.path.normpath(file)
            file = os.path.basename(self.choosed_file)
            #меняю надпись на кнопке
            self.button_file_chooser.configure(text="../%s" %file)
        else:
            self.choosed_file = None
            self.button_file_chooser.configure(text="указать файл")

    def change_exec_mode(self):
        if self.rb_values.get() == 0:
            self.command_enter.configure(state='disabled')
            self.button_file_chooser.configure(state='normal')
        else:
            self.button_file_chooser.configure(state='disabled')
            self.command_enter.configure(state='normal')
            self.command_enter.focus()


if __name__ == "__main__":
    app = MainWindow()
    