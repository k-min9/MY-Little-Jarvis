import tkinter as tk
from PIL import Image, ImageTk
import threading

import time
from messages import getMessage
from util_loader import load_settings

loading_message_box = None

def get_message(text, is_special=False):
    loaded_settings = load_settings()
    
    return getMessage(text, loaded_settings['setting_language'], is_special)

# master위에 tip 메시지를 getMessages
class HoverTip:
    def __init__(self, widget, tip_message, **kwargs):
        self.widget = widget
        self.tip_message = tip_message
        self.tip_window = None

        self.widget.bind("<Enter>", self.show_tip)
        self.widget.bind("<Leave>", self.hide_tip)
        self.widget.bind("<Motion>", self.follow_mouse)

    def show_tip(self, event):
        if self.tip_window or not self.tip_message:
            return

        self.tip_window = tk.Toplevel(self.widget)
        self.tip_window.wm_overrideredirect(True)
        self.tip_window.attributes("-topmost", 1)


        label = tk.Label(self.tip_window, text=get_message(self.tip_message), bg="yellow", justify='left')
        label.pack()
        
        self.follow_mouse(event)

    def follow_mouse(self, event):
        if self.tip_window:
            x = event.x_root + 10
            y = event.y_root - 10
            self.tip_window.geometry(f"+{x}+{y}")

    def hide_tip(self, event):
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

# 이펙터
class Effecter(tk.Toplevel):
    def __init__(self, root, images=None, duration=0.2, center=None, **kwargs):
        super().__init__(**kwargs)
        
        self.root = root
        
        self.attributes('-topmost', 99)
        self.wm_attributes('-transparentcolor', '#f0f0f0')
        self.overrideredirect(True)
        
        self.images = images
        self.duration = duration
        self.current_index = 0

        self.label = tk.Label(self)
        self.label.pack()

        self.after(0, self.show_next_image)

        self.center = center
        if center:
            self.geometry(f"+{center[0]}+{center[1]}")
        else: # 없으면 root 중심으로 전개 (나중에 늘어나면 center, origin 추가.)
            x = int(self.root.winfo_x())# + root.winfo_width()/2)
            y = int(self.root.winfo_y())# + root.winfo_height()/2)
            self.geometry(f"+{x}+{y}")

    def show_next_image(self):
        if self.current_index < len(self.images):
            image = self.images[self.current_index]
            self.label.configure(image=image)
            self.current_index += 1
            self.after(int(self.duration * 1000), self.show_next_image)
        else:
            self.destroy()

# 질문 상자
class MessageBoxAskQuestion(tk.Toplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        
        # 번역
        title = get_message(title)
        message = get_message(message)
            
        global loading_message_box
        if loading_message_box:
            loading_message_box.destroy()
        loading_message_box = self
        
        self.title(title) 
        self.geometry(f"300x100+{parent.winfo_x() + 100}+{parent.winfo_y() + 100}")
        self.attributes("-topmost", 98)
        self.result = None

        label = tk.Label(self, text=message)
        label.pack(padx=20, pady=10)

        yes_button = tk.Button(self, text=get_message('Yes'), command=self.on_yes, width=12)
        yes_button.pack(side="left", padx=30)

        no_button = tk.Button(self, text=get_message("No"), command=self.on_no, width=12)
        no_button.pack(side="right", padx=30)

    def on_yes(self):
        global loading_message_box
        loading_message_box = None
        self.result = True
        self.destroy()

    def on_no(self):
        global loading_message_box
        loading_message_box = None
        self.result = False
        self.destroy()

# 안내 상자
class MessageBoxShowInfo(tk.Toplevel):
    def __init__(self, parent, title, message):
        super().__init__(parent)
        
        # 번역
        title = get_message(title)
        message = get_message(message)
        
        self.title(title)
        self.geometry(f"300x100+{parent.winfo_x() + 100}+{parent.winfo_y() + 100}")
        self.attributes("-topmost", 100)
         
        global loading_message_box
        if loading_message_box:
            loading_message_box.destroy()
        loading_message_box = self

        label = tk.Label(self, text=message, width=999, wraplength=280)
        label.pack(padx=10, pady=10)
        new_height = label.winfo_reqheight() + 60
        self.geometry(f"300x{new_height}")

        ok_button = tk.Button(self, text="OK", command=self.on_ok, width=20)
        ok_button.pack()

    def on_ok(self):
        global loading_message_box
        loading_message_box = None
        self.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    
    def on_right_click(event):
        # 1초마다 아직도 메뉴가 열려있는지 확인 (Unmap은 unpost등의 명시적 함수에만 쓰이고, Tkinter의 메뉴자동숨김내장함수를 감지할 수 없음)
        def check_menu_visibility():
            global is_waiting
            if not menu.winfo_ismapped():
                is_waiting = False
            else:
                root.after(1000, check_menu_visibility)
        global is_waiting
        is_waiting = True
        menu.post(event.x_root, event.y_root)
        check_menu_visibility()
    
    def test_ask():
        ask_question_box = MessageBoxAskQuestion(root, "Confirm", "YES / NO")
        root.wait_window(ask_question_box)
        if ask_question_box.result:   
            print('yes')
        else:
            print('no')

    def test_show():
        MessageBoxShowInfo(root, "Error", "key [ENTER] is not allowed.")

    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Ask", command=test_ask)
    menu.add_command(label="Show", command=test_show)
    
    root.bind("<Button-3>", on_right_click)


    root.mainloop()
    
    

    


