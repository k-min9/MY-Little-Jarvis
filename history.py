import tkinter as tk
from tkinter import ttk
from datetime import datetime
import json
import history_detail
import os
import googletrans

from util_ui import MessageBoxAskQuestion, MessageBoxShowInfo
import state
from messages import getMessage

history_screen = None

def get_message(text, language, is_special=False):
    return getMessage(text, language, is_special)

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
        self.language = state.get_g_language()
        self.translator = None
        try:
           self.translator = googletrans.Translator()
        except:
            pass
        
        # Current History Frame
        self.current_history_frame = tk.Frame(self, width=300, height=20)
        self.current_history_frame.pack(pady=10, fill="x")
        
        self.current_history_label = tk.Label(self.current_history_frame, text=get_message("Current Chat", self.language))
        self.current_history_label.pack(side=tk.LEFT, padx=5)
        
        def update_history_dropdown(event):
            self.loaded_history_meta['cur_conversation'] = self.history_dropdown.get()
            save_history_meta(self.loaded_history_meta)
            
        self.history_options = list()  # dropdown option : 이름으로
        for conversation in self.loaded_history_meta['conversation_order']:
            self.history_options.append(self.loaded_history_meta['conversations'][conversation]['title'])              
        self.history_var = tk.StringVar(value=self.loaded_history_meta['cur_conversation'])
        self.history_dropdown = ttk.Combobox(self.current_history_frame, textvariable=self.history_var, state="readonly")
        self.history_dropdown['values'] = self.history_options
        self.history_dropdown.pack(side=tk.LEFT)
        self.history_dropdown.bind("<<ComboboxSelected>>", update_history_dropdown)
        
        self.new_button = tk.Button(self.current_history_frame, text=get_message("New Chat", self.language), command=self.create_new_history)
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
        
        learning_button = tk.Button(buttons_frame, text=get_message("AI learning", self.language), command=lambda: self.learning_history_item(item, item_frame))
        learning_button.pack(side="right", padx=5)   
        
        delete_button = tk.Button(buttons_frame, text=get_message("Delete", self.language), command=lambda: self.delete_history_item(item, item_frame))
        delete_button.pack(side="right", padx=5)   
        
        modify_button = tk.Button(buttons_frame, text=get_message("Modify", self.language), command=lambda: self.modify_history_item(item, item_label))
        modify_button.pack(side="right", padx=5)
        
        detail_button = tk.Button(buttons_frame, text=get_message("Detail", self.language), command=lambda: self.open_history_detail(item))
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

    def learning_history_item(self, item, item_frame):
        ask_question_box = MessageBoxAskQuestion(self, "Confirm", "Analyze the information to learn from the conversation history.")
        self.wait_window(ask_question_box)
        if ask_question_box.result:  
            new_learning = self.summary_stream()
            print('learning', new_learning)
            if new_learning:
                pass
                # # title 변경
                # self.title(new_title)
                # self.item['title'] = new_title
                
                # # 파일 새로 열고 저장
                # try:
                #     with open('memory/history_meta.json', 'r', encoding='utf-8') as file:
                #         history_meta = json.load(file)
                #     history_meta['conversations'][self.item_key]['title'] = new_title
                #     with open('memory/history_meta.json', 'w', encoding='utf-8') as file:
                #         json.dump(history_meta, file, ensure_ascii=False, indent=4)    
                #     print('change memory/history_meta.json')
                # except:
                #     pass
    
    def summary_stream(self):
        import ai_summary
        reply = ''
        for j, reply in enumerate(ai_summary.process_stream(None, 'm9dev', 'arona', True, False)):
            pass        
        trait_infos = ai_summary.get_trait_infos(reply)

        # 새로운 Toplevel 창 생성
        top = tk.Toplevel(self)
        top.title("Select Learning")
        top.geometry('700x400')

        # Canvas와 Scrollbar를 포함하는 Frame 생성
        canvas_frame = tk.Frame(top)
        canvas_frame.pack(fill="both", expand=True)

        # Canvas 생성
        canvas = tk.Canvas(canvas_frame)
        canvas.pack(side="left", fill="both", expand=True)

        # Scrollbar 생성 및 Canvas에 연결
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Frame을 Canvas에 넣기
        inner_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=inner_frame, anchor="nw")

        # 선택된 항목을 저장할 리스트
        selected_traits = []

        # Frame 안에 trait 정보와 체크박스 추가
        for trait_info in trait_infos:
            trait_type = trait_info['type']
            trait = trait_info['trait']
            trait_reason = trait_info.get('reason', '')

            # google trans 번역으로 title 및 reason 번역
            trait_type_trans = trait_type
            trait_trans = trait
            trait_reason_trans = trait_reason
            if self.translator:
                try:
                    # 이 부분은 번역 과정에서 문자열 치환을 처리하는 부분입니다.
                    trait_trans = trait_trans.replace('{char}', 'char').replace('{Char}', 'char').replace('char', '{char}')
                    trait_trans = trait_trans.replace('{user}', 'user').replace('{User}', 'user').replace('user', '{user}')
                    trait_trans = self.translator.translate(trait_trans, dest=self.language).text  
                    
                    trait_reason_trans = trait_reason_trans.replace('{char}', 'char').replace('{Char}', 'char').replace('char', '{char}')
                    trait_reason_trans = trait_reason_trans.replace('{user}', 'user').replace('{User}', 'user').replace('user', '{user}')
                    trait_reason_trans = self.translator.translate(trait_reason_trans, dest=self.language).text  
                except Exception as e:
                    print(f"Translation error: {e}")

            # 개별 Frame 생성
            frame = tk.Frame(inner_frame)
            frame.pack(fill="x", padx=10, pady=5)

            # 체크박스 생성
            var = tk.IntVar()
            check_button = tk.Checkbutton(frame, variable=var)
            check_button.pack(side="left")

            # trait 제목 라벨
            title_label = tk.Label(frame, text=trait_type_trans + " : " + trait_trans, font=("Arial", 12, "bold"))
            title_label.pack(side="top", anchor="w")

            # trait 이유 라벨
            reason_label = tk.Label(frame, text=trait_reason_trans, font=("Arial", 10))
            reason_label.pack(side="top", anchor="w", padx=(20, 0))

            # 선택된 trait을 저장하기 위해 trait_info와 var를 묶어서 추가
            selected_traits.append((trait_info, var))

        # Canvas 크기 조정
        inner_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        # 학습 버튼 생성
        learn_button = tk.Button(top, text="학습", command=lambda: on_learn())
        learn_button.pack(side="right", padx=10, pady=10)

        def on_learn():
            # 학습 버튼 클릭 시 선택된 trait 정보를 리스트로 반환
            selected = [trait_info for trait_info, var in selected_traits if var.get() == 1]
            print("Selected traits for learning:", selected)
            top.destroy()
            self.selected_traits = selected

        def on_close():
            top.destroy()

        # Toplevel 창이 닫힐 때 빈 리스트를 반환하도록 함
        top.protocol("WM_DELETE_WINDOW", on_close)

        # 창 실행 대기
        top.wait_window()
        return getattr(self, 'selected_traits', [])


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
