import tkinter as tk
from tkinter import ttk
from datetime import datetime
import json
import history_detail
import os

from util_balloon import MessageBoxAskQuestion, MessageBoxShowInfo

history_screen = None

def load_history_meta():
    try:
        with open('memory/history_meta.json', 'r', encoding='utf-8') as file:
            history_meta = json.load(file)
            
            if 'cur_conversation' not in history_meta:
                history_meta['cur_conversation'] = ''
                print('load_history: cur_conversation error')       
            if 'conversation_order' not in history_meta:
                history_meta['conversation_order'] = list()
                print('load_history: conversation_order error')
            if 'conversations' not in history_meta:
                history_meta['conversations'] = dict()
                print('load_history: conversations error')
            return history_meta
    except:
        # 파일이 없을 경우 기본값 설정
        history_meta = {
            'cur_conversation': '',
            'conversation_order': list(),
            'conversations': dict()
        }
        return history_meta

def save_history_meta(history_meta):
    # 폴더가 없으면 생성
    os.makedirs('memory', exist_ok=True)  
    with open('memory/history_meta.json', 'w', encoding='utf-8') as file:
        json.dump(history_meta, file, ensure_ascii=False, indent=4)
    print('save settings in memory/history_meta.json')

def open_history_screen(master):
    global history_screen
    if history_screen is None:
        history_screen = HistoryScreen(master)
    else:
        history_screen.lift()
                
class HistoryScreen(tk.Toplevel):
    def __init__(self, master):
        def on_window_close():
            # 종료전 쓰레기 정리
            global history_screen
            history_screen = None

            self.destroy()  
        super().__init__(master)
        self.title("History")
        self.protocol("WM_DELETE_WINDOW", lambda:on_window_close())
               
        # 기본 세팅
        self.loaded_history_meta = load_history_meta()
        
        # Current History Frame
        self.current_history_frame = tk.Frame(self, width=300, height=20)
        self.current_history_frame.pack(pady=10, fill="x")
        
        self.current_history_label = tk.Label(self.current_history_frame, text="Current History")
        self.current_history_label.pack(side=tk.LEFT, padx=5)
        
        def update_history_dropdown(event):
            self.loaded_history_meta['cur_conversation'] = self.history_dropdown.get()
            save_history_meta(self.loaded_history_meta)
            
        self.history_options = self.loaded_history_meta['conversation_order']
        self.history_var = tk.StringVar(value=self.loaded_history_meta['cur_conversation'])
        self.history_dropdown = ttk.Combobox(self.current_history_frame, textvariable=self.history_var)
        self.history_dropdown['values'] = self.history_options
        self.history_dropdown.pack(side=tk.LEFT)
        self.history_dropdown.bind("<<ComboboxSelected>>", update_history_dropdown)
        
        self.new_button = tk.Button(self.current_history_frame, text="New", command=self.create_new_history)
        self.new_button.pack(side=tk.LEFT, padx=(20,10))
        
        # History List Frame with Scrollbar
        self.history_list_frame = tk.Frame(self)
        self.history_list_frame.pack(pady=10, fill="both", expand=True)
        
        self.canvas = tk.Canvas(self.history_list_frame, height=200)
        self.scrollbar = tk.Scrollbar(self.history_list_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # order에 맞게 item 추가/표시
        self.history_order = self.loaded_history_meta['conversation_order']  # list
        self.history_items = self.loaded_history_meta['conversations']  # dict
        self.history_frames = []
        for history in self.history_order:
            if history in self.history_items:
                history_dict = self.history_items[history]
                if 'filename' in history_dict and os.path.isfile('./memory/'+history_dict['filename']):
                    self.add_history_item(history_dict)
                    
    def add_history_item(self, item):
        item_name = item['title']
        item_frame = tk.Frame(self.scrollable_frame, width=300)
        item_frame.pack(fill="x", pady=5)
        
        item_label = tk.Label(item_frame, text=item_name, anchor="w", justify="left")
        item_label.pack(side="left", padx=(5, 20), fill="x", expand=True)
        
        buttons_frame = tk.Frame(item_frame)
        buttons_frame.pack(side="right")
        
        delete_button = tk.Button(buttons_frame, text="Delete", command=lambda: self.delete_history_item(item, item_frame))
        delete_button.pack(side="right", padx=5)   
        
        modify_button = tk.Button(buttons_frame, text="Modify", command=lambda: self.modify_history_item(item, item_label))
        modify_button.pack(side="right", padx=5)
        
        detail_button = tk.Button(buttons_frame, text="Detail", command=lambda: self.open_history_detail(item))
        detail_button.pack(side="right", padx=5)
        
        self.history_frames.append(item_frame)
    
    def open_history_detail(self, item):
        # Placeholder function to open history detail
        print(f"Open details for {item['title']}")
        history_detail.open_history_detail_screen(self, item, None)

    def modify_history_item(self, item, item_label):
        modify_window = tk.Toplevel(self)
        modify_window.title("Modify History Item")
        
        title_frame = tk.Frame(modify_window)
        title_frame.pack(fill="x", padx=10, pady=5)
        
        title_label = tk.Label(title_frame, text="Modify Name")
        title_label.pack(side="left")
        
        title_entry = tk.Entry(title_frame)
        title_entry.insert(0, item_label.cget("text"))
        title_entry.pack(side="left", fill="x", expand=True, padx=10)
        
        button_frame = tk.Frame(modify_window)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        cancel_button = tk.Button(button_frame, text="Cancel", command=modify_window.destroy)
        cancel_button.pack(side="right")
        
        save_button = tk.Button(button_frame, text="Save", command=lambda: self.save_modified_name(item, item_label, title_entry, modify_window))
        save_button.pack(side="right", padx=5)
    
    def save_modified_name(self, item, item_label, title_entry, modify_window):
        item_name = item['title']
        new_name = title_entry.get()
        if new_name:
            if item_name in self.history_options:
                # json 갱신
                index = self.loaded_history_meta['conversation_order'].index(item_name)
                self.loaded_history_meta['conversation_order'][index] = new_name
                
                # 드롭다운 갱신
                self.history_options = self.loaded_history_meta['conversation_order']
                self.history_dropdown['values'] = self.history_options
                
                if item_name == self.loaded_history_meta['cur_conversation']:
                    self.loaded_history_meta['cur_conversation'] = new_name
                    self.history_var.set(new_name)
                    
                # 변경내역 save
                save_history_meta(self.loaded_history_meta)

            item_label.config(text=new_name)
        modify_window.destroy()

    def delete_history_item(self, item, item_frame):
        item_name = item['title']
        ask_question_box = MessageBoxAskQuestion(self, "Confirm", "Do you really want to delete it?")
        self.wait_window(ask_question_box)
        if ask_question_box.result:  
            if item_name in self.history_options:
                # 드롭다운 갱신
                self.history_options.remove(item_name)
                self.history_dropdown['values'] = self.history_options
            
                # json 갱신
                self.loaded_history_meta['conversation_order'] = self.history_options           
                if item_name == self.loaded_history_meta['cur_conversation']:
                    self.loaded_history_meta['cur_conversation'] = ''
                    self.history_var.set('')
                
                # 변경내역 save
                save_history_meta(self.loaded_history_meta)

            item_frame.destroy()
            self.history_frames.remove(item_frame)


    def create_new_history(self):
        ask_question_box = MessageBoxAskQuestion(self, "Confirm", "Do you want to start a new conversation?")
        self.wait_window(ask_question_box)
        if ask_question_box.result:   
            item = dict()
            
            new_item_name = datetime.now().strftime("%Y%m%d%H%M%S")
            item['title'] = new_item_name
            item['time'] = new_item_name
            item['filename'] = 'conversation_' + new_item_name + '.json'
            
            # 설정을 JSON 형식으로 저장
            os.makedirs('./memory', exist_ok=True)
            with open('memory/'+item['filename'], 'w', encoding='utf-8') as file:
                json.dump([], file, ensure_ascii=False, indent=4)

            # 변수 갱신 및 드롭다운 추가
            self.history_var.set(new_item_name) 
            self.history_options.append(new_item_name)
            self.history_dropdown['values'] = self.history_options 

            # json 갱신
            self.loaded_history_meta['conversation_order'] = self.history_options    
            self.loaded_history_meta['cur_conversation'] = new_item_name
            self.loaded_history_meta['conversations'][new_item_name] = item
                        
            # UI 반영
            self.add_history_item(item)
            
            # 변경내역 save
            save_history_meta(self.loaded_history_meta)
        
def main():
    root = tk.Tk()
    root.withdraw()
    open_history_screen(root)
    root.mainloop()

if __name__ == "__main__":
    main()
