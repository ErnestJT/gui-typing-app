import tkinter as tk
from random import choices
from keyboard import is_modifier, hook, unhook_all
from keyboard._keyboard_event import KeyboardEvent
from keyboard._winkeyboard import official_virtual_keys
from pygetwindow import getActiveWindow
from tkinter import messagebox

KEYBOARD_FIRST_ROW = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p']
KEYBOARD_SECOND_ROW = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l']
KEYBOARD_THIRD_ROW = ['z', 'x', 'c', 'v', 'b', 'n', 'm']


class TypingApp:
    def __init__(self) -> None:
        
        self.root = tk.Tk()
        self.root.geometry('600x500')
        self.root.resizable(False,False)
        self.root.title('Typing Speed Test')
        self.root.config(padx=30, pady=30)
        
        self.__game_started = False
        
        self.generated_text: str = ""
        self.typed_text: str = ""
        
        self.text_widget: tk.Text
        self.timer_label: tk.Label
        self.current_position = 0
        
        self.characters_typed = 0
        
        self.__set_up_game()
        
        self.root.mainloop()
    
    def __set_up_game(self) -> None:
        self.__destroy_widgets()
        
        self.characters_typed = 0
        self.current_position = 0
        
        self.text_widget = tk.Text(self.root, height = 8, font = ('Helvetica', 16, 'bold'))
        self.text_widget.tag_config('incorrect_key', background = 'red', foreground = 'white')
        self.text_widget.tag_config('correct_key', background = 'green', foreground = 'white')
        self.text_widget.bind("<ButtonPress-1>", lambda e: "break")
        self.text_widget.pack(side = 'top', fill = 'x', pady = (0, 20))
        self.text_widget.config(state = "disabled")
        
        self.__set_up_keyboard()
        self.__add_more_words()
        
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(side = 'bottom', fill = 'both')
        
        start_button = tk.Button(bottom_frame, text = 'S  T  A  R  T', command = self.__start_game,
                                borderwidth = 1, bg = '#0cc0df',
                                font = ('Helvetica', 12, 'bold'))
        start_button.pack(fill = 'none')
        
        self.timer_label = tk.Label(bottom_frame, text ='Timer: 60')
        self.timer_label.pack() 
        
    def __show_results(self):
        self.__reset_game()
        
        try:
            with open('high_score.txt') as file:
                scores = file.read()
                scores = scores.split(',')
                
                high_score_wpm, high_score_cps = int(scores[0]), int(scores[1])
        except (FileNotFoundError, ValueError, IndexError) as e:
            print(e)
            high_score_wpm, high_score_cps = 60, 8
        
        corrected_wpm = (self.characters_typed // 5) * (60 // 60)
        corrected_cps = self.characters_typed // 60
        
        #I do not need to check for CPS, as CPS increases with WPM
        if corrected_wpm > high_score_wpm:
            high_score_wpm = corrected_wpm
            high_score_cps = corrected_cps
            
            try:
                with open('high_score.txt', mode = 'w') as file:
                    file.write(f'%s, %s' % (high_score_wpm, high_score_cps))
            except PermissionError:
                messagebox.showwarning('Could not save high scores to file.')
            except FileNotFoundError:
                messagebox.showwarning('"high_score.txt" cannot be found.')
    
        if corrected_wpm > 100:
            compliment_text = "Superb!"
        elif corrected_wpm > 80:
            compliment_text = "Amazing!"
        elif corrected_wpm > 60:
            compliment_text = "Nice!"
        elif corrected_wpm > 40:
            compliment_text = "Above average!"
        else:
            compliment_text = "You tried your best!"
        
        high_score_text = f"""High Score:
  {high_score_wpm} WPM and {high_score_cps} CPS """
        
        header_rectangle = tk.Label(self.root, text = 'FINAL RESULTS', bg = 'gray', font = ('Helvetica', 51, 'bold'), fg = 'white')
        header_rectangle.grid(column = 0, row = 0, columnspan = 2, pady = (0, 60))
        
        wpm_label = tk.Label(self.root, text = f'WPM: {corrected_wpm:.0f}', bg = 'gray', fg = 'white', font = ('Helvetica', 15, 'normal'))
        wpm_label.grid(column = 0, row = 1, sticky = 'NESW', ipadx = 20, ipady = 20)
        
        cps_label = tk.Label(self.root, text = f'CPS: {corrected_cps:.0f}', bg = 'gray', fg = 'white', font = ('Helvetica', 15, 'normal'))
        cps_label.grid(column = 0, row = 2, sticky = 'NESW', ipadx = 20, ipady = 20)
        
        restart_button = tk.Button(self.root, text = 'Restart', command = self.__set_up_game, bg = '#0cc0df', font = ('Helvetica', 20, 'bold'))
        restart_button.grid(column = 0, row = 3, sticky = 'NESW', pady = 50)
        
        high_score_label = tk.Label(self.root, text = high_score_text, bg = 'light gray', font = ('Helvetica', 20, 'bold'))
        high_score_label.config(anchor =  'center')
        high_score_label.grid(column = 1, row = 1, rowspan = 2, sticky = 'NESW')
        
        compliment_label = tk.Label(self.root, text = compliment_text, bg = 'light gray', 
                                    font = ('Helvetica', 20, 'bold'))
        compliment_label.grid(column = 1, row = 3, sticky = 'NESW', pady = 50)
        
        
        
        
    def __set_up_keyboard(self) -> None:
        first_keyboard_frame = tk.Frame(self.root)
        first_keyboard_frame.pack(side = 'top')
        
        second_keyboard_frame = tk.Frame(self.root)
        second_keyboard_frame.pack(side = 'top')
        
        third_keyboard_frame = tk.Frame(self.root)
        third_keyboard_frame.pack(side = 'top')
        
        for letter in KEYBOARD_FIRST_ROW:
            keyboard_key = tk.Button(first_keyboard_frame,text = letter.upper(), height = 2, width = 5)
            keyboard_key.pack(side = 'left', anchor = 'nw', padx = 5, pady = 5)
            
            keyboard_key.bind('<Button>', lambda event: self.__insert_key(
                KeyboardEvent('down', 
                            scan_code = next((k for k in official_virtual_keys if official_virtual_keys[k][0] == event.widget.cget('text').lower()))
                            , name = event.widget.cget('text').lower())
            ))
            
        for letter in KEYBOARD_SECOND_ROW:
            keyboard_key = tk.Button(second_keyboard_frame,text = letter.upper(), height = 2, width = 5)
            keyboard_key.pack(side = 'left',anchor = 'nw', padx = 5, pady = 5)
            
            keyboard_key.bind('<Button>', lambda event: self.__insert_key(
                KeyboardEvent('down', 
                            scan_code = next((k for k in official_virtual_keys if official_virtual_keys[k][0] == event.widget.cget('text').lower()))
                            , name = event.widget.cget('text').lower())
            ))

        for letter in KEYBOARD_THIRD_ROW:
            keyboard_key = tk.Button(third_keyboard_frame,text = letter.upper(), height = 2, width = 5)
            keyboard_key.pack(side = 'left',anchor = 'nw', padx = 5, pady = (5,10))
            
            keyboard_key.bind('<Button>', lambda event: self.__insert_key(
                KeyboardEvent('down', 
                            scan_code = next((k for k in official_virtual_keys if official_virtual_keys[k][0] == event.widget.cget('text').lower()))
                            , name = event.widget.cget('text').lower())
            ))
        hook(self.__insert_key)

    def __add_more_words(self):
        try:
            with open('common_words.txt') as word_file:
                words = word_file.readlines()
            words_generated = " ".join([word.strip() for word in choices(words, k = 140)])
            
            #Checks if player is currently in the game
            if self.current_position > 0:
                self.generated_text += " "
            self.generated_text += words_generated
            
        except FileNotFoundError:
            messagebox.showerror('Could not find "common_words.txt". Make sure the file is there!')
            return
        
        self.text_widget.config(state = "normal")
        self.text_widget.insert(tk.END, words_generated)
        self.text_widget.config(state = 'disabled')
    
    def __start_game(self):
        if not self.__game_started:
            self.__game_started = True
            self.__start_timer(60)

    
    def __insert_key(self, key: KeyboardEvent) -> None:
        active_window = getActiveWindow()
        
        if not self.__game_started:
            return
        
        #Checks if you are currently using the game
        if active_window is None or active_window.title != self.root.title():
            return
    
        #Checks if the key is in the alphabet, a modifier (shift, ctrl) and if it is pressed
        if key.name is None or key.event_type == 'up' or not key.name.isalpha() or is_modifier(key.name):
            return
        
        
        #Key.name's value is "space" when you enter a space
        key_entered = key.name.replace('space',' ')
        
        self.text_widget.config(state = 'normal')
        
        
        if key.name == 'backspace':
            if self.current_position <= 0: return
            self.text_widget.see(f"1.{self.current_position - 1}")

            #Checks if you erase a correct character
            if self.typed_text[self.current_position - 1] == self.generated_text[self.current_position - 1]:
                self.characters_typed -= 1
            
            self.text_widget.replace(index1 = f"1.{self.current_position - 1}", index2 = f"1.{self.current_position:.0f}", chars = self.generated_text[self.current_position-1])
            self.current_position -= 1
            
            self.typed_text = self.typed_text[:-1]
            self.text_widget.config(state = 'disabled')
            
            return
        
        self.typed_text += key_entered
        
        #Colors the letters if they're correct or incorrect
        if self.generated_text[self.current_position] == key_entered:
            self.text_widget.replace(f"1.{self.current_position}", 
                                    f"1.{self.current_position + 1}", 
                                    self.generated_text[self.current_position], 
                                    'correct_key')
            self.characters_typed += 1
        else:
            self.text_widget.replace(f"1.{self.current_position}",
                                    f"1.{self.current_position + 1}", 
                                    self.generated_text[self.current_position], 
                                    'incorrect_key')
            
        self.current_position += 1
        self.text_widget.see(f"1.{self.current_position + 360}")
        
        if self.current_position % 200 == 0:
            self.__add_more_words()
        
        self.text_widget.config(state = 'disabled')
    
    def __start_timer(self, count):
        timer_id = self.root.after(1000, self.__start_timer, count - 1)
        self.timer_label.configure(text = f'Timer: {count}')
        
        if count == 0:
            self.root.after_cancel(timer_id)
            self.__show_results()
            return
        
    def __destroy_widgets(self):
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def __reset_game(self):
        self.__game_started = False
        self.generated_text = ""
        
        for widget in self.root.winfo_children():
            widget.destroy()
        
        unhook_all()

