import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

proper_nouns_screen = None

CONFIG_PATH = './config/proper_nouns.json'

# 고유명사 데이터를 로드하는 함수
def load_proper_nouns():   
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w', encoding='utf-8') as file:
            json.dump([], file)
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
        return json.load(file)

# 고유명사 데이터를 저장하는 함수
def save_proper_nouns(data):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

class ProperNounsScreen(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("고유명사 관리")
        self.geometry("260x320")
        
        # 창 닫기 이벤트 처리
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 고유명사 데이터를 로드
        self.proper_nouns = load_proper_nouns()
        
        # 검색 프레임 생성
        search_frame = tk.Frame(self)
        search_frame.pack(pady=10, padx=10, fill="x")
        
        # 검색 라벨
        tk.Label(search_frame, text="검색").pack(side="left")
        
        # 검색 창 생성
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.update_displayed_nouns)
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side="left", fill="x", expand=True)
        
        # 추가 버튼 생성
        self.add_button = tk.Button(search_frame, text="Add", command=self.add_proper_noun)
        self.add_button.pack(side="right", padx=5)
        
        # 고유명사 리스트 캔버스 생성
        canvas_frame = tk.Frame(self, padx=5, pady=5)
        canvas_frame.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, width=180, height=200)
        self.scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
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
        
        # 저장하기 버튼 생성 (스크롤 밖 하단에 위치)
        self.save_button = tk.Button(self, text="저장하기", command=self.save_and_exit)
        self.save_button.pack(side="bottom", padx=10, pady=(0,10), anchor="s")
        
        # 고유명사 목록 표시
        self.update_displayed_nouns()

    # 고유명사 목록을 업데이트하는 함수
    def update_displayed_nouns(self, *args):
        search_term = self.search_var.get().lower()
        
        # 기존 위젯 제거
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # 검색어에 맞는 고유명사 표시
        for noun in self.proper_nouns:
            if search_term in noun['eng'].lower():
                self.add_proper_noun_item(noun)

    # 고유명사 항목을 추가하는 함수
    def add_proper_noun_item(self, noun):
        item_frame = tk.Frame(self.scrollable_frame)
        item_frame.pack(fill="x", pady=2)
        
        item_label = tk.Label(item_frame, text=noun['eng'], anchor="w", justify="left", width=12)
        item_label.pack(side="left", padx=(5, 20), fill="x", expand=True)
        
        delete_button = tk.Button(item_frame, text="Delete", command=lambda: self.confirm_delete(noun))
        delete_button.pack(side="right", padx=5)
        
        modify_button = tk.Button(item_frame, text="Modify", command=lambda: self.modify_proper_noun(noun))
        modify_button.pack(side="right", padx=5)

    # 고유명사 추가 창을 열어주는 함수
    def add_proper_noun(self):
        self.open_proper_noun_window()

    # 고유명사 수정 창을 열어주는 함수
    def modify_proper_noun(self, noun):
        self.open_proper_noun_window(noun)

    # 고유명사 삭제 확인 및 삭제 함수
    def confirm_delete(self, noun):
        if messagebox.askyesno("Confirm Delete", "정말 지우시겠습니까?"):
            self.delete_proper_noun(noun)

    # 고유명사 삭제 함수
    def delete_proper_noun(self, noun):
        self.proper_nouns.remove(noun)
        self.update_displayed_nouns()

    # 고유명사 추가/수정 창을 열어주는 함수
    def open_proper_noun_window(self, noun=None):
        def save():
            eng = eng_entry.get().strip()
            ko = ko_entry.get().strip()
            jp = jp_entry.get().strip()
            
            if not eng:
                messagebox.showwarning("Warning", "영어 이름은 필수값입니다.")
                return
            
            if noun:  # 수정의 경우
                if eng != noun['eng'] and any(n['eng'] == eng for n in self.proper_nouns):
                    messagebox.showwarning("Warning", "이미 있는 이름입니다.")
                    return
                noun.update({'eng': eng, 'ko': ko, 'jp': jp})
            else:  # 추가의 경우
                if any(n['eng'] == eng for n in self.proper_nouns):
                    messagebox.showwarning("Warning", "이미 있는 이름입니다.")
                    return
                self.proper_nouns.append({'eng': eng, 'ko': ko, 'jp': jp})
            
            self.update_displayed_nouns()
            window.destroy()

        window = tk.Toplevel(self)
        window.title("고유명사 추가/수정")
        window.geometry("240x160")
        
        form_frame = tk.Frame(window)
        form_frame.pack(pady=10, padx=10, fill="x")

        # 각 입력 항목을 라벨과 함께 배치
        tk.Label(form_frame, text="English:", width=9, anchor="w").grid(row=0, column=0)
        eng_entry = tk.Entry(form_frame)
        eng_entry.grid(row=0, column=1, padx=2, pady=5, sticky="ew")
        
        tk.Label(form_frame, text="Korean:", width=9, anchor="w").grid(row=1, column=0)
        ko_entry = tk.Entry(form_frame)
        ko_entry.grid(row=1, column=1, padx=2, pady=5, sticky="ew")
        
        tk.Label(form_frame, text="Japanese:", width=9, anchor="w").grid(row=2, column=0)
        jp_entry = tk.Entry(form_frame)
        jp_entry.grid(row=2, column=1, padx=2, pady=5, sticky="ew")
        
        if noun:
            eng_entry.insert(0, noun['eng'])
            ko_entry.insert(0, noun['ko'])
            jp_entry.insert(0, noun['jp'])
        
        button_frame = tk.Frame(window)
        button_frame.pack(pady=10)
        
        cancel_button = tk.Button(button_frame, text="Cancel", command=window.destroy)
        cancel_button.pack(side="right", padx=5)
        
        save_button = tk.Button(button_frame, text="Save", command=save)
        save_button.pack(side="right")

    # 저장 확인 및 저장 후 종료 함수
    def save_and_exit(self):
        if messagebox.askyesno("Save", "저장하고 종료하시겠습니까?"):
            save_proper_nouns(self.proper_nouns)
            self.destroy()

    # 창 닫기 시 확인 창 표시 함수
    def on_closing(self):
        if messagebox.askyesno("Quit", "저장하지 않고 종료하시겠습니까?"):
            global proper_nouns_screen
            proper_nouns_screen = None
            self.destroy()

# 고유명사의 모든 영어 이름을 리스트로 반환하는 함수
def get_proper_list():
    return [noun['eng'] for noun in load_proper_nouns()]

# 문자열에서 영어 이름을 일본어 이름으로 바꾸는 함수
def change_to_jp(input_string):
    proper_list = load_proper_nouns()
    input_string = input_string.lower()
    
    for noun in proper_list:
        if noun['eng'].lower() in input_string:
            input_string = input_string.replace(noun['eng'].lower(), noun['jp'])
    
    return input_string

def open_proper_nouns_screen(master):
    global proper_nouns_screen
    if proper_nouns_screen is None:
        proper_nouns_screen = ProperNounsScreen(master)
    else:
        proper_nouns_screen.lift()

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("400x400")
    open_proper_nouns_screen(root)
    root.mainloop()
