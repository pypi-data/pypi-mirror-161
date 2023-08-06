from tkinter import messagebox
import pyautogui
import time
import webbrowser
import cv2
import requests
from tkinter import *
import threading
from pynput.keyboard import Controller
import pywhatkit
import os
import win32api, win32con
import keyboard
import pyttsx3
from googletrans import Translator
from PIL import Image
import speech_recognition as sr
import numpy as np
import pandas as pd
import csv
from sklearn.tree import DecisionTreeClassifier




class ap:
    class steve:
        class steve:
            class steve:
                class steve:
                    class steve:
                        class steve:
                            class steve:
                                class steve:
                                    class steve:
                                        class steve:
                                            class steve:
                                                class steve:
                                                    class steve:
                                                        class steve:
                                                            class steve:
                                                                class steve:
                                                                    class steve:
                                                                        class steve:
                                                                            class steve:
                                                                                class steve:
                                                                                    class steve:
                                                                                        class steve:
                                                                                            class steve:
                                                                                                class steve:
                                                                                                    class steve:
                                                                                                        class steve:
                                                                                                            class steve:
                                                                                                                class steve:
                                                                                                                    class steve:
                                                                                                                        class steve:
                                                                                                                            class steve:
                                                                                                                                class steve:
                                                                                                                                    class steve:
                                                                                                                                        class steve:
                                                                                                                                            class steve:
                                                                                                                                                class steve:
                                                                                                                                                    class steve:
                                                                                                                                                        class steve:
                                                                                                                                                            class steve:
                                                                                                                                                                class steve:
                                                                                                                                                                    class steve:
                                                                                                                                                                        class steve:
                                                                                                                                                                            class steve:
                                                                                                                                                                                class steve:
                                                                                                                                                                                    class steve:
                                                                                                                                                                                        class steve:
                                                                                                                                                                                            class steve:
                                                                                                                                                                                                class steve:
                                                                                                                                                                                                    class steve:
                                                                                                                                                                                                        class steve:
                                                                                                                                                                                                            class steve:
                                                                                                                                                                                                                class steve:
                                                                                                                                                                                                                    class steve:
                                                                                                                                                                                                                        class steve:
                                                                                                                                                                                                                            class steve:
                                                                                                                                                                                                                                class steve:
                                                                                                                                                                                                                                    class steve:
                                                                                                                                                                                                                                        class steve:
                                                                                                                                                                                                                                            class steve:
                                                                                                                                                                                                                                                class steve:
                                                                                                                                                                                                                                                    class steve:
                                                                                                                                                                                                                                                        class steve:
                                                                                                                                                                                                                                                            class steve:
                                                                                                                                                                                                                                                                class steve:
                                                                                                                                                                                                                                                                    class steve:
                                                                                                                                                                                                                                                                        class steve:
                                                                                                                                                                                                                                                                            class steve:
                                                                                                                                                                                                                                                                                class steve:
                                                                                                                                                                                                                                                                                    class steve:
                                                                                                                                                                                                                                                                                        class steve:
                                                                                                                                                                                                                                                                                            class steve:
                                                                                                                                                                                                                                                                                                class steve:
                                                                                                                                                                                                                                                                                                    class steve:
                                                                                                                                                                                                                                                                                                        class steve:
                                                                                                                                                                                                                                                                                                            class steve:
                                                                                                                                                                                                                                                                                                                class steve:
                                                                                                                                                                                                                                                                                                                    class steve:
                                                                                                                                                                                                                                                                                                                        class steve:
                                                                                                                                                                                                                                                                                                                            class steve:
                                                                                                                                                                                                                                                                                                                                class steve:
                                                                                                                                                                                                                                                                                                                                    def steve1():
                                                                                                                                                                                                                                                                                                                                        def robotic_speech(text, gender=0):
                                                                                                                                                                                                                                                                                                                                            engine = pyttsx3.init()
                                                                                                                                                                                                                                                                                                                                            voices = engine.getProperty('voices')
                                                                                                                                                                                                                                                                                                                                            engine.setProperty('voice', voices[gender].id)
                                                                                                                                                                                                                                                                                                                                            engine.say(text)
                                                                                                                                                                                                                                                                                                                                            engine.runAndWait()

                                                                                                                                                                                                                                                                                                                                        robotic_speech('We are the many steves')
                                                                                                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                                                        def steve2():
                                                                                                                                                                                                                                                                                                                                            while True:
                                                                                                                                                                                                                                                                                                                                                robotic_speech('Steve')
                                                                                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                                                                        t = threading.Thread(target=steve2)
                                                                                                                                                                                                                                                                                                                                        t.start()
                                                                                                                                                                                                                                                                                                                                        

    class alerts:
        def warning(title, text):
            return messagebox.showwarning(title, text)

        def info(title, text):
            messagebox.showinfo(title, text)

        def error(title, text):
            return messagebox.showerror(title, text)

        def ask_ok_cancel(title, text):
            return messagebox.askokcancel(title, text)

        def ask_yes_no(title, text):
            return messagebox.askyesno(title, text)

        def ask_question(title, text):
            return messagebox.askquestion(title, text)

        def ask_retry_cancel(title, text):
            return messagebox.askretrycancel(title, text)

        def ask_yes_no_cancel(title, text):
            return messagebox.askyesnocancel(title, text)

        

        

    def list_screen_size():
        return pyautogui.size()

    def calculator(problem):
        return eval(problem)

    def translate(text, target):
        translator = Translator()
        new_text, origin = translator.translate(text=text, dest=target).text, translator.translate(text=text, dest=target).origin, translator.translate(text=text, dest=target)
        return new_text, origin

    class images:
        def show_image(window_name, picture):
            pic = cv2.imread(picture)
            cv2.imshow(window_name, pic)
            cv2.waitKey(1)

        

        def load_image(image):
            return cv2.imread(image)

        x, y = pyautogui.size()

        def screenshot(region=(0,0, x, y)):
            return pyautogui.screenshot(region=region)

        def save_image(image, image_name, file_type, load_image):
            if load_image == False:
                image.save(f'{image_name}.{file_type}')
            elif load_image == True:
                cv2.imwrite(f'{image_name}.{file_type}', image)




    def robotic_speech(text, gender=0):

        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[gender].id)
        engine.say(text)
        engine.runAndWait()

    def listen_for_speech():
        while True:
            try:
                with sr.Microphone() as source:
                    r = sr.Recognizer()
                    text = r.listen(source)
                    text = r.recognize_google(text)
                    if text:
                        return text
            except:
                pass

    def list_dir(directory):
        for (name, dirs, files) in os.walk(directory):
            return name, dirs, files

    def thread(funtion, args=None):
        t = threading.Thread(target=funtion, args=args)
        t.daemon = True
        t.start()

    def wait(delay):
        time.sleep(delay)

    def search_youtube(name):
        webbrowser.open(pywhatkit.playonyt(name))

    def get_site_content(site):
        return requests.get(site).content

    def get_site(site):
        return requests.get(site)

    class ai:
        def read_csv(file):
            return pd.read_csv(file)
        def write_row_to_csv(file_name, content):
            with open(file_name, 'w') as f:
                writer = csv.writer(f)
                writer.writerow(content)

        def write_multiple_rows_to_csv(file_name,content):
            with open(file_name, 'w') as f:
                writer = csv.writer(f)
                for i in range(len(content)):
                    writer.writerow(content[i])
        
        def predict(csv_file, known_columns):
            model = DecisionTreeClassifier()
            return model.predict(known_columns)

        
                    
    class bot:
        def hold_key(key, delay=0, stop_key='q'):
            if delay > 0:

                keyboard.press(key)
                while keyboard.is_pressed(stop_key) == False:
                    pass
                keyboard.release(key)

            else:
                keyboard.press(key)
                time.sleep(delay)
                keyboard.release(key)

        def macro(delay,x='',y='', image='', amount=0, stop_key='q'):
            def click():
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
                time.sleep(0.01)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
            if x and y:
                pyautogui.moveTo(x,y)
                if amount != 0:
                    for i in range(amount):
                        click()
                        time.sleep(delay)
                        if keyboard.is_pressed(stop_key):
                            break
                else:
                    while keyboard.is_pressed(stop_key) == False:
                        click()
                        time.sleep(delay)
            elif image:
                location = pyautogui.locateOnScreen(image)
                pyautogui.moveTo(location[0],location[1])
                if amount != 0:
                    for i in range(amount):
                        click()
                        time.sleep(delay)
                        if keyboard.is_pressed(stop_key):
                            break
                else:
                    while keyboard.is_pressed(stop_key) == False:
                        click()
                        time.sleep(delay)
            else:
                if amount != 0:
                    for i in range(amount):
                        click()
                        time.sleep(delay)
                        if keyboard.is_pressed(stop_key):
                            break
                else:
                    while keyboard.is_pressed(stop_key) == False:
                        click()
                        time.sleep(delay)
                    

        def current_position():
            pyautogui.displayMousePosition()

        def position():
            return pyautogui.position()

        def open_website(website):
            webbrowser.open(website)
        global keyboard1
        keyboard1 = Controller()
        def left_click(x, y):
            pyautogui.leftClick(x,y)

        def type(text, delay):
            for char in str(text):
                keyboard1.press(char)
                time.sleep(delay)

        def press(key):
            keyboard1.press(key)

        def move(x, y):
            pyautogui.move(x, y)

        def moveTo(x, y):
            pyautogui.moveTo(x, y)

        def scroll(amount):
            pyautogui.scroll(amount)

    class window:

        def __init__(self, frame,title='AP WINDOW', icon=None):
            
            frame.iconbitmap(icon)
            frame.title(title)
            frame.geometry('500x500')

        def create():

            root = Tk()
            return root
            

        def geometry(x, y, frame):
            frame.geometry(f'{x}x{y}')

        def unknown():
            pass
        def button(frame, text='', command=unknown, x=0, y=0, font=('Helvetica', 20)):
            btn = Button(master=frame, text=text, command=command, font=font)
            btn.place(x, y)
            frame.update()
        def label(frame, text='', x=0, y=0, font=('Helvetica', 20)):
            lbl = Label(frame, text=text, font=font)
            lbl.place(x=x, y=y)
            frame.update()
        def entry(frame, width=5, font=('Helvetica', 20),  x=0, y=0):
            
            btn = Button(frame, width=width, font=font)
            btn.place(x=x, y=y)
            frame.update()

        def frame(frame, location=[0,0], size=[100,100]):
            thing = Frame(frame, width=size[0], height=size[1])
            thing.place(x=location[0], y=location[1])

        def clear(frame):
            for widget in frame.winfo_children():
                widget.destroy()

        def loop(frame):
            frame.mainloop()



#ap.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve.steve1()