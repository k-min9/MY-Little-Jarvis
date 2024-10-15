import tkinter as tk
from tkinter import filedialog
import json
import os
import pickle
import googletrans # 번역 관련

from util_ui import MessageBoxAskQuestion, MessageBoxShowInfo
import state
from messages import getMessage

history_detail_screen = None

def load_history_content(file_name):    
    if not os.path.exists(file_name):
        return []
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return []
    
def get_message(text, language, is_special=False):
    return getMessage(text, language, is_special)

def open_history_detail_screen(master, item, callback):
    global history_detail_screen
    if history_detail_screen is None:
        history_detail_screen = historyDetailScreen(master, item, callback)
    else:
        history_detail_screen.lift()   

class historyDetailScreen(tk.Toplevel):
    def __init__(self, master, item, callback):
        def on_window_close(callback):
            # 종료전 쓰레기 정리
            global history_detail_screen
            history_detail_screen = None
            
            # 체크박스 리스트 전달
            checked_titles = []
            for frame in self.frames:
                if self.checkbutton_dict[frame.winfo_children()[0]].get() == 1:  # Check if checkbox is checked
                    title_label = frame.winfo_children()[1]
                    checked_titles.append(title_label.cget("text"))
            
            # 콜백으로 변경 캐릭터 적용
            if callback:  # 콜백함수없을 경우(테스트 등) 오류
                callback(checked_titles)  # callback에 리스트 반환
            self.destroy()  
        
        super().__init__(master)
        self.title(item['title'])
        self.protocol("WM_DELETE_WINDOW", lambda:on_window_close(callback))
        
        self.language = state.get_g_language()
        self.translator = None
        try:
           self.translator = googletrans.Translator()
        except:
            pass
        
        self.item = item
        self.item_key = item['time']
        self.file_name = 'memory/' + item['filename']
        self.history_content_list = load_history_content(self.file_name)

        self.input_frame = tk.Frame(self)
        self.input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        
        self.scrollbar = tk.Scrollbar(self.input_frame, orient="vertical")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.input_canvas = tk.Canvas(self.input_frame, yscrollcommand=self.scrollbar.set)
        self.input_canvas.grid(row=0, column=0, sticky="news")
        self.scrollbar.config(command=self.input_canvas.yview)
        self.input_frame_container = tk.Frame(self.input_canvas)
        self.input_canvas.create_window((0, 0), window=self.input_frame_container, anchor="nw")
        self.input_frame_container.bind("<Configure>", self.on_frame_configure)

        # self.checkbutton_set = set(chekcklist)  # 캐릭터 리스트 읽기  체크된 리스트 읽기
        self.checkbutton_dict = dict()

        self.frames = []
        self.import_data_init(self.history_content_list)
        
        self.history_detail_dict = dict()
        self.init_history_detail_dict()

        self.control_frame = tk.Frame(self)
        self.control_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")
        
        self.add_btn = tk.Button(self.control_frame, text=get_message("Add", self.language), command=self.add_line_window)
        self.add_btn.grid(row=0, column=0, sticky="ew", pady=2)

        self.delete_btn = tk.Button(self.control_frame, text=get_message("Del", self.language), command=self.delete_line)
        self.delete_btn.grid(row=1, column=0, sticky="ew", pady=2)

        self.summary_btn = tk.Button(self.control_frame, text=get_message("Summary", self.language), command=self.summary_title)
        self.summary_btn.grid(row=1, column=0, sticky="ew", pady=2)

        # self.save_btn = tk.Button(self.control_frame, text="체크", command=self.get_checked_titles)
        # self.save_btn.grid(row=2, column=0, sticky="ew", pady=2)

        # self.import_btn = tk.Button(self.control_frame, text="Import", command=self.import_data)
        # self.import_btn.grid(row=3, column=0, sticky="ew", pady=2)

        # self.export_btn = tk.Button(self.control_frame, text="Export", command=self.export_data)
        # self.export_btn.grid(row=4, column=0, sticky="ew", pady=2)
                
        
    def on_frame_configure(self, event):
        self.input_canvas.configure(scrollregion=self.input_canvas.bbox("all"))

    def init_history_detail_dict(self):
        try:
            file_path = self.file_name
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            with open(file_path, 'r', encoding='utf-8') as file:
                self.history_detail_dict = json.load(file)
        except:
            pass
    
    def save_history_detail_dict(self, speaker_entry, content_text):
        speaker = speaker_entry.get()
        content = content_text.get("1.0", "end-1c")
        
        self.history_detail_dict[speaker] = content
        if not os.path.exists(os.path.dirname(self.file_name)):
            os.makedirs(os.path.dirname(self.file_name))
        with open(self.file_name, 'w', encoding='utf-8') as file:
            json.dump(self.history_detail_dict, file, indent=4)

    def add_line_window(self):
        def add_line_window_confirm(self, speaker_entry, content_text):
            if speaker_entry.get() in self.history_detail_dict:
                # $$ 표기용 화면으로 생성
                # print('이미 있는 history_detail입니다.\n',speaker_entry.get())
                pass
                return
            if not speaker_entry.get():
                # $$ 표기용 화면으로 생성
                print('No Speaker Founded')
                pass
                return
            new_frame = self.add_line()
            self.update_line(speaker_entry, content_text, new_frame)
            add_window.destroy()
        add_window = tk.Toplevel(self)
        add_window.title("Add history_detail")
        title_frame = tk.Frame(add_window)
        title_frame.pack(fill="x", padx=10, pady=5)
        title_label = tk.Label(title_frame, text="Speaker")
        title_label.pack(side="left")
        speaker_entry = tk.Entry(title_frame)
        speaker_entry.pack(side="left", padx=(0, 10))
        content_frame = tk.Frame(add_window)
        content_frame.pack(fill="x", padx=10, pady=5)
        content_label = tk.Label(content_frame, text="Content")
        content_label.pack(side="left")
        content_text = tk.Text(content_frame, height=5, width=30)
        content_text.pack(side="right")
        button_frame = tk.Frame(add_window)
        button_frame.pack(fill="x", padx=10, pady=5)
        cancel_button = tk.Button(button_frame, text="취소", command=add_window.destroy)
        cancel_button.pack(side="right") 
        confirm_button = tk.Button(button_frame, text="확인", command=lambda: add_line_window_confirm(self, speaker_entry, content_text))
        confirm_button.pack(side="right", padx=2)

    def add_line(self):
        new_frame = tk.Frame(self.input_frame_container)
        new_frame.grid(row=len(self.frames), column=0, sticky="new")#, pady=1)

        checkbox_var = tk.IntVar()
        checkbox = tk.Checkbutton(new_frame, variable=checkbox_var)
        self.checkbutton_dict[checkbox] = checkbox_var
        
        checkbox.grid(row=0, column=0, sticky="w")
        title_label = tk.Label(new_frame, text="Speaker", width=8, anchor="w", justify='left')
        title_label.grid(row=0, column=1, padx=(0, 10), sticky="w")
        content_label = tk.Label(new_frame, text="Message", width=20, anchor="w", justify='left')
        content_label.grid(row=0, column=2, padx=(0, 10), sticky="w")
        modify_button = tk.Button(new_frame, text=get_message("Edit", self.language), command=lambda: self.modify_line_window(new_frame, title_label, content_label))
        modify_button.grid(row=0, column=3, padx=(0, 10), sticky="w")
        delete_button = tk.Button(new_frame, text=get_message("Del", self.language), command=lambda: self.delete_specific_line(new_frame))
        delete_button.grid(row=0, column=4, sticky="w")

        self.frames.append(new_frame)
        return new_frame

    def delete_line(self):
        if self.frames:
            frame_to_delete = self.frames[-1]
            frame_to_delete.destroy()
            self.frames.pop()

    def delete_specific_line(self, frame):
        # dic 정리
        speaker = frame.winfo_children()[1].cget("text")
        if speaker in self.history_detail_dict:
            del self.history_detail_dict[speaker]
            file_path = "./memory/conversation_memory.json"
            if not os.path.exists(os.path.dirname(file_path)):
                os.makedirs(os.path.dirname(file_path))
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(self.history_detail_dict, file, indent=4)

        frame.destroy()
        self.frames.remove(frame)
        
    def summary_title(self):
        ask_question_box = MessageBoxAskQuestion(self, "Confirm", "Suggest title suggestions from conversation history.")
        self.wait_window(ask_question_box)
        if ask_question_box.result:  
            new_title = self.summary_title_stream()
            if new_title:
                # title 변경
                self.title(new_title)
                self.item['title'] = new_title
                
                # 파일 새로 열고 저장
                try:
                    with open('memory/history_meta.json', 'r', encoding='utf-8') as file:
                        history_meta = json.load(file)
                    history_meta['conversations'][self.item_key]['title'] = new_title
                    with open('memory/history_meta.json', 'w', encoding='utf-8') as file:
                        json.dump(history_meta, file, ensure_ascii=False, indent=4)    
                    print('change memory/history_meta.json')
                except:
                    pass
        
    def summary_title_stream(self):
        import ai_title
        reply = ''
        for j, reply in enumerate(ai_title.process_stream(None, 'm9dev', 'arona', True, False)):
            pass        
        title_infos = ai_title.get_title_infos(reply)
        
        def on_select(title):
            # 확인 메시지 박스 띄우기
            ask_question_box = MessageBoxAskQuestion(self, "Confirm", f"Do you want to select this title?\n\n{title}")
            self.wait_window(ask_question_box)
            if ask_question_box.result:  
                new_title[0] = title
                top.destroy()
            
        def on_close():
            top.destroy()
        
        # 새로운 Toplevel 창 생성
        top = tk.Toplevel(self)
        top.title("Select Title")
        new_title = [None]
 
        for title_info in title_infos:
            title = title_info['title']            
            title_reason = ''
            if 'reason' in title_info:
                title_reason = title_info['reason']
                
            # google trans 번역으로 title 및 reason 번역
            if self.translator:
                try:
                    title = self.translator.translate(title, dest=self.language).text  
                    title_reason = self.translator.translate(title_reason, dest=self.language).text  
                except:
                    pass

            frame = tk.Frame(top)
            frame.pack(fill="x", padx=10, pady=5)
            
            frame_label = tk.Frame(frame)
            frame_label.pack(side="top", anchor="w")

            # 제목 라벨
            title_label = tk.Label(frame_label, text=title, font=("Arial", 12, "bold"))
            title_label.pack(side="top", anchor="w")

            # 이유 라벨
            reason_label = tk.Label(frame_label, text=title_reason, font=("Arial", 10))
            reason_label.pack(side="top", anchor="w", padx=(20, 0))

            # 선택 버튼
            select_button = tk.Button(frame, text="Select", command=lambda t=title: on_select(t))
            select_button.pack(side="right", padx=5)

        # Toplevel 창이 닫힐 때 빈 문자열을 반환하도록 함
        top.protocol("WM_DELETE_WINDOW", on_close)

        # 창 실행 대기
        top.wait_window()
        return new_title[0]
        
    # def get_checked_titles(self):
    #     checked_titles = []
    #     for frame in self.frames:
    #         if self.checkbutton_dict[frame.winfo_children()[0]].get() == 1:  # Check if checkbox is checked
    #             title_label = frame.winfo_children()[1]
    #             checked_titles.append(title_label.cget("text"))
    #     return checked_titles
        
    def import_data_init(self, datas):
        # file_path = "./memory/conversation_memoryAA.json"
        # if not os.path.exists(os.path.dirname(file_path)):
        #     os.makedirs(os.path.dirname(file_path))
        # with open(file_path, 'r', encoding='utf-8') as file:
        #     datas = json.load(file)
        for data in datas:
            speaker = data['speaker']
            message = data['message_trans']
            self.add_line()
            self.frames[-1].winfo_children()[1].config(text=speaker)
            message = message[:20] + "..." if len(message) > 20 else message  # 20글자까지 표기
            message = message.replace('\n',' ')
            self.frames[-1].winfo_children()[2].config(text=message)  # 체크 이미 있는 경우 해버리기
            # if speaker in self.checkbutton_set:
            #     self.checkbutton_dict[self.frames[-1].winfo_children()[0]].set(1) 
                
    # # dict일때의 로직 / 차후 수정
    # def import_data(self):
    #     initial_dir = "./local"
    #     if not os.path.exists(initial_dir):
    #         os.makedirs(os.path.dirname(initial_dir))    
    #     file_path = filedialog.askopenfilename(initialdir=initial_dir, initialfile='history_detail.json', speaker="Select file", filetypes=(("JSON files", "*.json"), ("All files", "*.*")))
    #     if file_path:
    #         with open(file_path, 'r', encoding='utf-8') as file:
    #             data = json.load(file)
    #         for speaker, content in data.items():
    #             self.add_line()
    #             self.frames[-1].winfo_children()[1].config(text=speaker)
    #             content = content.replace[:20] + "..." if len(content) > 20 else content  # 20글자까지 표기
    #             content = content.replace('\n',' ')
    #             self.frames[-1].winfo_children()[2].config(text=content)

    # def export_data(self):
    #     data = {}
    #     for frame in self.frames:
    #         speaker = frame.winfo_children()[1].cget("text")
    #         content = frame.winfo_children()[2].cget("text")
    #         data[speaker] = content
    #     file_path = "./memory/conversation_memory.json"
    #     if not os.path.exists(os.path.dirname(file_path)):
    #         os.makedirs(os.path.dirname(file_path))
    #     with open(file_path, 'w', encoding='utf-8') as file:
    #         json.dump(data, file, indent=4)
            
    def modify_line_window(self, frame, title_label, content_label):
        def modify_line_window_confirm(self, speaker_entry, content_text, frame):
            self.update_line(speaker_entry, content_text, frame)
            modify_window.destroy()
        speaker = title_label.cget("text")
        content = ''
        self.init_history_detail_dict()
        if speaker in self.history_detail_dict:
            content = self.history_detail_dict[speaker]
        modify_window = tk.Toplevel(self)
        modify_window.title("Modify Line")
        title_frame = tk.Frame(modify_window)
        title_frame.pack(fill="x", padx=10, pady=5)
        title_label = tk.Label(title_frame, text="Speaker")
        title_label.pack(side="left")
        speaker_entry = tk.Entry(title_frame)
        speaker_entry.pack(side="left", padx=(0, 10))
        speaker_entry.insert(0, speaker)
        content_frame = tk.Frame(modify_window)
        content_frame.pack(fill="x", padx=10, pady=5)
        content_label = tk.Label(content_frame, text="Content")
        content_label.pack(side="left")
        content_text = tk.Text(content_frame, height=5, width=30)
        content_text.insert("1.0", content)
        content_text.pack(side="right")
        button_frame = tk.Frame(modify_window)
        button_frame.pack(fill="x", padx=10, pady=5)
        cancel_button = tk.Button(button_frame, text="취소", command=modify_window.destroy)
        cancel_button.pack(side="right")
        confirm_button = tk.Button(button_frame, text="확인", command=lambda: modify_line_window_confirm(self, speaker_entry, content_text, frame))
        confirm_button.pack(side="right",padx=2)


    def update_line(self, speaker_entry, content_text, frame):
        speaker = speaker_entry.get()
        content = content_text.get("1.0", "end-1c")[:20] + "..." if len(content_text.get("1.0", "end-1c")) > 20 else content_text.get("1.0", "end-1c")  # 20글자까지 표기
        content = content.replace('\n',' ')
        for widget in frame.winfo_children():
            widget.destroy()
        checkbox_var = tk.IntVar()
        checkbox = tk.Checkbutton(frame, variable=checkbox_var)
        self.checkbutton_dict[checkbox] = checkbox_var
        checkbox.grid(row=0, column=0, sticky="w")
        title_label = tk.Label(frame, text=speaker, width=8, anchor="w", justify='left')
        title_label.grid(row=0, column=1, padx=(0, 10), sticky="w")
        content_label = tk.Label(frame, text=content, width=20, anchor="w", justify='left')
        content_label.grid(row=0, column=2, padx=(0, 10), sticky="w")
        modify_button = tk.Button(frame, text=get_message("Edit", self.language), command=lambda: self.modify_line_window(frame, title_label, content_label))
        modify_button.grid(row=0, column=3, padx=(0, 10), sticky="w")
        delete_button = tk.Button(frame, text=get_message("Del", self.language), command=lambda: self.delete_specific_line(frame))
        delete_button.grid(row=0, column=4, sticky="w")
        # history_detail json 저장
        self.save_history_detail_dict(speaker_entry, content_text)

    
def main():
    root = tk.Tk()
    open_history_detail_screen(root, None)
    root.mainloop()

if __name__ == "__main__":
    main()
