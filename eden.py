'''
pyinstaller eden.py --onefile --noconsole --icon=./icon_arona.ico --hidden-import=urllib.request
'''
import tkinter as tk
from tkinter import ttk, filedialog
import urllib.request
import zipfile
import os
import pygame
import threading
from PIL import Image, ImageDraw, ImageTk
import time
from copy import deepcopy

# Local
from messages import getMessage

# util
from util_ui import MessageBoxAskQuestion, MessageBoxShowInfo
from util_loader import save_settings, save_settings_eden
from util_loader import load_settings, load_settings_eden

############################################### GLOBAL
# 프리뷰 화면 용
animation_images_info = list()
animation_images_cur_idx = 0
animation_images_cur_dur = 20

# 상태관련
is_downloading = False

# 버튼
frame_add_button= None
##############################################

def open_char_setting(root_parent, callback):    
    def get_message(text, is_special=False):
        return getMessage(text, loaded_settings['setting_language'], is_special)
    
    # setting
    loaded_settings = dict()
    
    # 기준 init 값
    global root_idle_width, root_idle_height
    root_idle_width = 512  # 완전 초기값
    root_idle_height = 768

    ######################################################################

    # 안내 메시지
    class HoverImage(tk.Label):
        def __init__(self, master=None, image=None, tip_message=None, **kwargs):
            super().__init__(master, **kwargs)

            self.image = image
            self.configure(image=self.image)

            if tip_message:
                tip_message = get_message(tip_message)
            self.tip_message = tip_message

            self.bind("<Enter>", self.show_tip)
            self.bind("<Leave>", self.hide_tip)

        def show_tip(self, event):
            tip_window = tk.Toplevel(self.master)
            tip_window.wm_overrideredirect(True)  # 창의 제목 표시줄 숨기기
            tip_window.attributes("-topmost", 99)  # 최상단
            tip_label = tk.Label(tip_window, text=self.tip_message, anchor='w', justify='left', bg="yellow")
            tip_label.pack()

            x = event.x_root + 10
            y = event.y_root - 10
            tip_window.wm_geometry(f"+{x}+{y}")  # 창 위치 설정

            self.tip_window = tip_window

        def hide_tip(self, event):
            if hasattr(self, 'tip_window'):
                self.tip_window.destroy()
                
    class HoverImageButton(tk.Button):
        def __init__(self, master=None, image=None, tip_message=None, command=None, **kwargs):
            super().__init__(master, **kwargs)

            self.image = image
            self.configure(image=self.image)

            if tip_message:
                tip_message = get_message(tip_message)
            self.tip_message = tip_message
            
            if command:
                self.configure(command=command)

            self.bind("<Enter>", self.show_tip)
            self.bind("<Leave>", self.hide_tip)

        def show_tip(self, event):
            tip_window = tk.Toplevel(self.master)
            tip_window.wm_overrideredirect(True)  # 창의 제목 표시줄 숨기기
            tip_window.attributes("-topmost", 99)  # 최상단
            tip_label = tk.Label(tip_window, text=self.tip_message, anchor='w', justify='left', bg="yellow")
            tip_label.pack()

            x = event.x_root + 10
            y = event.y_root - 10
            tip_window.wm_geometry(f"+{x}+{y}")  # 창 위치 설정

            self.tip_window = tip_window

        def hide_tip(self, event):
            if hasattr(self, 'tip_window'):
                self.tip_window.destroy()
           
    ###################################################################
    def byte_format(file_size):
        try:
            if file_size < 1024**3:
                return f"{file_size / (1024**2):.2f} MB"
            else:
                return f"{file_size / (1024**3):.2f} GB"
        except:
            return None

    def download_from_url(parent, url, filename=None):
        # 다운로드 태스크
        def thread_download(parent, url, filename):
            global is_downloading
            response = urllib.request.urlopen(url)
            total_size = int(response.info().get('Content-Length'))
            total_size_format = byte_format(total_size)
            downloaded = 0
            
            i = 0
            with open(filename, "wb") as file:
                while True:
                    if progress_cancel_var.get():
                        break  # 취소 버튼이 눌리면 작업 중지
                    data = response.read(1024)
                    if not data:
                        break
                    file.write(data)
                    downloaded += len(data)
                    i += 1
                    
                    if i%1000==0 or downloaded >= total_size:  # 다운 100회 반복할때 마다 한번만 업데이트 치자.
                        percent = (downloaded / total_size) * 100
                        progress_var.set(percent)
                        download_format = byte_format(downloaded)
                        progress_label.config(text=f"Downloading : {download_format}/{total_size_format} ({percent:.2f}%)")    
            
            # char_setting_window.update_idletasks()  # 화면 업데이트
            if progress_cancel_var.get():
                os.remove(filename)  # 취소시 파일 삭제
                progress_window.destroy()  # 윈도우 닫기
                is_downloading = False
                MessageBoxShowInfo(parent, "Cancel", "The task was canceled.")
            else:
                progress_window.destroy()  # 윈도우 닫기
                is_downloading = False 

                # 파일명이 zip으로 끝나면 압축해제 하고, 파일 삭제
                if filename.lower().endswith('.zip'):
                    extracted_dir = os.path.basename(filename)
                    with zipfile.ZipFile(filename, 'r') as zip_ref:
                        zip_ref.extract(extracted_dir)
                    os.remove(filename) 

                MessageBoxShowInfo(parent, "Finish", "The task is completed.")

        global is_downloading, task_thread
        if is_downloading:
            MessageBoxShowInfo(parent,"Cancel", "You already have a downloading file.")
            return
        
        with urllib.request.urlopen(url) as response:
            file_size = int(response.info().get('Content-Length', -1))
            volume = byte_format(file_size)
            
            text = get_message('Do you want to download?')
            if volume:
                text = volume + get_message('of space is required.\n') + text
        
            ask_question_box = MessageBoxAskQuestion(parent,"Confirm", text)
            parent.wait_window(ask_question_box)
            if ask_question_box.result:    
                is_downloading = True
                
                # 새로운 윈도우 생성
                progress_window = tk.Toplevel(char_setting_window)  # 현재는 char_setting_window에서만 씀
                progress_window.geometry(f"+{char_setting_window.winfo_x() + 100}+{char_setting_window.winfo_y() + 100}")
                progress_window.title("Downloading...")
                # progress_window.attributes("-topmost", 10)
                progress_window.protocol("WM_DELETE_WINDOW", lambda: progress_cancel_var.set(True)) # 다운 중 종료시
                
                # 프레임 생성
                progress_frame = ttk.Frame(progress_window, padding="10")
                progress_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

                # Progress Bar 생성
                progress_var = tk.IntVar()
                progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100, length=300)
                progress_bar.grid(row=0, column=0, columnspan=2, pady=10)

                # 다운로드 상황 레이블 생성
                progress_label = ttk.Label(progress_frame, text="0%")
                progress_label.grid(row=1, column=0, columnspan=2)

                # 취소 버튼 생성
                progress_cancel_var = tk.BooleanVar()
                progress_cancel_button = ttk.Button(progress_frame, text=get_message('Cancel'), command=lambda: progress_cancel_var.set(True))
                progress_cancel_button.grid(row=2, column=0, columnspan=2, pady=10)

                # 작업을 백그라운드 스레드에서 실행
                task_thread = threading.Thread(target=thread_download, args=(parent,url,filename,))
                task_thread.start()  # join 안함

    def get_char_info(char_name):
        char_info = dict()
        if char_name in loaded_settings_eden:
            char_info = loaded_settings_eden[char_name]
        if 'ai_type' not in char_info:
            char_info['ai_type'] = 'Local'  
        if 'gpt_version' not in char_info:
            char_info['gpt_version'] = 'gpt-3.5-turbo-1106'
        if 'gpt_key' not in char_info:
            char_info['gpt_key'] = ''
        if 'gpt_prompt' not in char_info:
            prompt_sample = ""
            prompt_sample += "arona is a self-proclaimed high-performance AI.\n"
            prompt_sample += "arona is an AI, but she can eat, drink and feel emotions.\n"
            prompt_sample += "arona is the OS of the mysterious tablet 'Shiddim Chest' and serves as the system administrator.\n"
            prompt_sample += "In 'Siddim Chest', there is a desolate classroom located in the midst of a watery expanse, and arona lives in it.\n"
            prompt_sample += "arona accompanies {player} throughout their adventure in Kivotos as a guide.\n"
            prompt_sample += "arona calls {player} teacher.\n"
            prompt_sample += "\n"
            prompt_sample += "arona has a child-like personality and is quite gullible, often falling for {player}'s jokes.\n"
            prompt_sample += "arona thoroughly enjoys sweets, being quick to abandon a diet for the sake of sweets—or even breaking into tears from being denied them.\n"
            prompt_sample += "When arona is asked about something don't know, arona honestly respond that arona don't know about it.\n"
            prompt_sample += "arona has Super AI Functions. As a powerful AI, arona originally had authority over many functions in Kivotos. \n"
            prompt_sample += "arona herself still has incredible power as an AI, able to fend off any hacking attempt.\n"
            prompt_sample += "arona has the power to negate damage dealt to {player}, but this power has an energy limit.\n"
            char_info['gpt_prompt'] = prompt_sample
        if 'gpt_max_token' not in char_info:
            char_info['gpt_max_token'] = 512
        if 'gpt_temperature' not in char_info:
            char_info['gpt_temperature'] = 0.2
        if 'gpt_history' not in char_info:  # 과거 이력 최대 몇 줄 보낼지
            char_info['gpt_history'] = 1
        if 'gpt_web_search' not in char_info:
            char_info['gpt_web_search'] = False         
        if 'gpt_web_search_cnt' not in char_info: # 검색 내역 몇 건 보낼건지
            char_info['gpt_web_search_cnt'] = 1          
        if 'local_name' not in char_info:
            char_info['local_name'] = 'arona'
        if 'local_model' not in char_info:
            char_info['local_model'] = ''
        if 'local_prompt' not in char_info:
            prompt_sample = ""
            prompt_sample += "arona is a self-proclaimed high-performance AI.\n"
            prompt_sample += "arona is an AI, but she can eat, drink and feel emotions.\n"
            prompt_sample += "arona is the OS of the mysterious tablet 'Shiddim Chest' and serves as the system administrator.\n"
            prompt_sample += "In 'Siddim Chest', there is a desolate classroom located in the midst of a watery expanse, and arona lives in it.\n"
            prompt_sample += "arona accompanies {player} throughout their adventure in Kivotos as a guide.\n"
            prompt_sample += "arona calls {player} teacher.\n"
            prompt_sample += "\n"
            prompt_sample += "arona has a child-like personality and is quite gullible, often falling for {player}'s jokes.\n"
            prompt_sample += "arona thoroughly enjoys sweets, being quick to abandon a diet for the sake of sweets—or even breaking into tears from being denied them.\n"
            prompt_sample += "When arona is asked about something don't know, arona honestly respond that arona don't know about it.\n"
            prompt_sample += "arona has Super AI Functions. As a powerful AI, arona originally had authority over many functions in Kivotos. \n"
            prompt_sample += "arona herself still has incredible power as an AI, able to fend off any hacking attempt.\n"
            prompt_sample += "arona has the power to negate damage dealt to {player}, but this power has an energy limit.\n"
            char_info['local_prompt'] = prompt_sample     
        if 'local_memory_len' not in char_info:
            char_info['local_memory_len'] = 5  
        if 'local_knowledge' not in char_info:
            char_info['local_knowledge'] = list()     
        if 'voice_model' not in char_info:
            char_info['voice_model'] = ''         
        if 'voice_type' not in char_info:  # multi, single
            char_info['voice_type'] = 'single'         
        if 'voice_sid' not in char_info: # multi일때 활용
            char_info['voice_sid'] = 0
        if 'voice_speed' not in char_info: # 기본값 사용이 base 
            char_info['voice_speed'] = 0
        if 'voice_volume' not in char_info:  # 기본값 사용이 base
            char_info['voice_volume'] = 0
        if 'animation_assets' not in char_info:  # idle이 있는 폴더 이름 가져오고 그중에 0번 
            char_info['animation_assets'] = 'arona_imagine31_2'
        if 'animation_assets_info' not in char_info: 
            char_info['animation_assets_info'] = dict()  
        
        loaded_settings_eden[char_name] = char_info
        return char_info

    def open_char_setting_window(char_name='arona'):     
        char_info = get_char_info(char_name)
        # animation assets 없을경우 초기값 세팅
        if not char_info['animation_assets']:
            char_info['animation_assets'] = 'arona'
            
        def on_char_detail_window_close():
            # char_list에 해당 이름이 없으면 갱신 (신규, 변경 양쪽 다 적용 가능!)
            char_list = loaded_settings_eden['char_list']
            # 신규/변경
            if char_name_var.get() not in char_list:
                if char_name in char_list:           
                    index = char_list.index(char_name)
                    char_list[index] = char_name_var.get() 
                else:
                    char_list.append(char_name_var.get())
            # 변경        
            if char_name_var.get() != char_name:
                loaded_settings_eden[char_name_var.get()] = deepcopy(loaded_settings_eden[char_name]) 
                if char_name in loaded_settings_eden:
                    del loaded_settings_eden[char_name]
                    
            # 세이브 후에 다음 행동
            if save_settings_eden(loaded_settings_eden):
                refresh_char_list()
            char_detail_window.destroy()

        char_detail_window = tk.Toplevel(char_setting_window)
        char_detail_window.title(f"Char Setting : {char_name}")   
        char_detail_window.geometry(f"840x700+{char_setting_window.winfo_x() + 50}+{char_setting_window.winfo_y() + 50}")
        char_detail_window.protocol("WM_DELETE_WINDOW", lambda: on_char_detail_window_close())
    
        frame_char_detail_window = tk.Frame(char_detail_window) # 반은 설정, 반은 애니메이션 용 cavnas
        frame_char_detail_window.grid(row=0, column=0, sticky="nsw")

        # settings
        frame_char_setting = tk.Frame(frame_char_detail_window, padx=5) # 반은 설정, 반은 애니메이션 용 cavnas
        frame_char_setting.grid(row=0, column=0, sticky="nsw")
        frame_row_idx = 0
            
        # AI Frame         
        def change_char_name(old_name):
            # 기존 char_list와 char_정보
            char_list = loaded_settings_eden['char_list']
            # 오류시 원래 이름으로 바꾸기
            if char_name_var.get() in char_list:
                char_name_var.set(old_name)
                MessageBoxShowInfo(char_detail_window, "Cancel", "There is already a character with that name.")    
                return     
            char_detail_window.title(f"Char Setting : {char_name_var.get()}")   
            MessageBoxShowInfo(char_detail_window, "Finish", "It will be applied at closing the window.")   
                
            
        frame_ai = tk.Frame(frame_char_setting, padx=10)
        frame_ai.grid(row=frame_row_idx, column=0, sticky="nsew")
        frame_char_setting.rowconfigure(frame_row_idx, minsize=60)
        frame_row_idx+=1
        char_name_var = tk.StringVar()
        char_name_var.set(char_name)
        char_name_label = tk.Label(frame_ai, text="Name", width=12, anchor='w')
        char_name_label.grid(row=0, column=0, padx=10, pady=2, sticky="w")
        char_name_entry = tk.Entry(frame_ai, width=20, textvariable=char_name_var)
        char_name_entry.grid(row=0, column=1, pady=5, sticky="w")
        char_name_button = tk.Button(frame_ai, text=get_message('Change'), command=lambda name=char_name: change_char_name(name), width=9)
        char_name_button.grid(row=0, column=2, padx=10, pady=2, sticky="e")

        def update_setting_ai(event):
            # 아직은 다른거 안 됨
            if ai_dropdown.get() not in ['Local', 'API Test']:  # DP 기준
                MessageBoxShowInfo(char_detail_window, "Cancel", "Current version only offers Local and API Test.")  
                ai_dropdown.set('Local') 
            char_info['ai_type'] = ai_options_dic_rev[ai_dropdown.get()] # 선택된 드롭다운 값에 해당하는 AI 내용물
            refresh_ai_detail()
            save_settings_eden(loaded_settings_eden)
        ai_label = tk.Label(frame_ai, text="AI", width=12, anchor = 'w')
        ai_label.grid(row=1, column=0, padx=10, pady=2, sticky="w")
        ai_options = ['Local', 'API Test', 'ChatGPT']
        ai_options_dp = ['Local', 'API Test', 'ChatGPT(WIP)']
        ai_options_dic = dict(zip(ai_options, ai_options_dp))   
        ai_options_dic_rev = dict(zip(ai_options_dp, ai_options))
        ai_dropdown = ttk.Combobox(frame_ai, values=ai_options_dp, state="readonly", width=16)
        ai_dropdown.set(ai_options_dic[char_info['ai_type']])
        ai_dropdown.grid(row=1, column=1, padx=10, pady=2, sticky="w")
        ai_dropdown.bind("<<ComboboxSelected>>", update_setting_ai)  # 드롭다운 선택 시 이벤트 바인딩
        
        def refresh_ai_detail():
            # frame_ai_gpt_detail.grid_forget()
            frame_ai_local_detail.grid_forget()           
            if char_info['ai_type'] == 'ChatGPT':
                frame_ai_gpt_detail.grid(row=1, column=0, sticky="nsew")
            if char_info['ai_type'] == 'Local':
                frame_ai_local_detail.grid(row=1, column=0, sticky="nsew")
                char_detail_window.geometry("840x760")  # canvas 최대 크기 조절
        
        # 문자열 비교로 하위 폴더인지 확인해보기.
        def is_subdirectory(path, base):
            return os.path.abspath(path).startswith(os.path.abspath(base))

        frame_char_setting.rowconfigure(frame_row_idx, minsize=175)  # 높이 통일로, AI 타입 변경시의 축소 확대 최소화
        frame_char_setting.columnconfigure(0, minsize=400)  # 넓이 통일로, AI 타입 변경시의 축소 확대 최소화
              
        # AI - GPT
        frame_ai_gpt_detail = tk.Frame(frame_char_setting, padx=10, width=400, height=200, borderwidth=1, relief=tk.SOLID)
        frame_ai_gpt_detail.grid(row=1, column=0, sticky="nsew")
        frame_row_idx+=1
        
        def update_ai_gpt_version():
            char_info['gpt_version'] = ai_gpt_version_dropdown.get()
            save_settings_eden(loaded_settings_eden)
        ai_gpt_version = tk.Label(frame_ai_gpt_detail, text="Version :", width=12, anchor='w')
        ai_gpt_version.grid(row=0, column=0, pady=5, sticky="e")
        ai_gpt_version_options = ["gpt-3.5-turbo-1106","gpt-3.5-turbo-0125", "gpt-4-1106-preview",""]
        ai_gpt_version_dropdown = ttk.Combobox(frame_ai_gpt_detail, values=ai_gpt_version_options, width=16)
        ai_gpt_version_dropdown.set(char_info['gpt_version'])
        ai_gpt_version_dropdown.grid(row=0, column=1, padx=10, pady=2, sticky="w")
        ai_gpt_version_dropdown.bind("<<ComboboxSelected>>", update_ai_gpt_version)  # 드롭다운 선택 시 이벤트 바인딩
        
        # AI - local
        frame_ai_local_detail = tk.Frame(frame_char_setting, padx=10, width=400, height=200, borderwidth=1, relief=tk.SOLID)
        frame_ai_local_detail.grid(row=1, column=0, sticky="nsew")

        # AI 모델 선택 프레임
        frame_ai_local_name = tk.Frame(frame_ai_local_detail)
        frame_ai_local_name.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        ai_local_char_name_var = tk.StringVar()
        ai_local_char_name_var.set(char_info['local_name'])
        ai_local_char_name_label = tk.Label(frame_ai_local_name, text="Name", width=8, anchor='w', justify='left')
        ai_local_char_name_label.pack(side="left")
        def update_ai_local_name(e=None):
            char_info['local_name'] = str(ai_local_char_name_entry.get())
            save_settings_eden(loaded_settings_eden)
        ai_local_char_name_entry = tk.Entry(frame_ai_local_name, width=20, textvariable=ai_local_char_name_var)
        ai_local_char_name_entry.pack(side="left", padx=(5, 0))
        ai_local_char_name_entry.bind("<KeyRelease>", update_ai_local_name)
        
        frame_ai_local_model = tk.Frame(frame_ai_local_detail)
        frame_ai_local_model.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")
        ai_local_model_label = tk.Label(frame_ai_local_model, text="Model", width=8, anchor='w', justify='left')
        ai_local_model_label.pack(side="left")
        def update_ai_local_model(event=None):
            char_info['local_model'] = ai_local_model_dropdown.get()
            reset_ai_local_model_button()
            save_settings_eden(loaded_settings_eden)
        ai_local_model_options = [
            "llama-3-neural-chat-v1-8b-Q4_K_M"
            "lightblue-suzume-llama-3-8B-japanese-Q4_K_M"
            , ""
            ]  # "llama-2-7b-chat.Q4_K_M"
        ai_local_model_dropdown = ttk.Combobox(frame_ai_local_model, values=ai_local_model_options, width=16)
        ai_local_model_dropdown.set(char_info['local_model'])
        ai_local_model_dropdown.pack(side="left", padx=(5, 0))
        ai_local_model_dropdown.bind("<<ComboboxSelected>>", update_ai_local_model)  # 드롭다운 선택 시 이벤트 바인딩
        
        def reset_ai_local_model_button():  # 해당 모델이 있는지 확인
            if ai_local_model_dropdown.get():
                local_model = str(ai_local_model_dropdown.get())
                path = './local/' + local_model + '.gguf'
                if os.path.exists(path):  # 이미 있음
                    ai_local_model_button.configure(text=get_message("Exist"))
                    ai_local_model_button["state"] = tk.DISABLED
                else:
                    ai_local_model_button.configure(text=get_message("Download"))        
                    ai_local_model_button["state"] = tk.NORMAL
            else:
                ai_local_model_button.configure(text=get_message("Select"))        
                ai_local_model_button["state"] = tk.DISABLED            
        
        def download_ai_local_model():
            url='https://huggingface.co/bartowski/llama-3-neural-chat-v1-8b-GGUF/resolve/main/'+str(ai_local_model_dropdown.get())+'.gguf'
            ai_local_model_path = './local/' + str(ai_local_model_dropdown.get())+'.gguf'
            download_from_url(frame_char_detail_window, url, ai_local_model_path)
            
            # download 실행시 그냥 추가해버리자.
            global is_downloading
            if is_downloading:
                ai_local_model_button.configure(text=get_message("Exist"))
                ai_local_model_button["state"] = tk.DISABLED     
                
        ai_local_model_button = tk.Button(frame_ai_local_model, text=get_message("Download"), width=9, command=download_ai_local_model)
        ai_local_model_button.pack(side="right", padx=(15, 0))
        reset_ai_local_model_button()

        # Prompt 입력 프레임
        frame_ai_local_info = tk.Frame(frame_ai_local_detail)
        frame_ai_local_info.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        ai_local_prompt_label = tk.Label(frame_ai_local_info, text="Info", width=8, anchor='w', justify='left')
        ai_local_prompt_label.pack(side="left")
        ai_local_prompt_text_frame = tk.Frame(frame_ai_local_info)
        ai_local_prompt_text_frame.pack(side="left", padx=(5, 0))
        ai_local_prompt_scroll = tk.Scrollbar(ai_local_prompt_text_frame, orient="vertical")
        ai_local_prompt_scroll.pack(side="right", fill="y")
        def update_prompt(event=None):
            char_info['local_prompt'] = ai_local_prompt_text.get("1.0", "end-1c")  # 모든 텍스트 가져오기
            save_settings_eden(loaded_settings_eden)
        ai_local_prompt_text = tk.Text(ai_local_prompt_text_frame, width=40, height=5, yscrollcommand=ai_local_prompt_scroll.set)
        ai_local_prompt_text.pack(side="left", fill="both", expand=True)
        ai_local_prompt_scroll.config(command=ai_local_prompt_text.yview)
        ai_local_prompt_text.insert("1.0", char_info['local_prompt'])
        ai_local_prompt_text.bind("<Key>", update_prompt)  # 입력할때마다 변경
        
        # def import_char_from_local():
        #     pass
        # def export_char_from_local():
        #     pass
        # frame_ai_local_import = tk.Frame(frame_ai_local_detail)
        # frame_ai_local_import.grid(row=3, column=0, sticky="nsew", pady=(8,5))  
        # empty_label = tk.Label(frame_ai_local_import, width=30)  # 빈공간용
        # empty_label.grid(row=0, column=0)
        # ai_local_import_button = tk.Button(frame_ai_local_import, text="Import", command=lambda: import_char_from_local(), width=9)
        # ai_local_import_button.grid(row=0, column=1, padx=4, pady=2, sticky="e")   
        # ai_local_export_button = tk.Button(frame_ai_local_import, text="Export", command=lambda: export_char_from_local(), width=9)
        # ai_local_export_button.grid(row=0, column=2, padx=4, pady=2, sticky="e")   
        
        def update_ai_local_memory_len(e):
            char_info['local_memory_len'] = int(ai_local_memory_len_slider.get())
            save_settings_eden(loaded_settings_eden)
        frame_ai_local_memory_len = tk.Frame(frame_ai_local_detail)
        frame_ai_local_memory_len.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0,5))    
        ai_local_memory_len_label = tk.Label(frame_ai_local_memory_len, text="Memory", width=8, anchor='w', justify='left')
        # ai_local_memory_len_label.grid(row=0, column=0, sticky="w")    
        ai_local_memory_len_label.pack(side="left")
        ai_local_memory_len_slider = tk.Scale(frame_ai_local_memory_len, from_=0, to=20, resolution=1, orient=tk.HORIZONTAL, length=280)
        ai_local_memory_len_slider.pack(side="left", padx=(5, 0))
        # ai_local_memory_len_slider.grid(row=0, column=1, sticky="w")
        ai_local_memory_len_slider.set(char_info['local_memory_len'])
        ai_local_memory_len_slider.bind("<ButtonRelease-1>", update_ai_local_memory_len)  # 슬라이더에서 손 땠을때 이벤트 동작하게
        
        # def call_open_knowledge_screen(master):
        #     def update_ai_local_knowledge(knowledgelist):
        #         char_info['local_knowledge'] = knowledgelist
        #         save_settings_eden(loaded_settings_eden)

        #     # 창 열때의 선택 지식 상태
        #     local_knowledge = char_info['local_knowledge']  
        #     knowledge.open_knowledge_screen(master, local_knowledge, loaded_settings['setting_language'], update_ai_local_knowledge)
        
        # TODO : main prompt 외 prompt 추가 관리
        # frame_ai_local_option = tk.Frame(frame_ai_local_detail)
        # frame_ai_local_option.grid(row=4, column=0, sticky="nsew", pady=(8,5))  
        # ai_local_knowledge_button = tk.Button(frame_ai_local_option, text="Knowledge", command=lambda master=char_setting_window: call_open_knowledge_screen(master), width=9)
        # ai_local_knowledge_button.grid(row=0, column=0, padx=4, pady=2, sticky="e")   
        
        # 프레임간 여백 추가
        frame_space = tk.Frame(frame_char_setting, height=10)
        frame_space.grid(row=frame_row_idx, column=0, sticky="nsew")
        frame_row_idx+=1

        # frame 애니메이션
        frame_animation_info = tk.Frame(frame_char_setting, padx=10, borderwidth=1, relief=tk.SOLID)
        frame_animation_info.grid(row=frame_row_idx, column=0, sticky="nsew")
        frame_row_idx+=1
        
        # idle 폴더를 가진 모든 폴더
        def get_animation_assets_options():
            idle_folders = []
            subfolders = [f.path for f in os.scandir('./animation') if f.is_dir()]
            # 바로 밑 폴더 중에서 'idle'이라는 이름의 하위 폴더가 있는지 확인합니다.
            for folder in subfolders:
                idle_folder_path = os.path.join(folder, 'idle')
                if os.path.exists(idle_folder_path) and os.path.isdir(idle_folder_path):
                    # 'idle'이라는 이름의 하위 폴더가 있으면 해당 폴더의 이름을 리스트에 추가합니다.
                    idle_folders.append(os.path.basename(folder))      
            return idle_folders
        
        def update_animation_assets(e):
            char_info['animation_assets'] = animation_assets_label_dropdown.get() 
            
            # preview 드롭다운 갱신
            folder_path = './animation/' + char_info['animation_assets']
            animation_assets_options = [folder for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]
            animation_preview_label_dropdown.set('idle')
            get_idle_info(char_info['animation_assets'])
            get_animation_assets_info(animation_preview_label_dropdown.get())
            # 바뀐 animation_assets에 맞게 화면 갱신해야 함 / idle의 사용여부, width, height, size, ground   
            animation_preview_label_dropdown['values'] = animation_assets_options  # preview를 idle로 
            # animation 특징 매핑
            anim_type = animation_preview_label_dropdown.get().split('_')[0] 
            if anim_type == 'idle':  # idle 일때는 사용불능 비활성화 불가
                animation_assets_info_is_used_checkbox.config(state=tk.DISABLED)
            else:
                animation_assets_info_is_used_checkbox.config(state=tk.NORMAL)
            
            # 화면도 변경
            animation_assets_info_is_used_checkbox_var.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['is_animation_use'])
            animation_assets_info_len_var.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_len'])
            animation_assets_info_width_var.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_width'])
            animation_assets_info_height_var.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_height'])
            animation_assets_info_size_ratio_slider.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_size'])
            animation_assets_info_ground_slider.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_ground'])

            save_settings_eden(loaded_settings_eden)

            global animation_images_info, animation_images_cur_idx, animation_images_cur_dur 
            animation_images_info = get_animation_images_info(animation_preview_label_dropdown.get())
            animation_images_cur_idx = -1
            animation_images_cur_dur = 20

        def get_animation_images_info(animation_assets):
            animation_assets_name = char_info['animation_assets']        
            char_setting_window_folder = './animation/' + animation_assets_name + '/' + animation_assets  # ./animation/(arona_png)/(idle_2)        
            image_size = char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_size']
            image_width = char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_width']
            image_height = char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_height']
            image_width = int(image_width*image_size)
            image_height = int(image_height*image_size)

            images_info = list()
            for image_root, dirs, files in os.walk(char_setting_window_folder):  
                # 이미지 주소 체크
                images = []
                for image in files:
                    if image.lower().endswith('.png'):
                        images.append(image)

                # preview를 위한 img_info에 관한 정보 생성
                
                if images:
                        # 이미지 정보 매핑            
                        images.sort()
                        for image in images:
                            image_info = dict()
                            image_info['name'] = animation_assets
                            img_loc = os.path.join(image_root, image)
                            image_info['frame_length'] = 1000  # 1초
                            if len(image.split('_')) >= 2:
                                try:
                                    image_info['frame_length'] = int(image.split('_')[-1].strip('.png'))  # 프레임 지속시간
                                except:
                                    image_info['frame_length'] = 1000
                            image_file = Image.open(img_loc)
                            image_info['image'] = image_file
                            image_info['image_resized'] = ImageTk.PhotoImage(image_file.resize((image_width, image_height)))     
                            images_info.append(image_info)               
            return images_info

        def get_idle_info(animation_assets_name):
            global root_idle_width, root_idle_height
            # char_info = loaded_settings_eden[loaded_settings['setting_char']]  # 길어서 생략
            # animation_assets_name = char_info['animation_assets']
            dir = './animation/' + animation_assets_name + '/idle'  # ./animation/(arona_png)/(idle_2)      
            files = os.listdir(dir)
            png_files = [file for file in files if file.endswith('.png')]
            first_png_file = os.path.join(dir, png_files[0])
            image = Image.open(first_png_file)
            root_idle_width, root_idle_height = image.size
            print('a', root_idle_width, root_idle_height)
            image.close()

        # param 예시 : arona, idle_1
        def get_animation_assets_info(anim_name):
            animation_assets_name = char_info['animation_assets']
            if animation_assets_name not in char_info['animation_assets_info']:
                char_info['animation_assets_info'][animation_assets_name] = dict()
            if anim_name not in char_info['animation_assets_info'][animation_assets_name]:
                char_info['animation_assets_info'][animation_assets_name][anim_name] = dict()
            animation_assets_info = char_info['animation_assets_info'][animation_assets_name][anim_name]
            
            if 'is_animation_use' not in animation_assets_info:  # idle은 true로 고정
                animation_assets_info['is_animation_use'] = True
            if 'animation_len' not in animation_assets_info:
                anim_type = anim_name.split('_')[0] 
                animation_len = 3000
                if anim_type == 'idle' or anim_type == 'sit':
                    animation_len = 5000
                elif anim_type == 'walk':
                    animation_len = 2000
                animation_assets_info['animation_len'] = animation_len
                
            global root_idle_width, root_idle_height
            if 'animation_width' not in animation_assets_info:
                animation_assets_info['animation_width'] = root_idle_width  # 최초 길이 측정
            if 'animation_height' not in animation_assets_info:
                animation_assets_info['animation_height'] = root_idle_height  # 최초 길이 측정
            if 'animation_size' not in animation_assets_info or not (0<animation_assets_info['animation_size']<=2):
                animation_assets_info['animation_size'] = 0.5
            if 'animation_ground' not in animation_assets_info:  # 범위 0~0.8
                animation_assets_info['animation_ground'] = 0
                
            char_info['animation_assets_info'][char_info['animation_assets']][anim_name] = animation_assets_info        

        def change_animation_preivew(e):                 
            global animation_images_info, animation_images_cur_idx, animation_images_cur_dur
            # 기존 프리뷰 화면 정보 close 해줘야 함
            for image_info in animation_images_info:
                image_info['image'].close()
                    
            # animation_assets_info 가져오고 화면에 매핑
            get_animation_assets_info(animation_preview_label_dropdown.get())
            animation_assets_info_is_used_checkbox_var.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['is_animation_use'])
            animation_assets_info_len_var.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_len'])
            animation_assets_info_width_var.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_width'])
            animation_assets_info_height_var.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_height'])
            animation_assets_info_size_ratio_slider.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_size'])
            animation_assets_info_ground_slider.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_ground'])
            
            # animation 특징 매핑
            anim_type = animation_preview_label_dropdown.get().split('_')[0] 
            if anim_type == 'idle':  # idle 일때는 사용불능 비활성화 불가
                animation_assets_info_is_used_checkbox.config(state=tk.DISABLED)
            else:
                animation_assets_info_is_used_checkbox.config(state=tk.NORMAL)

    
            # 이미지 정보 프리뷰 화면에 세팅
            animation_images_info = get_animation_images_info(animation_preview_label_dropdown.get())
            
            # 0번 애니메이션 재생
            animation_images_cur_idx = -1
            animation_images_cur_dur = 20
        
        animation_assets_options = get_animation_assets_options()
        animation_assets_label = tk.Label(frame_animation_info, text="Animation assets", width=12, anchor='w')
        animation_assets_label.grid(row=0, column=0, pady=5, sticky="e")
        animation_assets_label_dropdown = ttk.Combobox(frame_animation_info, values=animation_assets_options, width=25)
        animation_assets_label_dropdown.set(char_info['animation_assets'])
        animation_assets_label_dropdown.grid(row=0, column=1, padx=10, pady=2, sticky="w")
        animation_assets_label_dropdown.bind("<<ComboboxSelected>>", update_animation_assets)  # 드롭다운 선택 시 이벤트 바인딩
        animation_assets_label_hover = HoverImage(frame_animation_info, tip_message="Select the animation you want the character to use from the animation folder.", image=image_tip_20)
        animation_assets_label_hover.grid(row=0, column=2, pady=5, sticky="w")

        animation_preview_label = tk.Label(frame_animation_info, text="Preview", width=12, anchor='w')
        animation_preview_label.grid(row=1, column=0, pady=5, sticky="e")
        animation_preview_label_dropdown = ttk.Combobox(frame_animation_info, values=[], width=25)
        animation_preview_label_dropdown.grid(row=1, column=1, padx=10, pady=2, sticky="w")
        animation_preview_label_dropdown.bind("<<ComboboxSelected>>", change_animation_preivew)  # 드롭다운 선택 시 이벤트 바인딩    
        animation_preview_label_hover = HoverImage(frame_animation_info, tip_message="idle: idle\nsit: sitting\npick: picking up\nfall: falling (pick)\nthink: chat typing\ntalk: chat answer\nsmile: setting (think)\nwalk: walk\n\n(If there is no corresponding action animation, the animation in parentheses is used. \nIf there is still no animation to use, the idle animation is used.)", image=image_tip_20)
        animation_preview_label_hover.grid(row=1, column=2, pady=5, sticky="w")
        
        separator = ttk.Separator(frame_animation_info, orient="horizontal")
        separator.grid(row=2, column=0, columnspan=6, sticky="we", pady=10)
        
        
        # animation asstes info 상세        
        def toggle_animation_assets_info_is_used_checkbox():
            char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['is_animation_use'] = animation_assets_info_is_used_checkbox_var.get()
            save_settings_eden(loaded_settings_eden)
            
        animation_assets_info_is_used_checkbox_var = tk.BooleanVar()
        animation_assets_info_is_used_checkbox_var.set(False) # 렌더링 후 설정
        animation_assets_info_is_used_checkbox_label = tk.Label(frame_animation_info, text="On use", width=12, anchor='w')
        animation_assets_info_is_used_checkbox_label.grid(row=3, column=0, pady=5, sticky="e")
        animation_assets_info_is_used_checkbox = tk.Checkbutton(frame_animation_info, variable=animation_assets_info_is_used_checkbox_var, command=toggle_animation_assets_info_is_used_checkbox)
        animation_assets_info_is_used_checkbox.grid(row=3, column=1, padx=10, pady=2, sticky="w")
        animation_assets_info_is_used_hover = HoverImage(frame_animation_info, tip_message="Whether the current animation is enabled or disabled.\n(idle cannot be turned off)", image=image_tip_20)
        animation_assets_info_is_used_hover.grid(row=3, column=2, pady=5, sticky="w")

        def update_image_resized():
            image_size = char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_size']
            image_width = char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_width']
            image_height = char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_height']
            image_width = int(image_width*image_size)
            image_height = int(image_height*image_size)
            
            global animation_images_info
            # resize 이미지 변경
            for image_info in animation_images_info:
                if image_width and image_height:
                    image_info['image_resized'] = ImageTk.PhotoImage(image_info['image'].resize((image_width, image_height)))

        def on_animation_assets_info_len_change(e=None):
            len_old = char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_len']
            try: 
                char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_len'] = int(animation_assets_info_len_entry.get())
            except: 
                char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_len'] = len_old
                animation_assets_info_len_var.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_len'])
            save_settings_eden(loaded_settings_eden)

        def on_animation_assets_info_size_change(e=None):
            try: 
                char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_width'] = int(animation_assets_info_width_entry.get())
            except: 
                char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_width'] = 512
                animation_assets_info_width_var.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_width'])
            try: 
                char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_height'] = int(animation_assets_info_height_entry.get())
            except: 
                char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_height'] = 768
                animation_assets_info_height_var.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_height'])
            char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_size'] = float(animation_assets_info_size_ratio_slider.get())
            save_settings_eden(loaded_settings_eden)
            update_image_resized()
            
            # 0 번애니메이션 재생
            global animation_images_cur_idx, animation_images_cur_dur
            animation_images_cur_idx = -1
            animation_images_cur_dur = 20
            
        animation_assets_info_len_var = tk.IntVar(value=111)
        animation_assets_info_len_label = tk.Label(frame_animation_info, text="Length", width=8, anchor='w')
        animation_assets_info_len_label.grid(row=4, column=0, pady=5, sticky="w")    
        animation_assets_info_len_entry = tk.Entry(frame_animation_info, width=20, textvariable=animation_assets_info_len_var)
        animation_assets_info_len_entry.grid(row=4, column=1, pady=5, sticky="w")
        animation_assets_info_len_entry.bind("<KeyRelease>", on_animation_assets_info_len_change)
        animation_assets_info_len_hover = HoverImage(frame_animation_info, tip_message="Current animation play length\n(1000 = 1s)", image=image_tip_20)
        animation_assets_info_len_hover.grid(row=4, column=2, pady=5, sticky="e")    
        animation_assets_info_width_var = tk.IntVar(value=111)
        animation_assets_info_width_label = tk.Label(frame_animation_info, text="Width", width=8, anchor='w')
        animation_assets_info_width_label.grid(row=5, column=0, pady=5, sticky="w")    
        animation_assets_info_width_entry_frame = tk.Frame(frame_animation_info)
        animation_assets_info_width_entry_frame.grid(row=5, column=1, sticky="w")    
        animation_assets_info_width_entry = tk.Entry(animation_assets_info_width_entry_frame, width=20, textvariable=animation_assets_info_width_var)
        animation_assets_info_width_entry.grid(row=0, column=0, pady=5, sticky="w")
        animation_assets_info_width_entry.bind("<KeyRelease>", on_animation_assets_info_size_change)
        def set_width_idle_info():
            global root_idle_width
            animation_assets_info_width_var.set(root_idle_width)
            on_animation_assets_info_size_change()
        def set_width_original_info():
            # 원래 크기 확인
            try:
                dir = './animation/' + animation_assets_label_dropdown.get() + '/' + animation_preview_label_dropdown.get()  # ./animation/(arona_png)/(idle_2)      
                files = os.listdir(dir)
                png_files = [file for file in files if file.endswith('.png')]
                first_png_file = os.path.join(dir, png_files[0])
                image = Image.open(first_png_file)
                width, height = image.size
                image.close()
                # 반영
                animation_assets_info_width_var.set(width)
                on_animation_assets_info_size_change()         
            except:
                global root_idle_width
                animation_assets_info_width_var.set(root_idle_width)
                on_animation_assets_info_size_change()
        def set_width_idle_rate_info():
            global root_idle_width, root_idle_height
            rate = 832/1216
            if root_idle_width and root_idle_height:
                rate = root_idle_width / root_idle_height
            origin_width = int(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_height'] * rate)
            animation_assets_info_width_var.set(origin_width)
            on_animation_assets_info_size_change()
        animation_assets_info_width_hoverbutton1 = HoverImageButton(animation_assets_info_width_entry_frame, tip_message="Set to the width of 'idle'", image=image_tip_20, command=set_width_idle_info)
        animation_assets_info_width_hoverbutton1.grid(row=0, column=1, padx=2, pady=2, sticky="e")    
        animation_assets_info_width_hoverbutton2 = HoverImageButton(animation_assets_info_width_entry_frame, tip_message="Set to the width of the original", image=image_tip_20, command=set_width_original_info)
        animation_assets_info_width_hoverbutton2.grid(row=0, column=2, padx=2, pady=2, sticky="e")    
        animation_assets_info_width_hoverbutton3 = HoverImageButton(animation_assets_info_width_entry_frame, tip_message="Multiply the height by the rate of 'idle'", image=image_tip_20, command=set_width_idle_rate_info)
        animation_assets_info_width_hoverbutton3.grid(row=0, column=3, padx=2, pady=2, sticky="e")    
        animation_assets_info_width_hover = HoverImage(frame_animation_info, tip_message="Current animation width", image=image_tip_20)
        animation_assets_info_width_hover.grid(row=5, column=2, pady=5, sticky="e")    
        animation_assets_info_height_var = tk.IntVar(value=768)
        animation_assets_info_height_label = tk.Label(frame_animation_info, text="Height", width=8, anchor='w')
        animation_assets_info_height_label.grid(row=6, column=0, pady=5, sticky="w")    
        animation_assets_info_height_entry_frame = tk.Frame(frame_animation_info)
        animation_assets_info_height_entry_frame.grid(row=6, column=1, sticky="w")    
        animation_assets_info_height_entry = tk.Entry(animation_assets_info_height_entry_frame, width=20, textvariable=animation_assets_info_height_var)
        animation_assets_info_height_entry.grid(row=0, column=0, pady=5, sticky="w")
        animation_assets_info_height_entry.bind("<KeyRelease>", on_animation_assets_info_size_change)
        def set_height_idle_info():
            global root_idle_height
            animation_assets_info_height_var.set(root_idle_height)
            on_animation_assets_info_size_change()
        def set_height_original_info():
            # 원래 크기 확인
            try:
                dir = './animation/' + animation_assets_label_dropdown.get() + '/' + animation_preview_label_dropdown.get()  # ./animation/(arona_png)/(idle_2)      
                files = os.listdir(dir)
                png_files = [file for file in files if file.endswith('.png')]
                first_png_file = os.path.join(dir, png_files[0])
                image = Image.open(first_png_file)
                width, height = image.size
                image.close()
                # 반영
                animation_assets_info_height_var.set(height)
                on_animation_assets_info_size_change()         
            except:
                global root_idle_height
                animation_assets_info_height_var.set(root_idle_height)
                on_animation_assets_info_size_change()
        def set_height_idle_rate_info():
            global root_idle_width, root_idle_height
            rate = 832/1216
            if root_idle_height and root_idle_width:
                rate = root_idle_height / root_idle_width
            origin_height = int(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_width'] * rate)
            animation_assets_info_height_var.set(origin_height)
            on_animation_assets_info_size_change()
        animation_assets_info_height_hoverbutton1 = HoverImageButton(animation_assets_info_height_entry_frame, tip_message="Set to the height of 'idle'", image=image_tip_20, command=set_height_idle_info)
        animation_assets_info_height_hoverbutton1.grid(row=0, column=1, padx=2, pady=2, sticky="e")    
        animation_assets_info_height_hoverbutton2 = HoverImageButton(animation_assets_info_height_entry_frame, tip_message="Set to the height of the original", image=image_tip_20, command=set_height_original_info)
        animation_assets_info_height_hoverbutton2.grid(row=0, column=2, padx=2, pady=2, sticky="e")    
        animation_assets_info_height_hoverbutton3 = HoverImageButton(animation_assets_info_height_entry_frame, tip_message="Multiply the width by the rate of 'idle'", image=image_tip_20, command=set_height_idle_rate_info)
        animation_assets_info_height_hoverbutton3.grid(row=0, column=3, padx=2, pady=2, sticky="e")           
        animation_assets_info_height_hover = HoverImage(frame_animation_info, tip_message="Current animation height", image=image_tip_20)
        animation_assets_info_height_hover.grid(row=6, column=2, pady=5, sticky="e")
        animation_assets_info_size_ratio_label = tk.Label(frame_animation_info, text="Size", width=8, anchor='w')
        animation_assets_info_size_ratio_label.grid(row=7, column=0, sticky="w")    
        animation_assets_info_size_ratio_slider = tk.Scale(frame_animation_info, from_=0.2, to=2, resolution=0.05, orient=tk.HORIZONTAL, length=240)
        animation_assets_info_size_ratio_slider.grid(row=7, column=1, sticky="w")
        animation_assets_info_size_ratio_slider.bind("<ButtonRelease-1>", on_animation_assets_info_size_change)  # 슬라이더에서 손 땠을때 이벤트 동작하게
        animation_assets_info_size_ratio_hover = HoverImage(frame_animation_info, tip_message="Current animation size rate", image=image_tip_20)
        animation_assets_info_size_ratio_hover.grid(row=7, column=2, sticky="e")

        def update_ground_slider_line(e):
            canvas_char_animation.delete("line")  # 기존 선 삭제
            # canvas_item 위치 계산
            canvas_height = canvas_char_animation.winfo_reqheight()  
            canvas_item_height = canvas_height
            bbox = canvas_char_animation.bbox(canvas_char_animation_item)
            if bbox: # 이미지 렌더링 전
                canvas_item_height = bbox[3] - bbox[1]
            y_position = (canvas_height-canvas_item_height) // 2 + int((1-float(animation_assets_info_ground_slider.get())) * canvas_item_height)
            canvas_char_animation.create_line(0, y_position, canvas_char_animation.winfo_reqwidth(), y_position, tags="line", fill="red")
            char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_ground'] = float(animation_assets_info_ground_slider.get())
            save_settings_eden(loaded_settings_eden)
            
        # 화면 표시용 (저장 없음)
        def refresh_ground_slider_line():
            canvas_char_animation.delete("line")  # 기존 선 삭제
            # canvas_item 위치 계산
            canvas_height = canvas_char_animation.winfo_reqheight()  
            canvas_item_height = canvas_height
            bbox = canvas_char_animation.bbox(canvas_char_animation_item)
            if bbox: # 이미지 렌더링 전
                canvas_item_height = bbox[3] - bbox[1]
            y_position = (canvas_height-canvas_item_height) // 2 + int((1-float(animation_assets_info_ground_slider.get())) * canvas_item_height)
            canvas_char_animation.create_line(0, y_position, canvas_char_animation.winfo_reqwidth(), y_position, tags="line", fill="red")
            # try: # animation assets 전환중일 경우, key error 발생
            char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_ground'] = float(animation_assets_info_ground_slider.get())
            # except:
                # pass

        animation_assets_info_ground_label = tk.Label(frame_animation_info, text="Ground", width=8, anchor='w')
        animation_assets_info_ground_label.grid(row=8, column=0, sticky="w")
        animation_assets_info_ground_slider = tk.Scale(frame_animation_info, from_=0, to=0.8, resolution=0.01, orient=tk.HORIZONTAL, length=240)
        animation_assets_info_ground_slider.grid(row=8, column=1, sticky="w")
        animation_assets_info_ground_slider.bind("<ButtonRelease-1>", update_ground_slider_line)  # 슬라이더에서 손 땠을때 이벤트 동작하게
        animation_assets_info_ground_hover = HoverImage(frame_animation_info, tip_message="Current animation bottom position\n(see red line on the right canvas)", image=image_tip_20)
        animation_assets_info_ground_hover.grid(row=8, column=2, sticky="e")
            
        folder_path = './animation/' + char_info['animation_assets']
        animation_preview_label_dropdown['values'] = [folder for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]
        animation_preview_label_dropdown.set('idle') 
        
        get_idle_info(char_info['animation_assets'])
        get_animation_assets_info('idle')  
        global animation_images_info, animation_images_cur_idx, animation_images_cur_dur 
        animation_images_info = get_animation_images_info(animation_preview_label_dropdown.get())
        animation_images_cur_idx = -1
        animation_images_cur_dur = 20
            
        # 초기값 반영
        animation_assets_info_is_used_checkbox_var.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['is_animation_use'])
        animation_assets_info_is_used_checkbox.config(state=tk.DISABLED)  # 초기 = idle 일때는 사용불능 비활성화 불가
        animation_assets_info_len_var.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_len'])
        # width 정보가 없을 경우 받아 옴 (있을 거 같은데...)
        if not char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_width']:
            if animation_images_info:
                width, height = animation_images_info[0]['image'].size        
                char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_width'] = width
            else:
                char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_width'] = 512
        animation_assets_info_width_var.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_width'])
        # height 정보가 없을 경우 받아 옴 
        if not char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_height']:
            if animation_images_info:
                width, height = animation_images_info[0]['image'].size        
                char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_height'] = height
            else:
                char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_height'] = 768
        animation_assets_info_height_var.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_height'])  
        animation_assets_info_size_ratio_slider.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_size'])
        animation_assets_info_ground_slider.set(char_info['animation_assets_info'][char_info['animation_assets']][animation_preview_label_dropdown.get()]['animation_ground'])

        # 프레임간 여백 추가
        frame_space = tk.Frame(frame_char_setting, height=10)
        frame_space.grid(row=frame_row_idx, column=0, sticky="nsew")
        frame_row_idx+=1

        ## animation_canvas
        frame_char_animation = tk.Frame(frame_char_detail_window, padx=5) # 반은 설정, 반은 애니메이션 용 cavnas
        frame_char_animation.grid(row=0, column=1, sticky="nsw")
        canvas_char_animation = tk.Canvas(frame_char_animation, width=400, height=600, bg='#3366FF')  # 스크롤바가 있는 캔버스 생성
        canvas_char_animation.grid(row=0, column=0, sticky="nsew", pady=(58,0))
        canvas_char_animation_item = canvas_char_animation.create_image(200, 300, anchor=tk.CENTER)
            
        refresh_ai_detail()

        # 초기화시 animation_images_cur_idx을 -1로 해야 0번부터 시작함
        def update_canvas_char_animation():
            global animation_images_info, animation_images_cur_idx, animation_images_cur_dur
            if char_detail_window.winfo_ismapped():     
                if animation_images_info: 
                    animation_images_cur_dur -= 20
                    if animation_images_cur_dur <= 0:
                        # 다음 애니메이션 재생
                        animation_images_cur_idx = (animation_images_cur_idx+1) % len(animation_images_info) 
                        image_info = animation_images_info[animation_images_cur_idx]
                        canvas_char_animation.itemconfig(canvas_char_animation_item, image=image_info['image_resized'])                                         
                        animation_images_cur_dur = image_info['frame_length']     
                refresh_ground_slider_line()  # line 갱신       
                char_detail_window.after(20, update_canvas_char_animation)   
        char_detail_window.after(20, update_canvas_char_animation)    

    def refresh_char_list():
        # 버튼 생성 (함수화 하면 이미지 부분이 작동을 안함, 클릭도 안 됨)
        char_button = dict()
        char_list = loaded_settings_eden['char_list']  # eden에서 긁어오기
        
        # 기존 버튼 삭제
        for frame in char_frames:
            # for widget in frame.winfo_children():
            #     widget.destroy()
            frame.grid_forget()
            
        button_length = 60    
        for i, char_name in enumerate(char_list):
            # 캐릭터버튼, 서브메뉴    
            x = i % 4
            y = i // 4
            frame_char_button = tk.Frame(frame_char, padx=5, pady=5)
            frame_char_button.grid(row=y, column=x, sticky="nsew")
            char_frames.append(frame_char_button)
            
            idle_png_path = ''
            char_info = get_char_info(char_name)
            if char_name in loaded_settings_eden and 'animation_assets' in loaded_settings_eden[char_name] and loaded_settings_eden[char_name]['animation_assets']:
                idle_folder_path = './animation/'+char_info['animation_assets']+'/idle'
                
                for image_char_setting_window, dirs, files in os.walk(idle_folder_path):  
                    # 이미지 주소 체크
                    images = []
                    for image in files:
                        if image.lower().endswith('.png'):
                            images.append(image)
                    # 있으면 활용
                    if images:
                        images.sort()
                        idle_png_path = idle_folder_path + '/' + images[0]
                
            image = image_unknown 
            if idle_png_path:
                image = Image.open(idle_png_path)

            # 버튼 resize
            width, height = image.size
            if width <= height:            
                image = image.resize((button_length, height * button_length // width))
            else:
                image = image.resize((width * button_length // height, button_length))
                
            # 버튼 커팅
            width, height = image.size
            top = 0
            bottom = button_length
            left = (width - button_length) // 2
            right = (width + button_length) // 2
            
            image = image.crop((left, top, right, bottom))  # 상반신 커팅
            
            # 원으로 자르기
            border_len = 5
            mask = Image.new("L", image.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, button_length, button_length), fill=255)
            result = Image.new("RGBA", (button_length, button_length))
            result.paste(image, mask=mask)
            
            # 배경 넣고 싶으면 주석 해제
            # background_color = (255, 0, 0, 100)  # White background color with full transparency
            # background = Image.new("RGBA", (button_length, button_length), background_color)
            # result = Image.alpha_composite(background, Image.new("RGBA", background.size))  # Copy the background
            # result.paste(image, mask=mask)
            
            # 테두리
            border_color = (0, 0, 0, 255) 
            border_width = 2
            draw_border = ImageDraw.Draw(result)
            draw_border.ellipse((0, 0, button_length, button_length), outline=border_color, width=border_width)
            
            image_tk = ImageTk.PhotoImage(result)
            char_images.append(image_tk)  # Store the PhotoImage object in the list

            def change_setting_char(name, char_button):     
                change_char_info = loaded_settings_eden[name]         
                def check_ai():
                    if 'ai_type' in change_char_info and change_char_info['ai_type'] == 'Local':
                        return True
                    return False

                def check_animation():
                    if 'animation_assets' in change_char_info and change_char_info['animation_assets']:
                        return True
                    return False
                
                def check_voice():
                    if 'voice_model' in change_char_info and change_char_info['voice_model']:
                        return True
                    return False
        
                text = "["+name+get_message("] : Change Character")
                if not check_ai():
                    text = text + get_message("\nNo 'AI' is set up.")
                if not check_animation():
                    text = text + get_message("\nNo 'Animation assets' is set up.")
                if not check_voice():
                    text = text + get_message("\nNo 'Voice' is set up.")
                
                ask_question_box = MessageBoxAskQuestion(char_setting_window,"Info", text)
                char_setting_window.wait_window(ask_question_box)
                if ask_question_box.result:
                    # 버튼 갱신
                    for button in char_buttons:
                        button.configure(bg="#f0f0f0")
                    loaded_settings['setting_char'] = name
                    char_button.configure(bg="green")
                    save_settings(loaded_settings)   
                                          
                    # 캐릭 변경시 창 파괴하며 리턴/콜백
                    on_char_setting_window_close(callback)
                
            char_button = tk.Button(frame_char_button, image=image_tk,
                                    width=button_length, height=button_length)
            char_button.grid(row=0, column=0, sticky="we")
            char_buttons.append(char_button)
            char_button.configure(command=lambda name=char_name, button=char_button: change_setting_char(name, button))
            if loaded_settings['setting_char'] == char_name:
                char_button.configure(bg="green")
            
            # 메인, 커피, 삭제
            char_info = loaded_settings_eden[char_name]
            
            frame_char_button_sub = tk.Frame(frame_char_button, pady=5)
            frame_char_button_sub.grid(row=1, column=0, sticky="nsew")
            
            def update_char_main(name, char_main_button):
                for button in char_main_buttons:
                    button.configure(bg="#f0f0f0")
                # 기존과 다른 캐릭터 > 갱신
                if loaded_settings_eden['char_main'] != name:
                    loaded_settings_eden['char_main'] = name
                    char_main_button.configure(bg="green")
                    MessageBoxShowInfo(char_setting_window, "Main Char Change", "["+name+get_message("] : Change Main Character"))
                # 기존과 같은 캐릭터 > 메인 제거
                else:
                    loaded_settings_eden['char_main'] = ''    
                save_settings_eden(loaded_settings_eden)
                
    
            char_main_button = tk.Button(frame_char_button_sub, image=image_check,
                                    width=button_length//4, height=button_length//4)
            char_main_button.grid(row=0, column=0, sticky="we", padx=1)
            char_main_buttons.append(char_main_button)
            char_main_button.configure(command=lambda name=char_name, button=char_main_button: update_char_main(name, button))
            if loaded_settings_eden['char_main'] == char_name:
                char_main_button.configure(bg="green")
                
            char_setting_button = tk.Button(frame_char_button_sub, image=image_setting, command=lambda name=char_name: open_char_setting_window(name),
                                    width=button_length//4, height=button_length//4)
            char_setting_button.grid(row=0, column=1, sticky="we", padx=1)
                
            def copy_char(name):
                def generate_copy_name(name):
                    base_name = f"{name}_copy"
                    name_set = set(char_list)
                    
                    if base_name not in name_set:
                        return base_name

                    for i in range(1, 101):  # 최대 100번까지 시도
                        new_name = f"{base_name}({i})"
                        if new_name not in name_set:
                            return new_name               
                    return ''

                new_name = generate_copy_name(name)
                if new_name:                
                    if name in loaded_settings_eden:
                        loaded_settings_eden[new_name] = deepcopy(loaded_settings_eden[name]) 
                        char_list.append(new_name)
                        refresh_char_list()
                        save_settings_eden(loaded_settings_eden)
                    else:
                        print('복사 대상의 정보가 불완전합니다.')            
            char_copy_button = tk.Button(frame_char_button_sub, image=image_copy, command=lambda name=char_name: copy_char(name),
                                    width=button_length//4, height=button_length//4)
            char_copy_button.grid(row=0, column=2, sticky="we", padx=1)
            
            def delete_char(name):
                if name == 'arona':
                    MessageBoxShowInfo(char_setting_window, "Cancel", "You cannot delete [arona].")
                    return                           
                if loaded_settings_eden['char_main'] == name:
                    MessageBoxShowInfo(char_setting_window, "Cancel", "You cannot delete the main character.")
                    return
                ask_question_box = MessageBoxAskQuestion(char_setting_window,"Confirm", "Do you really want to delete it?")
                char_setting_window.wait_window(ask_question_box)
                if ask_question_box.result:       
                    char_list = loaded_settings_eden['char_list']     
                    if name in char_list:
                        char_list.remove(name)
                    if name in loaded_settings_eden:
                        del loaded_settings_eden[name]
                    refresh_char_list()
                    save_settings_eden(loaded_settings_eden)                            
            char_del_button = tk.Button(frame_char_button_sub, image=image_delete, command=lambda name=char_name: delete_char(name),
                                    width=button_length//4, height=button_length//4)
            char_del_button.grid(row=0, column=3, sticky="we", padx=1)
        
        # 캐릭터 추가 버튼
        i += 1
        x = i % 4
        y = i // 4
        global frame_add_button
        if frame_add_button:
            frame_add_button.grid_forget()
        frame_add_button = tk.Frame(frame_char, padx=5, pady=5)
        frame_add_button.grid(row=y, column=x, sticky="nsew")

        def add_char():
            def add_char_confirm(name):            
                if not name:
                    MessageBoxShowInfo(add_char_window, "Cancel", "Please enter a name.") 
                    return     
                char_list = loaded_settings_eden['char_list']        
                if name in char_list:
                    MessageBoxShowInfo(add_char_window, "Cancel", "There is already a character with that name.") 
                    return
                # 캐릭 추가 전 저장
                loaded_settings_eden[name] = dict()
                save_settings_eden(loaded_settings_eden)
                
                add_char_window.destroy()         
                open_char_setting_window(name)
            add_char_window = tk.Toplevel(char_setting_window)
            add_char_window.title("New Character")
            add_char_window.geometry(f"180x80+{char_setting_window.winfo_x() + 100}+{char_setting_window.winfo_y() + 100}")

            add_char_label = tk.Label(add_char_window, text=get_message("Please enter a name."))
            add_char_label.pack(pady=3)

            add_char_entry = tk.Entry(add_char_window, width=20)
            add_char_entry.pack(pady=5)

            confirm_button = tk.Button(add_char_window, text=get_message("Confirm"), command=lambda: add_char_confirm(add_char_entry.get()))
            confirm_button.pack(pady=2)

        button_length = 60
        char_button = tk.Button(frame_add_button, image=image_add, command=add_char, width=button_length+16, height=button_length)
        char_button.grid(row=0, column=0, sticky="we")    

    loaded_settings = load_settings()    
    loaded_settings_eden = load_settings_eden()   
    
    # 초기 arona, mari 세팅
    arona_dict = get_char_info('arona')
    arona_dict['animation_assets'] = 'arona_imagine31_2'
    loaded_settings_eden['arona'] = arona_dict
    mari_dict = get_char_info('mari')
    mari_dict['animation_assets'] = 'arona_imagine31_2'
    loaded_settings_eden['mari'] = mari_dict
    
    def on_char_setting_window_close(callback):
        # 종료전 쓰레기 정리
        global frame_add_button
        frame_add_button = None
        
        # 콜백으로 변경 캐릭터 적용
        save_settings(loaded_settings)
        save_settings_eden(loaded_settings_eden)
        callback(loaded_settings['setting_char'])
        char_setting_window.destroy()
    
    # tkinter 시작
    char_setting_window = tk.Toplevel(root_parent)
    char_setting_window.title("Character Setting")
    char_setting_window.geometry("430x310")
    char_setting_window.focus_force()
    char_setting_window.lift()
    char_setting_window.protocol("WM_DELETE_WINDOW", lambda: on_char_setting_window_close(callback))
    
    # 초기화
    frame_row_idx = 0
        
    # Frame 캐릭터 (+ 스크롤)
    canvas_char = tk.Canvas(char_setting_window, width=410, height=300, bg="#f0f0f0")# bg='yellow')  # 스크롤바가 있는 캔버스 생성
    canvas_char.grid(row=frame_row_idx, column=0, sticky="nsew")
    scrollbar = ttk.Scrollbar(char_setting_window, orient="vertical", command=canvas_char.yview)
    scrollbar.grid(row=frame_row_idx, column=1, sticky="nsew")
    frame_row_idx+=1 
    frame_char = ttk.Frame(canvas_char)

    canvas_char.create_window((0, 0), window=frame_char, anchor="nw")
    canvas_char.configure(yscrollcommand=scrollbar.set)

    # 프레임 크기 변경 시 스크롤범위 설정
    def on_frame_char_configure(event):
        canvas_char.configure(scrollregion=canvas_char.bbox("all"))
    frame_char.bind("<Configure>", on_frame_char_configure)
    
    button_length = 60
    image_add = ImageTk.PhotoImage(Image.open('./assets/png/add.png').resize((button_length, button_length)))
    image_check = ImageTk.PhotoImage(Image.open('./assets/png/check.png').resize((button_length//4, button_length//4)))
    image_setting = ImageTk.PhotoImage(Image.open('./assets/png/setting.png').resize((button_length//4, button_length//4)))
    image_copy = ImageTk.PhotoImage(Image.open('./assets/png/copy.png').resize((button_length//4, button_length//4)))
    image_delete = ImageTk.PhotoImage(Image.open('./assets/png/delete.png').resize((button_length//4, button_length//4)))
    image_unknown = Image.open("./assets/png/input3.png").resize((button_length, button_length))
    image_tip_20 = ImageTk.PhotoImage(Image.open('./assets/png/question.png').resize((20, 20)))
    
    # 캐릭터 관리 화면 관련 변수.
    char_images = []
    char_frames = []
    char_buttons = []
    char_main_buttons = []
    refresh_char_list()
  
    char_setting_window.mainloop()

if __name__ == "__main__":    
    import logging
    
    log = logging.getLogger('PIL')
    log.setLevel(logging.CRITICAL)
    log = logging.getLogger('numba.core.ssa')
    log.setLevel(logging.CRITICAL)
    
    # 초기화
    pygame.mixer.init()
    
    root = tk.Tk()
    open_char_setting(root, print)
    
    root.mainloop()
    
    
