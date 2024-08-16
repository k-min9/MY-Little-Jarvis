import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageGrab
import os
import time
import threading
from tkinterdnd2 import TkinterDnD, DND_FILES
import shutil
from screeninfo import get_monitors
import state

class ScreenshotApp:
    def __init__(self, root, menu=None):
        self.root = root
        # self.root.title("Screenshot App")

        self.screenshot_rect = None
        self.continuous_save_running = False
        self.continuous_save_thread = None
        self.current_monitor = None  # 현재 모니터를 저장하기 위한 변수 추가
        self.dnd_toplevel = None  # 이미지 입력용

        if menu:
            self.context_menu = None
        else:
            # 내부 사용
            self.context_menu = tk.Menu(self.root, tearoff=0)
        
            self.context_menu.add_command(label="Set Screenshot Area", command=self.set_screenshot_area)
            self.context_menu.add_command(label="Save as PNG", command=self.save_screenshot)
            self.context_menu.add_command(label="Save as PNG(Chk)", command=self.save_as_png)
            self.context_menu.add_command(label="Show Screenshot Rect", command=self.show_screenshot_rect)
            self.context_menu.add_command(label="Start Continuous Save", command=self.toggle_continuous_save)
            self.context_menu.add_command(label="Get External PNG", command=self.create_dnd_toplevel)

            self.root.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        if self.context_menu:
            self.context_menu.post(event.x_root, event.y_root)

    def set_screenshot_area(self):
        # Get the monitor information where the root window is located
        root_x = self.root.winfo_rootx()
        root_y = self.root.winfo_rooty()

        for monitor in get_monitors():
            if monitor.x <= root_x < monitor.x + monitor.width and monitor.y <= root_y < monitor.y + monitor.height:
                self.current_monitor = monitor
                screen_x = monitor.x
                screen_y = monitor.y
                screen_width = monitor.width
                screen_height = monitor.height
                break

        # Create a new Toplevel window covering the correct monitor
        self.top = tk.Toplevel(self.root)
        self.top.geometry(f"{screen_width}x{screen_height}+{screen_x}+{screen_y}")
        self.top.overrideredirect(True)
        self.top.attributes("-alpha", 0.3)
        self.top.configure(bg='white')

        self.canvas = tk.Canvas(self.top, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.start_x = None
        self.start_y = None
        self.rect_id = None
        
        state.set_is_screenshot_area_selecting(True)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_move_press(self, event):
        cur_x, cur_y = (event.x, event.y)
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, cur_x, cur_y, outline='red', width=2)

    def on_button_release(self, event):
        end_x, end_y = (event.x, event.y)
        self.start_x, self.start_y, end_x, end_y = min(self.start_x, end_x), min(self.start_y, end_y), max(self.start_x, end_x), max(self.start_y, end_y)
        self.screenshot_rect = (self.start_x, self.start_y, end_x, end_y)
        self.top.destroy()
        
        state.set_is_screenshot_area_selecting(False)  # state 갱신

    def save_as_png(self):
        if self.screenshot_rect:
            file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                     filetypes=[("PNG files", "*.png")])
            if file_path:
                self.save_screenshot(file_path)
        else:
            messagebox.showwarning("Warning", "Please set the screenshot area first.")

    def copy_to_clipboard(self):
        if self.screenshot_rect:
            x1, y1, x2, y2 = self.screenshot_rect
            screen_x = self.current_monitor.x
            screen_y = self.current_monitor.y
            image = ImageGrab.grab(bbox=(x1 + screen_x, y1 + screen_y, x2 + screen_x, y2 + screen_y), all_screens=True)
            self.root.clipboard_clear()
            self.root.clipboard_append(image)
        else:
            messagebox.showwarning("Warning", "Please set the screenshot area first.")

    def save_screenshot(self, file_path='./image/screenshot.png'):
        if not self.screenshot_rect:
            messagebox.showwarning("Warning", "Please set the screenshot area first.")
            return
        if not os.path.exists("./image"):
            os.makedirs("./image")
        x1, y1, x2, y2 = self.screenshot_rect
        screen_x = self.current_monitor.x
        screen_y = self.current_monitor.y
        image = ImageGrab.grab(bbox=(x1 + screen_x, y1 + screen_y, x2 + screen_x, y2 + screen_y), all_screens=True)
        image.save(file_path)

    def toggle_continuous_save(self):
        if self.continuous_save_running:
            self.continuous_save_running = False
            self.screenshot_rect = None
            self.continuous_save_thread.join()  # Ensure the thread has finished
            if self.context_menu:
                self.context_menu.entryconfig("Stop Continuous Save", label="Start Continuous Save")
        else:
            if not self.screenshot_rect:
                if state.get_is_screenshot_area_selecting():
                    messagebox.showwarning("Warning", "Selecting screenshot area...")
                else:
                    messagebox.showwarning("Warning", "Please set the screenshot area first.")
                    self.set_screenshot_area()
                return 'No'
            else:
                self.active_continuous_save_thread()
            
    def active_continuous_save_thread(self):
        if self.continuous_save_running:  # 기작동중일 경우 return
            return
        self.continuous_save_running = True
        if self.context_menu:
            self.context_menu.entryconfig("Start Continuous Save", label="Stop Continuous Save")
        self.continuous_save_thread = threading.Thread(target=self.continuous_save)
        self.continuous_save_thread.start()

    def continuous_save(self):
        count = 1
        while self.continuous_save_running:
            self.save_screenshot()
            count += 1
            time.sleep(1)

    def show_screenshot_rect(self):
        if self.screenshot_rect:
            monitor = self.current_monitor
            screen_x = monitor.x
            screen_y = monitor.y
            screen_width = monitor.width
            screen_height = monitor.height

            # Create a new Toplevel window covering the correct monitor
            self.top = tk.Toplevel(self.root)
            self.top.geometry(f"{screen_width}x{screen_height}+{screen_x}+{screen_y}")
            self.top.overrideredirect(True)
            self.top.attributes("-alpha", 0.3)
            self.top.configure(bg='white')

            self.canvas = tk.Canvas(self.top)
            self.canvas.pack(fill=tk.BOTH, expand=tk.YES)

            x1, y1, x2, y2 = self.screenshot_rect
            self.canvas.create_rectangle(x1, y1, x2, y2, outline='red', width=2)
            self.top.after(2000, self.top.destroy)  # Show the rectangle for 2 seconds then destroy the window
        else:
            messagebox.showwarning("Warning", "No screenshot area set.")

    def create_dnd_toplevel(self):
        if self.dnd_toplevel:  # 있을 경우 기존것 focus
            self.dnd_toplevel.focus()
            return      
        self.dnd_toplevel = TkinterDnD.Tk()
        self.dnd_toplevel.title("Drop PNG Here")
        self.dnd_toplevel.geometry("300x200")
        self.dnd_toplevel.attributes("-topmost", 100)
        # self.dnd_toplevel.overrideredirect(True)

        self.dnd_label = tk.Label(self.dnd_toplevel, text="Drag and drop a PNG file here")
        self.dnd_label.pack(expand=True, fill=tk.BOTH)

        self.dnd_toplevel.drop_target_register(DND_FILES)
        self.dnd_toplevel.dnd_bind('<<Drop>>', self.on_drop)
        
        self.img_label = None
        self.confirm_label = None
        self.cancel_label = None
        
        self.create_img_label()

        # Toplevel 윈도우 닫을 때 호출되는 이벤트 바인딩
        self.dnd_toplevel.protocol("WM_DELETE_WINDOW", self.on_exit)

    def on_drop(self, event):
        file_path = event.data.strip('{}')
        is_temp_file = False
        if not file_path.lower().endswith('.png'): # 우선 png 변환을 시도
            try:
                # 입력 파일 열기
                with Image.open(file_path) as img:
                    file_path = os.path.splitext(file_path)[0] + '.png'
                    
                    # 이미지 저장 (PNG 형식)
                    img.save(file_path, 'PNG')
                    is_temp_file = True
            except:
                tk.messagebox.showerror("Error", "Please drop a PNG file")
                return

        save_path = './image/external.png'
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        shutil.copy(file_path, save_path)
        
        self.create_img_label()
        
        # png 변환타입은 여기서 삭제
        if is_temp_file:
            if os.path.exists(file_path):
                os.remove(file_path)
    
    def create_img_label(self):
        if os.path.exists('./image/external.png'):
            img = Image.open('./image/external.png')
            img = img.resize((260, 160))  # 이미지 크기 조정
            img_tk = ImageTk.PhotoImage(img, master=self.dnd_label)  # tkinter 이미지 실종 방지용

            if hasattr(self, 'img_label') and self.img_label:
                self.img_label.destroy()
            if hasattr(self, 'confirm_label') and self.confirm_label:
                self.confirm_label.destroy()
            if hasattr(self, 'cancel_label') and self.cancel_label:
                self.cancel_label.destroy()

            self.img_label = tk.Label(self.dnd_toplevel, image=img_tk)
            self.img_label.image = img_tk
            self.img_label.pack(expand=True, fill=tk.BOTH)
            
            # 확인 및 취소 버튼 역할을 하는 Label 추가
            self.confirm_label = tk.Label(self.dnd_toplevel, text="Confirm", fg="green", cursor="hand2")
            self.confirm_label.pack(side=tk.LEFT, expand=True)
            self.confirm_label.bind("<Button-1>", self.on_confirm)

            self.cancel_label = tk.Label(self.dnd_toplevel, text="Delete", fg="red", cursor="hand2")
            self.cancel_label.pack(side=tk.RIGHT, expand=True)
            self.cancel_label.bind("<Button-1>", self.on_cancel)
      
    def on_confirm(self, event):
        self.dnd_toplevel.destroy()
        self.dnd_toplevel = None
        
    def on_cancel(self, event=None):
        if os.path.exists('./image/external.png'):
            os.remove('./image/external.png')
        self.create_img_label()
        
    def on_exit(self, event=None):
        self.dnd_toplevel.destroy() 
        self.dnd_toplevel = None

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenshotApp(root)
    root.geometry("800x600")
    root.mainloop()
