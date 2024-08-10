# 개발 모드
DEV_MODE = True

if not DEV_MODE or True:
    import logging  # PIL, hpack 등 logger 쓰는 라이브러리가 너무 날뜀
    logging.disable(logging.INFO) # disable INFO and DEBUG logging everywhere
    logging.disable(logging.DEBUG) # disable INFO and DEBUG logging everywhere
    logging.disable(logging.WARNING) # disable WARNING, INFO and DEBUG logging everywhere

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass  # pyinstaller에서는 noconsole에서 sys.stdout 가 None 임
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')  # print가 cp-949 오류 내는 경우를 막아줌

import gc
import threading
import time
import tkinter as tk
from tkinter import Scale, ttk, filedialog
from PIL import Image, ImageTk, ImageDraw, ImageFont, ImageOps
import random
import os
import json
import keyboard
import webbrowser
import queue
import numpy as np
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # 끔찍한 로그덩어리 pygame
import pygame
import queue

import speech_recognition as sr
from speech_recognition.audio import AudioData

# Local module
from messages import getMessage
from inference_ko import synthesize_char
from screeninfo import get_monitors
import memory

import state
import ai_intent_reader
import ai_web_search
import ai_conversation
import ai_singleton

from util_screenshot import ScreenshotApp
import googletrans # 번역 관련
from proper_nouns import change_to_jp, change_to_ko  # 고유명사 번역

is_program_ended = False
is_use_cuda = False

# 전역 변수
loaded_settings = dict()

is_chatting = False  # 입력을 받아들일 수 있는지.


question = ''
query_ai_translation_question = ''
query_ai_intent = ''
query_ai_rag_story = ''
query_ai_conversation = ''
query_ai_translation_jp = ''
query_ai_translation_ko = ''
query_ai_translation_en = ''
latest_ai_module = ''  # regenerate 용

translator_google = googletrans.Translator()
response_ai_translation_jp = ''
response_ai_translation_ko = ''

answer_balloon = None
ask_balloon = None

loading_screen_text = "Start Loading...\n"
loading_message_box = None

setting_lang = 'en'

# thread 관련
whisper_model = None
audio_queue = queue.Queue()

talk_thread = None
talk_thread_test = None

tikitaka_thread = None
tikitaka_status_thread = None
faster_whisper_listener = None

chat_key_thread = None  # 채팅시작 키보드 인식 관련
is_chat_key_thread_activated = False  # Test와 공유

loading_screen_thread = None

wav_thread = None
wav_event = None

# 서버 관련
llama_server = None

# 음성인식 관련
recognizer = None
is_talk_thread_activated  = False
is_sr_test = False
sr_test_text = ''

# 화면인식 관련
is_focus = False
screenshotApp = None
screenshotApp_thread = None

# tkinter 변수
status_balloon = None
ask_balloon = None
root_frame_width = 512  # root 현재 재생 프레임 넓이
root_frame_height = 768  # root 현재 재생 프레임 높이

# pygame Audio 변수
global_sound = None
global_sound_queue = queue.Queue()
global_sound_queue_history = list()  # 다시 재생
global_sound_idx = 0  # 현재 답변의 idx 확인용

status = ''  # 시작은 fall
anim_idx = 0  # stauts 애니메이션들 중 X번째 애니메이션
anim_ground = 0  # 현재 재생 애니메이션 땅에서부터의 높이
anim_lock = False # 자체 change animation 불가
# anim_is_ground = False
frame_idx = 0  # 재생중 프레임
duration_anim = 200  # 애니메이션 총 지속시간, 낙하 후 0.2초 동안 update 없음
duration_frame = 0  # 같은 애니메이션 내 지속시간
is_dragging = False
is_chatting = False  # 채팅 입력부터 발언까지 전반
is_falling = True
fall_delta = 80  # 80ms 정도는 set_status('fall')이 되지 않음
status_delta = 50  # 50ms 정도는 set_status('idle')예외가 되지 않음
is_waiting = False  # 세팅 등으로 대기중

root_idle_width = 512  # 완전 초기값
root_idle_height = 768
root_frame_width = 512  # root 현재 재생 프레임 넓이
root_frame_height = 768  # root 현재 재생 프레임 높이
window_bottom = None  # 모니터의 최소 높이

# 모니터 정보
monitor_main = None
monitor_current = None
monitor_adj_x, monitor_adj_y = 0, 0  # x, y 모니터 대비 상대적 위치 계산용
monitor_screen_width, monitor_screen_height = 1920, 1080  # 화면 가로 세로 크기 재설정

# chat window
chat_window = None

char_info = {
    "voice_model": "arona_m9dev",
    "voice_type": "multi",
    "voice_sid": 10,
    "voice_speed": 0,
    "voice_volume": 0,
    "animation_assets": "arona_imagine31_2",
    "animation_assets_info": {
        "arona_imagine31_2": {
        "idle": {
          "is_animation_use": True,
          "animation_len": 5000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.5,
          "animation_ground": 0.02
        },
        "pick": {
          "is_animation_use": True,
          "animation_len": 3000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.4,
          "animation_ground": 0.0
        },
        "pick_2": {
          "is_animation_use": True,
          "animation_len": 3000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.4,
          "animation_ground": 0.0
        },
        "pick_3": {
          "is_animation_use": True,
          "animation_len": 3000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.4,
          "animation_ground": 0.0
        },
        "sit": {
          "is_animation_use": True,
          "animation_len": 5000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.4,
          "animation_ground": 0.13
        },
        "sit_2": {
          "is_animation_use": True,
          "animation_len": 5000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.45,
          "animation_ground": 0.23
        },
        "sit_3": {
          "is_animation_use": True,
          "animation_len": 5000,
          "animation_width": 320,
          "animation_height": 512,
          "animation_size": 0.5,
          "animation_ground": 0.08
        },
        "sit_4": {
          "is_animation_use": True,
          "animation_len": 5000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.5,
          "animation_ground": 0.18
        },
        "sit_6": {
          "is_animation_use": True,
          "animation_len": 5000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.45,
          "animation_ground": 0.32
        },
        "sit_5": {
          "is_animation_use": True,
          "animation_len": 5000,
          "animation_width": 320,
          "animation_height": 512,
          "animation_size": 0.45,
          "animation_ground": 0.08
        },
        "sit_7": {
          "is_animation_use": True,
          "animation_len": 5000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.4,
          "animation_ground": 0.28
        },
        "smile": {
          "is_animation_use": True,
          "animation_len": 3000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.45,
          "animation_ground": 0.0
        },
        "smile_2": {
          "is_animation_use": True,
          "animation_len": 3000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.45,
          "animation_ground": 0.0
        },
        "talk": {
          "is_animation_use": True,
          "animation_len": 3000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.5,
          "animation_ground": 0.02
        },
        "fall": {
          "is_animation_use": True,
          "animation_len": 3000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.4,
          "animation_ground": 0.0
        },
        "fall_2": {
          "is_animation_use": True,
          "animation_len": 3000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.4,
          "animation_ground": 0.0
        },
        "fall_3": {
          "is_animation_use": True,
          "animation_len": 3000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.4,
          "animation_ground": 0.0
        },
        "pick_4": {
          "is_animation_use": True,
          "animation_len": 3000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.4,
          "animation_ground": 0.0
        },
        "pick_5": {
          "is_animation_use": True,
          "animation_len": 3000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.4,
          "animation_ground": 0.0
        },
        "pick_6": {
          "is_animation_use": True,
          "animation_len": 3000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.4,
          "animation_ground": 0.0
        },
        "think": {
          "is_animation_use": True,
          "animation_len": 3000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.5,
          "animation_ground": 0.0
        },
        "think_2": {
          "is_animation_use": True,
          "animation_len": 3000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.5,
          "animation_ground": 0.0
        },
        "think_3": {
          "is_animation_use": True,
          "animation_len": 3000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.5,
          "animation_ground": 0.0
        },
        "walk": {
          "is_animation_use": True,
          "animation_len": 2000,
          "animation_width": 413,
          "animation_height": 604,
          "animation_size": 0.5,
          "animation_ground": 0.0
        }
      }
    },
    "local_name": "arona",
    "local_model": "",
    "local_prompt": "arona is a self-proclaimed high-performance AI.\narona is an AI, but she can eat, drink and feel emotions.\narona is the OS of the mysterious tablet 'Shiddim Chest' and serves as the system administrator.\nIn 'Siddim Chest', there is a desolate classroom located in the midst of a watery expanse, and arona lives in it.\narona accompanies {player} throughout their adventure in Kivotos as a guide.\narona calls {player} teacher.\n\narona has a child-like personality and is quite gullible, often falling for {player}'s jokes.\narona thoroughly enjoys sweets, being quick to abandon a diet for the sake of sweets—or even breaking into tears from being denied them.\nWhen arona is asked about something don't know, arona honestly respond that arona don't know about it.\narona has Super AI Functions. As a powerful AI, arona originally had authority over many functions in Kivotos. \narona herself still has incredible power as an AI, able to fend off any hacking attempt.\narona has the power to negate damage dealt to {player}, but this power has an energy limit.\n",
    "local_memory_len": 5,
    "local_knowledge": []
}

######################################################################
# 로딩 옵션 스크린
class LoadingOptionScreen:
    def __init__(self, master):
        self.master = master
        self.master.title("Select Option")
        self.master.geometry("300x200")
        icon_path = 'assets/ico/icon_arona.ico'
        self.master.iconbitmap(icon_path)
        self.custom_window = None
        self.confirmed = False  # 확인으로 종료되었을때 다음 단계

        # Title Label
        self.title_label = ttk.Label(master, text="Select Option", anchor="center", font=("Arial", 14))
        self.title_label.pack(pady=10)

        # frame_gpu for Radio Buttons
        self.frame_gpu = ttk.Frame(master)
        self.frame_gpu.pack(pady=10)

        # Option Variable
        self.option_var2 = tk.StringVar(value=self.load_option2())

        # Radio Buttons
        self.cpu_radio = ttk.Radiobutton(self.frame_gpu, text="CPU", variable=self.option_var2, value="CPU", command=self.toggle_radio_buttons)
        HoverTip(self.cpu_radio, "Use CPU for Normal response.")
        self.gpu_radio = ttk.Radiobutton(self.frame_gpu, text="GPU", variable=self.option_var2, value="GPU", command=self.toggle_radio_buttons)
        HoverTip(self.gpu_radio, "Use Nvidia GPU for fast response.\n(VRAM about 8~10GB needed)")

        self.cpu_radio.pack(side='left', padx=5)
        self.gpu_radio.pack(side='left', padx=5)

        # Frame for Radio Buttons
        self.frame = ttk.Frame(master)
        self.frame.pack(pady=10)

        # Option Variable
        self.option_var = tk.StringVar(value=self.load_option())

        # Checked Options Example
        self.checked_options = self.load_options_customlist()

        # Radio Buttons
        self.fast_radio = ttk.Radiobutton(self.frame, text="Fast", variable=self.option_var, value="Fast")
        HoverTip(self.fast_radio, "Fast loading with minimal settings")
        self.normal_radio = ttk.Radiobutton(self.frame, text="Normal", variable=self.option_var, value="Normal")
        HoverTip(self.normal_radio, "Default. Enable all options")
        self.custom_radio = ttk.Radiobutton(self.frame, text="Custom", variable=self.option_var, value="Custom", command=self.open_custom_window)
        HoverTip(self.custom_radio, "Custom. Proceed with the selected option")

        self.fast_radio.pack(side='left', padx=5)
        self.normal_radio.pack(side='left', padx=5)
        self.custom_radio.pack(side='left', padx=5)
        self.toggle_radio_buttons()  # 라디오버튼 활성화

        # Confirm Button
        self.confirm_button = ttk.Button(master, text="확인", command=self.on_confirm)
        self.confirm_button.pack(anchor='e', pady=10, padx=10)
        
        # self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def load_option(self):
        global loaded_settings
        return loaded_settings['setting_load_option']
    
    def load_option2(self):
        global loaded_settings
        return loaded_settings['setting_program_type']
    
    def load_options_customlist(self):
        global loaded_settings
        return loaded_settings['setting_load_option_customlist']       

    def save_option(self):
        global loaded_settings, is_use_cuda
        loaded_settings['setting_load_option'] = self.option_var.get()
        loaded_settings['setting_program_type'] = self.option_var2.get()
        if not loaded_settings['setting_program_type'] == 'CPU':
            is_use_cuda = True
        save_settings()

    def open_custom_window(self):
        if self.custom_window and tk.Toplevel.winfo_exists(self.custom_window):
            self.custom_window.focus()
            self.custom_window.lift()
            return
        
        self.custom_window = tk.Toplevel(self.master)
        self.custom_window.title("Options")
        icon_path = 'assets/ico/icon_arona.ico'
        self.custom_window.iconbitmap(icon_path)

        # Checkboxes Variables
        self.conv_var = tk.IntVar(value=1 if 'conversation' in self.checked_options else 0)
        self.web_var = tk.IntVar(value=1 if 'web' in self.checked_options else 0)
        self.story_var = tk.IntVar(value=1 if 'story' in self.checked_options else 0)
        self.short_memory_var = tk.IntVar(value=1 if 'S.memory' in self.checked_options else 0)
        self.long_memory_var = tk.IntVar(value=1 if 'L.memory' in self.checked_options else 0)
        self.translation_var = tk.IntVar(value=1 if 'translation' in self.checked_options else 0)
        self.image_var = tk.IntVar(value=1 if 'image.R' in self.checked_options else 0)
        self.sound_var = tk.IntVar(value=1 if 'sound.R' in self.checked_options else 0)

        def on_custom_window_close():
            global loaded_settings
            self.checked_options.clear()
            if self.conv_var.get():
                self.checked_options.append('conversation')
            if self.web_var.get():
                self.checked_options.append('web')
            if self.story_var.get():
                self.checked_options.append('story')
            if self.translation_var.get():
                self.checked_options.append('translation')
            if self.long_memory_var.get():
                self.checked_options.append('S.memory')
            if self.long_memory_var.get():
                self.checked_options.append('L.memory')
            if self.image_var.get():
                self.checked_options.append('image.R')
            if self.sound_var.get():
                self.checked_options.append('sound.R')
            loaded_settings['setting_load_option_customlist'] = self.checked_options
            save_settings()               
            self.custom_window.destroy()

        self.custom_window.protocol("WM_DELETE_WINDOW", on_custom_window_close)

        # Checkboxes
        conv_check = ttk.Checkbutton(self.custom_window, text="Conversation", variable=self.conv_var, state='disabled')
        HoverTip(conv_check, "Default conversations")
        web_check = ttk.Checkbutton(self.custom_window, text="Web", variable=self.web_var)
        HoverTip(web_check, "Web search results are reflected in the answer")
        story_check = ttk.Checkbutton(self.custom_window, text="Story", variable=self.story_var, state='disabled')
        HoverTip(story_check, "Enables conversations about Story elements.")
        translation_check = ttk.Checkbutton(self.custom_window, text="Translation", variable=self.translation_var, state='disabled')
        HoverTip(translation_check, "Translation with AI. Resourcefully not recommended.")
        short_memory_check = ttk.Checkbutton(self.custom_window, text="S.Memory", variable=self.short_memory_var)
        HoverTip(short_memory_check, "Short-term memory. Reflects recent conversations in the conversation.")
        long_memory_check = ttk.Checkbutton(self.custom_window, text="L.Memory", variable=self.long_memory_var)
        HoverTip(long_memory_check, "Long-term memory. It remembers user characteristics and reflects them in conversations.")
        image_check = ttk.Checkbutton(self.custom_window, text="Image.R", variable=self.image_var)
        HoverTip(image_check, "Image recognition. Enables conversations about images\nwithin a specified range or dragged and dropped images.")
        sound_check = ttk.Checkbutton(self.custom_window, text="Sound.R", variable=self.sound_var)
        HoverTip(sound_check, "Speech recognition. Enables direct conversation with AI via microphone")

        # Grid Layout for Checkboxes
        conv_check.grid(row=0, column=0, padx=5, pady=2, sticky='w')
        web_check.grid(row=0, column=1, padx=5, pady=2, sticky='w')
        story_check.grid(row=1, column=0, padx=5, pady=2, sticky='w')
        translation_check.grid(row=1, column=1, padx=5, pady=2, sticky='w')
        short_memory_check.grid(row=2, column=0, padx=5, pady=2, sticky='w')
        long_memory_check.grid(row=2, column=1, padx=5, pady=2, sticky='w')
        image_check.grid(row=3, column=0, padx=5, pady=2, sticky='w')
        sound_check.grid(row=3, column=1, padx=5, pady=2, sticky='w')
        
    def toggle_radio_buttons(self):
        state = tk.NORMAL if self.option_var2.get() == 'CPU' else tk.DISABLED
        self.fast_radio.config(state=state)
        self.normal_radio.config(state=state)
        self.custom_radio.config(state=state)
        
    def on_confirm(self):
        self.confirmed = True
        self.save_option()
        self.master.destroy()


# 로딩 스크린
class LoadingScreen:
    def __init__(self, loading_root):
        self.loading_root = loading_root
        
        # 화면 가로, 세로 크기
        screen_width = loading_root.winfo_screenwidth()
        screen_height = loading_root.winfo_screenheight()
        
        # 로딩 화면의 가로, 세로 크기 및 위치 설정
        width = 350
        height = 400
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.loading_root.geometry(f"{width}x{height}+{x}+{y}")
        
        self.loading_frame = tk.Frame(self.loading_root)
        self.loading_frame.grid(row=0, column=0, sticky="nsw")

        self.loading_root.overrideredirect(True)
        self.loading_root.wm_attributes('-topmost', 90)

        # GIF를 프레임으로 분할하여 리스트에 저장
        self.frames = []
        self.frame_delays = []
        gif_path = "./assets/gif/mari_move.gif"
        self.load_frames(gif_path)

        # 첫 번째 프레임을 초기 이미지로 설정
        self.current_frame = 0
        self.loading_label = tk.Label(self.loading_frame, image=self.frames[self.current_frame], borderwidth=2, relief="solid",width=300, height=300, anchor='n')
        self.loading_label.grid(row=0, column=0, padx=25, pady=(20,0))

        # 로딩 텍스트를 표시할 Label 생성
        self.loading_text_label = tk.Label(self.loading_frame, text="Loading...", anchor='n', justify='left', bg="yellow")
        self.loading_text_label.grid(row=1, column=0, pady=10)

        # 프레임 전환을 위한 스레드 시작
        self.anim_thread = threading.Thread(target=self.animate_frames)
        self.anim_thread.start()
        
        # 텍스트 전환을 위한 스레드 시작
        self.text_thread = threading.Thread(target=self.update_loading_text)
        self.text_thread.start()
        
        # 로딩화면 종료를 위한 스레드 시작
        self.destroy_thread = threading.Thread(target=self.check_is_loading)
        self.destroy_thread.start()

    def load_frames(self, gif_path):
        gif = Image.open(gif_path)
        width, height = gif.size
        top = 0
        bottom = 300
        left = (width - 300) // 2
        right = (width + 300) // 2
        
        while True:
            try:
                frame = ImageTk.PhotoImage(gif.crop((left, top, right, bottom)).resize((300,300)).copy())  # 상반신 커팅 후 resize
                delay = gif.info['duration']  # 각 프레임의 지연 시간
                self.frames.append(frame)
                self.frame_delays.append(delay)
                gif.seek(gif.tell() + 1)
            except EOFError:
                break

    def check_is_loading(self):
        def kill_loading_root():
            global loading_root
            loading_root.destroy()
        global is_loading
        while is_loading:
            time.sleep(0.1)  # 0.1초마다 체크

        loading_root.after(10, kill_loading_root)

    def animate_frames(self):
        global is_loading
        while is_loading:  # 로딩 중일 때만 애니메이션을 재생
            # 프레임을 전환하여 GIF 애니메이션 효과 구현
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.loading_label.config(image=self.frames[self.current_frame])
            delay = self.frame_delays[self.current_frame] / 1000  # 밀리초를 초로 변환
            time.sleep(delay)

    def update_loading_text(self):
        global is_loading, loading_screen_text
        while is_loading:  # 로딩 중일 때만 텍스트 갱신
            # 로딩 텍스트 갱신
            self.loading_text_label.config(text=loading_screen_text)
            time.sleep(0.1)  # 0.1초마다 갱신

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
            
# 음성인식확인 말풍선 (answer: dict)
class SRBalloon(tk.Toplevel):
    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        
        self.text = text
        self.text_var = tk.StringVar(value=text)
        self.is_edit_mode = False  # 수정 모드 플래그
        
        self.canvas_width = 400
        self.canvas_height = 500
        self.overrideredirect(True)  # 창 장식(border) 제거
        self.attributes("-topmost", 99)  # 항상 최상위에 표시
        self.wm_attributes('-transparentcolor', '#306198')
        self.geometry(f"{self.canvas_width}x500+{root.winfo_x()}+{root.winfo_y()}")
        
        self.prev_x, self.prev_y = 0, 0
        
        # canvas 만들고
        self.canvas = tk.Canvas(self, width=self.canvas_width, highlightthickness=0, borderwidth=0, bd=0, bg='#306198')
        self.canvas.pack()
        self.create_text(self.text_var.get())
        self.create_image()

        self.close_btn = tk.Label(self, image=close_img, cursor="hand2", bg='#CFE9FE')
        self.close_btn.place(x=self.canvas_width - 28, y=3)
        self.close_btn.bind("<Button-1>", lambda e: self.kill_balloon())
        
        # 말풍선 내용을 표시하는 텍스트 추가
        self.text_widget = tk.Text(self.canvas, wrap=tk.WORD, width=30, height=3, background='white', font=("Noto Sans", 12, "bold"))
        self.text_window = self.canvas.create_window((self.canvas_width//2, self.canvas_height//2), window=self.text_widget, anchor='center')
        self.canvas.itemconfig(self.text_window, state='hidden')

        # 우측 하단 버튼들
        self.btns = list()
        buttons = [
            ("수정", img_modify, self.modify_mode, True), 
            ("보내기", send_img, self.send, True)
        ]
        x_offset = self.canvas_width - (25 * len(buttons)) - 3  # 버튼들을 오른쪽 하단에 정렬하기 위해 x 위치 계산
        y_offset = self.canvas_height - 30  # 버튼들의 y 위치
        i = 0
        for text, img, command, is_able in buttons:
            if is_able:
                btn = tk.Label(self, image=img, cursor="hand2", bg='#CFE9FE')
            else:
                btn = tk.Label(self, image=img, cursor="hand2", bg='#696969')
            btn.place(x=x_offset + (i * 25), y=y_offset)
            self.btns.append(btn)
            i += 1
            if command and is_able:
                btn.bind("<Button-1>", lambda e, cmd=command: cmd())
        self.modify_btn = self.btns[0]
        
        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        
    def create_text(self, text):
        self.text_label = self.canvas.create_text(self.canvas_width // 2, 0, text=text, anchor='center', fill="black", width=self.canvas_width - 60, font=("Noto Sans", 12, "bold"))
        x0, y0, x1, y1 = self.canvas.bbox(self.text_label)
        self.canvas_height = int(y1 - y0 + 60)
        self.canvas.config(height=self.canvas_height)
        self.canvas.move(self.text_label, 0, self.canvas_height // 2)
        self.geometry(f"{self.canvas_width}x{self.canvas_height}+{root.winfo_x()}+{root.winfo_y() - self.canvas_height - 30}")

    def create_image(self):
        global img_input
        img_input_resized = img_input.resize((self.canvas_width, self.canvas_height))
        self.photo = ImageTk.PhotoImage(img_input_resized)
        self.canvas_image = self.canvas.create_image(self.canvas_width // 2, 0, anchor='n', image=self.photo)
        self.canvas.itemconfig(self.canvas_image, image=self.photo)
        self.canvas.tag_raise(self.text_label, self.canvas_image)
        
    def reloc_btns(self):
        # 버튼 재정렬
        x_offset = self.canvas_width - (25 * len(self.btns)) - 3  # 버튼들을 오른쪽 하단에 정렬하기 위해 x 위치 계산
        y_offset = self.canvas_height - 30  # 버튼들의 y 위치
        i = 0
        for btn in self.btns:
            btn.place(x=x_offset + (i * 25), y=y_offset)
            i += 1        

    def modify_text(self, modified_text):
        self.canvas.delete(self.text_label)
        self.canvas.delete(self.canvas_image)
        self.text_var.set(modified_text)
        self.create_text(modified_text)
        self.create_image()
        self.reloc_btns()

    def kill_balloon(self):
        global ask_balloon
        ask_balloon = None
        self.photo = None
        self.destroy()  
        
    def on_press(self, event):
        self.prev_x, self.prev_y = event.x, event.y

    def on_drag(self, event):
        deltax = event.x - self.prev_x
        deltay = event.y - self.prev_y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def on_double_click(self, event):
        self.clipboard_clear()
        selected_text = self.canvas.itemcget(self.text_label, "text")
        self.clipboard_append(selected_text)
    
    def send(self):
        # 편집중이고 내용이 있을 경우 그걸로 set
        if self.is_edit_mode:
            new_text = self.text_widget.get("1.0", tk.END).strip()
            if new_text:  # 텍스트 위젯의 내용이 비어있지 않으면
                self.text_var.set(new_text)
                self.text = new_text
        root.after(0, send_chat_wrapper, self.text_var.get())
        self.kill_balloon()

    def modify_mode(self):
        if not self.is_edit_mode:
            self.is_edit_mode = True
            self.text_widget.delete("1.0", tk.END)  # 텍스트 위젯을 초기화
            self.text_widget.insert(tk.END, self.text_var.get())  # 텍스트 위젯에 텍스트 변수 값 설정
            self.canvas.itemconfig(self.text_label, state='hidden')
            self.canvas.itemconfig(self.text_window, state='normal')
            self.modify_btn.config(image=answer_balloon_detail_img)
        else:
            self.is_edit_mode = False
            new_text = self.text_widget.get("1.0", tk.END).strip()
            if new_text:  # 텍스트 위젯의 내용이 비어있지 않으면
                self.text_var.set(new_text)
                self.text = new_text
            else:  # 텍스트 위젯의 내용이 비어있으면 원래 텍스트 유지
                self.text_var.set(self.text)
            self.modify_text(self.text_var.get())
            self.canvas.itemconfig(self.text_window, state='hidden')
            self.canvas.itemconfig(self.text_label, state='normal')
            self.modify_btn.config(image=img_modify)

# 채팅 말풍선
class ChatBalloon(tk.Toplevel):
    def __init__(self, **kwargs):
        global chat_window, img_input
        super().__init__(**kwargs)
        
        self.canvas_width = 300
        self.canvas_height = 200
        self.overrideredirect(True)  # 창 장식(border) 제거
        self.attributes("-topmost", 99)  # 항상 최상위에 표시
        self.wm_attributes('-transparentcolor', '#5A6D89')
        self.geometry(f"{self.canvas_width}x{self.canvas_height}+{root.winfo_x()}+{root.winfo_y()-self.canvas_height-20}")
        
        chat_window = self

        self.prev_x, self.prev_y = 0, 0
        
        # canvas 만들고
        self.canvas = tk.Canvas(self, width=self.canvas_width, highlightthickness=0, borderwidth=0, bd=0, bg='#306198')
        self.canvas.pack()
        
        resized_image = img_input.resize((self.canvas_width, self.canvas_height))  # 이미지 크기를 조정합니다.
        self.photo = ImageTk.PhotoImage(resized_image)
        self.canvas_image = self.canvas.create_image(self.canvas_width//2, 0, anchor='n', image=self.photo)
        self.canvas.itemconfig(self.canvas_image, image=self.photo)
        # self.canvas.tag_raise(self.text_label, self.text_widget)
        
        # 말풍선 내용을 표시하는 텍스트 추가
        self.text_widget = tk.Text(self.canvas, wrap=tk.WORD, width=30, height=7, background='white', font=("Noto Sans", 12, "bold"))
        self.canvas.create_window((self.canvas_width//2, self.canvas_height//2), window=self.text_widget, anchor='center')
        
        self.text_widget.bind('<Return>', self.close_window)
        # self.canvas.tag_raise(self.text_widget, self.canvas_image)
        
        self.close_btn = tk.Label(self, image=close_img, cursor="hand2", bg='#CFE9FE')
        self.close_btn.place(x=self.canvas_width - 28, y=3)
        self.close_btn.bind("<Button-1>", lambda e: self.kill_balloon())

        # 우측 하단 버튼들
        global screenshotApp
        self.btns = list()
        buttons = [
            ("Input Image", image_img, screenshotApp.create_dnd_toplevel, True),
            ("Web Search", search_img, self.close_window_web, True),
            ("Send", send_img, self.close_window, True),
        ]
        x_offset = self.canvas_width - (25 * len(buttons)) - 3  # 버튼들을 오른쪽 하단에 정렬하기 위해 x 위치 계산
        y_offset = self.canvas_height - 30  # 버튼들의 y 위치
        i = 0
        for text, img, command, is_able in buttons:
            if is_able:
                btn = tk.Label(self, image=img, cursor="hand2", bg='#CFE9FE')
            else:
                btn = tk.Label(self, image=img, cursor="hand2", bg='#696969')
            btn.place(x=x_offset + (i * 25), y=y_offset)
            self.btns.append(btn)
            i += 1
            if text:
                HoverTip(btn, text)
            if command and is_able:
                btn.bind("<Button-1>", lambda e, cmd=command: cmd())
        
        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)

    def close_window(self, event=None):
        global is_chatting, chat_window
        text = self.text_widget.get("1.0", "end-1c")

        self.photo = None
        chat_window = None
        self.destroy()
       
        if text:
            sound_length, answer = send_chat(text)
            if answer:
                sound_length = 999  # $$$ 임시
                root.after(0, show_answer_balloon, sound_length, answer)
            # chat_question = text  # chat_listener가 가져감        
        else:
            set_status('idle')
            is_chatting = False

    def close_window_web(self, event=None):
        global is_chatting, chat_window
        text = self.text_widget.get("1.0", "end-1c")
        if text:    
            self.photo = None
            chat_window = None
            self.destroy()
            
            trans_question = translator_google.translate(text, dest='en').text    
            conversation_web(trans_question)
        else:
            return

    def kill_balloon(self):
        global is_chatting, chat_window
        
        self.photo = None
        chat_window = None
        
        set_status('idle')
        is_chatting = False
        
        self.destroy()  
        
    def on_press(self, event):
        self.prev_x, self.prev_y = event.x, event.y

    def on_drag(self, event):
        deltax = event.x - self.prev_x
        deltay = event.y - self.prev_y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

# 답변 말풍선 (answer: dict)
class AnswerBalloon(tk.Toplevel):
    img_output = None
    close_img = None
    answer_balloon_stop_img = None
    answer_balloon_translate_img = None
    answer_balloon_speaker_img = None
    answer_balloon_regenerate_img = None
    answer_balloon_cancel_img = None
    
    @classmethod
    def set_images(cls):
        cls.img_output = Image.open('./assets/png/output2.png') 
        cls.close_img = ImageTk.PhotoImage(Image.open("./assets/png/close.png").resize((20, 20)))
        
        cls.answer_balloon_stop_img = ImageTk.PhotoImage(Image.open("./assets/png/stop.png").resize((20, 20)))
        cls.answer_balloon_translate_img = ImageTk.PhotoImage(Image.open("./assets/png/translate.png").resize((20, 20)))
        cls.answer_balloon_speaker_img = ImageTk.PhotoImage(Image.open("./assets/png/speak.png").resize((20, 20)))
        cls.answer_balloon_regenerate_img = ImageTk.PhotoImage(Image.open("./assets/png/refresh.png").resize((20, 20)))
        cls.answer_balloon_cancel_img = ImageTk.PhotoImage(Image.open("./assets/png/delete.png").resize((20, 20)))    
    
    def __init__(self, answer, question=None, faster_whisper_listener=None, root_called=None, **kwargs):
        super().__init__(**kwargs)
                
        self.root = root if not root_called else root_called
        self.answer = answer
        self.question = question
        self.answer_var = tk.StringVar(value=answer)
        self.is_edit_mode = False  # 수정 모드 플래그
        
        self.faster_whisper_listener = faster_whisper_listener
        
        self.setting_lang = answer['setting_lang']
        self.answer_en = answer['answer_en']
        self.answer_ko = answer['answer_ko']
        self.answer_jp = answer['answer_jp']
        
        self.text = self.answer_en
        if self.setting_lang == 'jp':
            self.text = self.answer_jp
        elif self.setting_lang == 'ko':
            self.text = self.answer_ko
        self.text_visible = self.text
        
        self.canvas_width = 400
        self.canvas_height = 500
        self.overrideredirect(True)  # 창 장식(border) 제거
        self.attributes("-topmost", 99)  # 항상 최상위에 표시
        self.wm_attributes('-transparentcolor', '#306198')
        self.geometry(f"{self.canvas_width}x500+{self.root.winfo_x()}+{self.root.winfo_y()}")
        
        self.duration = 10*60*1000  # 기본값 10분
        self.duration_interval = 40  # 0.04초
        self.after(0, self.check_update)

        self.prev_x, self.prev_y = 0, 0
        
        # canvas 만들고
        self.canvas = tk.Canvas(self, width=self.canvas_width, highlightthickness=0, borderwidth=0, bd=0, bg='#306198')
        self.canvas.pack()
        self.create_text(self.text)
        self.create_image()

        self.close_btn = tk.Label(self, image=AnswerBalloon.close_img, cursor="hand2", bg='#CFE9FE')
        self.close_btn.place(x=self.canvas_width - 28, y=3)
        self.close_btn.bind("<Button-1>", lambda e: self.kill_balloon())

        # 말풍선 내용을 표시하는 텍스트 추가
        self.text_widget = tk.Text(self.canvas, wrap=tk.WORD, width=30, height=3, background='white', font=("Noto Sans", 12, "bold"))
        self.text_window = self.canvas.create_window((self.canvas_width//2, self.canvas_height//2), window=self.text_widget, anchor='center')
        self.canvas.itemconfig(self.text_window, state='hidden')
        
        # 우측 하단 버튼들
        self.btns = list()

        buttons = [
            ("중지", AnswerBalloon.answer_balloon_stop_img, self.stop_create, True),
            # ("수정", img_modify, self.modify_mode, True),   # Todo
            ("음성재생", AnswerBalloon.answer_balloon_speaker_img, play_wav_queue_history, True),
            ("번역변경", AnswerBalloon.answer_balloon_translate_img, self.change_lang, True),
            # ("질문보기", answer_balloon_question_view_img, self.open_question_view, True),  # Todo
            # ("상세", answer_balloon_detail_img, self.open_detail_view, False),  # Todo
            ("다시 생성", AnswerBalloon.answer_balloon_regenerate_img, self.regenerate_btn, True),
            ("대화취소", AnswerBalloon.answer_balloon_cancel_img, self.cancel_conversation, True),
            # ("답변복사", answer_balloon_copy_img, None, True)  # Todo
        ]
        x_offset = self.canvas_width - (25 * len(buttons)) - 3  # 버튼들을 오른쪽 하단에 정렬하기 위해 x 위치 계산
        y_offset = self.canvas_height - 30  # 버튼들의 y 위치
        i = 0
        for text, img, command, is_able in buttons:
            if is_able:
                btn = tk.Label(self, image=img, cursor="hand2", bg='#CFE9FE')
            else:
                btn = tk.Label(self, image=img, cursor="hand2", bg='#696969')
            btn.place(x=x_offset + (i * 25), y=y_offset)
            self.btns.append(btn)
            i += 1
            if command and is_able:
                btn.bind("<Button-1>", lambda e, cmd=command: cmd())
        self.modify_btn = self.btns[1]  # 하드 코딩
        
        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        
    def stop_create(self):
        state.set_is_stop_requested(True)
        clear_wav_queue()
        
        
    def create_text(self, text):
        self.text_label = self.canvas.create_text(self.canvas_width // 2, 0, text=text, anchor='center', fill="black", width=self.canvas_width - 60, font=("Noto Sans", 12, "bold"))
        x0, y0, x1, y1 = self.canvas.bbox(self.text_label)
        self.canvas_height = int(y1 - y0 + 60)
        self.canvas.config(height=self.canvas_height)
        self.canvas.move(self.text_label, 0, self.canvas_height // 2)
        self.geometry(f"{self.canvas_width}x{self.canvas_height}+{self.root.winfo_x()}+{self.root.winfo_y() - self.canvas_height - 30}")

    def create_image(self):
        img_output_resized = AnswerBalloon.img_output.resize((self.canvas_width, self.canvas_height))
        self.photo = ImageTk.PhotoImage(img_output_resized)
        self.canvas_image = self.canvas.create_image(self.canvas_width // 2, 0, anchor='n', image=self.photo)
        self.canvas.itemconfig(self.canvas_image, image=self.photo)
        self.canvas.tag_raise(self.text_label, self.canvas_image)
        
    def reloc_btns(self):
        # 버튼 재정렬
        x_offset = self.canvas_width - (25 * len(self.btns)) - 3  # 버튼들을 오른쪽 하단에 정렬하기 위해 x 위치 계산
        y_offset = self.canvas_height - 30  # 버튼들의 y 위치
        i = 0
        for btn in self.btns:
            btn.place(x=x_offset + (i * 25), y=y_offset)
            i += 1        

    def regenerate_btn(self):
        try:
            global answer_balloon
            if self.faster_whisper_listener:
                self.process_single_LLM(self.question)
                self.destroy()
            elif self.question:
                self.destroy()
                self.root.after(0, regenerate, self.question)
        except:
            pass

    def modify_text(self, modified_text):
        self.canvas.delete(self.text_label)
        self.canvas.delete(self.canvas_image)
        self.text = modified_text
        self.create_text(modified_text)
        self.create_image()
        self.reloc_btns()
        
    def modify_text_from_answer(self, modified_answer):
        print('why', self.setting_lang)
        # 변수정리
        self.answer['answer_en'] = modified_answer['answer_en']
        self.answer['answer_ko'] = modified_answer['answer_ko']
        self.answer['answer_jp'] = modified_answer['answer_jp']
        self.answer_en = modified_answer['answer_en']
        self.answer_ko = modified_answer['answer_ko']
        self.answer_jp = modified_answer['answer_jp']
        
        self.text = self.answer_en
        if self.setting_lang == 'jp':
            self.text = self.answer_jp
        elif self.setting_lang == 'ko':
            self.text = self.answer_ko
        
        self.canvas.delete(self.text_label)
        self.canvas.delete(self.canvas_image)
        self.create_text(self.text)
        self.create_image()
        self.reloc_btns()
       
    # text 변화를 확인하고 update
    def check_update(self):      
        if self:  
            if self.text_visible != self.text:
                self.text_visible = self.text
                self.modify_text(self.text_visible)

            # 여기서 지속시간도 체크
            self.duration -= self.duration_interval
            if self.duration <= 0:
                self.kill_balloon()
        else:
            print('balloon killed update')

    def update_text(self, updated_answer):
        self.answer = updated_answer
        self.setting_lang = updated_answer['setting_lang']
        self.answer_en = updated_answer['answer_en']
        self.answer_ko = updated_answer['answer_ko']
        self.answer_jp = updated_answer['answer_jp']
        
        self.text = self.answer_en
        if self.setting_lang == 'jp':
            self.text = self.answer_jp
        elif setting_lang == 'ko':
            self.text = self.answer_ko

    def kill_balloon(self):
        try:
            global is_chatting, answer_balloon
            if answer_balloon:
                answer_balloon = None
            is_chatting = False
            set_status('idle')
        except:
            pass
        self.photo = None
        self.destroy()  
        
    def on_press(self, event):
        self.prev_x, self.prev_y = event.x, event.y

    def on_drag(self, event):
        deltax = event.x - self.prev_x
        deltay = event.y - self.prev_y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def on_double_click(self, event):
        self.clipboard_clear()
        selected_text = self.canvas.itemcget(self.text_label, "text")
        self.clipboard_append(selected_text)
    
    def cancel_conversation(self):
        memory.delete_recent_dialogue()  # 대화 두개 지우고 answer 지우기
        memory.delete_recent_dialogue()
        self.kill_balloon()
    
    def open_question_view(self):
        pass
    
    def open_detail_view(self):
        pass

    def change_lang(self):
        if self.setting_lang == 'en':
            self.answer['setting_lang'] = 'jp'
            self.setting_lang = 'jp'
            self.modify_text(self.answer['answer_jp'])
        elif self.setting_lang == 'jp':
            self.answer['setting_lang'] = 'ko'
            self.setting_lang = 'ko'
            self.modify_text(self.answer['answer_ko'])
        else:
            self.answer['setting_lang'] = 'en'
            self.setting_lang = 'en'
            self.modify_text(self.answer['answer_en'])

    def modify_mode(self):
        if not self.is_edit_mode:
            self.is_edit_mode = True
            self.text_widget.delete("1.0", tk.END)  # 텍스트 위젯을 초기화
            self.text_widget.insert(tk.END, self.answer_var.get())  # 텍스트 위젯에 텍스트 변수 값 설정
            self.canvas.itemconfig(self.text_label, state='hidden')
            self.canvas.itemconfig(self.text_window, state='normal')
            self.modify_btn.config(image=answer_balloon_detail_img)
        else:
            self.is_edit_mode = False
            new_text = self.text_widget.get("1.0", tk.END).strip()
            if new_text:  # 텍스트 위젯의 내용이 비어있지 않으면
                self.text_var.set(new_text)
                self.text = new_text
            else:  # 텍스트 위젯의 내용이 비어있으면 원래 텍스트 유지
                self.text_var.set(self.text)
            self.modify_text(self.answer_var.get())
            self.canvas.itemconfig(self.text_window, state='hidden')
            self.canvas.itemconfig(self.text_label, state='normal')
            self.modify_btn.config(image=img_modify)

# 안내등의 가벼운 말풍선
class AnswerBalloonSimple(tk.Toplevel):    
    def __init__(self, text, root_called=None, **kwargs):
        global is_use_cuda
        super().__init__(**kwargs)
        
        # 번역
        self.text = get_message(text)            
        self.root = root if not root_called else root_called

        self.canvas_width = 400
        self.canvas_height = 500
        self.overrideredirect(True)  # 창 장식(border) 제거
        self.attributes("-topmost", 99)  # 항상 최상위에 표시
        self.wm_attributes('-transparentcolor', '#306198')
        self.geometry(f"{self.canvas_width}x500+{self.root.winfo_x()}+{self.root.winfo_y()}")
        
        # canvas 만들고
        self.canvas = tk.Canvas(self, width=self.canvas_width, highlightthickness=0, borderwidth=0, bd=0, bg='#306198')
        self.canvas.pack()
        self.create_text(self.text)
        self.create_image()
        
        # 말풍선 내용을 표시하는 텍스트 추가
        self.text_widget = tk.Text(self.canvas, wrap=tk.WORD, width=30, height=3, background='white', font=("Noto Sans", 12, "bold"))
        self.text_window = self.canvas.create_window((self.canvas_width//2, self.canvas_height//2), window=self.text_widget, anchor='center')
        self.canvas.itemconfig(self.text_window, state='hidden')
    
        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)

        result_ko = translator_google.translate(text, dest='ko').text        
        result_ko = change_to_ko(result_ko)
        result_jp = translator_google.translate(text, dest='ja').text
        result_jp = change_to_jp(result_jp)
        audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_ko, use_cuda=is_use_cuda, type='single', sid=0)
        sound_length = play_wav(audio, loaded_settings['setting_volume'])
        self.after(int(sound_length*1000)+800, self.kill_balloon)
        
    def create_text(self, text):
        self.text_label = self.canvas.create_text(self.canvas_width // 2, 0, text=text, anchor='center', fill="black", width=self.canvas_width - 60, font=("Noto Sans", 12, "bold"))
        x0, y0, x1, y1 = self.canvas.bbox(self.text_label)
        self.canvas_height = int(y1 - y0 + 60)
        self.canvas.config(height=self.canvas_height)
        self.canvas.move(self.text_label, 0, self.canvas_height // 2)
        self.geometry(f"{self.canvas_width}x{self.canvas_height}+{self.root.winfo_x()}+{self.root.winfo_y() - self.canvas_height - 30}")

    def create_image(self):
        img_output_resized = img_output.resize((self.canvas_width, self.canvas_height))
        self.photo = ImageTk.PhotoImage(img_output_resized)
        self.canvas_image = self.canvas.create_image(self.canvas_width // 2, 0, anchor='n', image=self.photo)
        self.canvas.itemconfig(self.canvas_image, image=self.photo)
        self.canvas.tag_raise(self.text_label, self.canvas_image)
        
    def on_press(self, event):
        self.prev_x, self.prev_y = event.x, event.y

    def on_drag(self, event):
        deltax = event.x - self.prev_x
        deltay = event.y - self.prev_y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def on_double_click(self, event):
        self.clipboard_clear()
        selected_text = self.canvas.itemcget(self.text_label, "text")
        self.clipboard_append(selected_text)
        
    def kill_balloon(self):
        self.photo = None
        self.destroy()  

# 질문 말풍선 (answer: dict)
class AskBalloon(tk.Toplevel):
    def __init__(self, text, trans_question, **kwargs):
        super().__init__(**kwargs)
        
        self.text = text
        self.trans_question = trans_question
        
        self.canvas_width = 400
        self.canvas_height = 500
        self.overrideredirect(True)  # 창 장식(border) 제거
        self.attributes("-topmost", 99)  # 항상 최상위에 표시
        self.wm_attributes('-transparentcolor', '#306198')
        self.geometry(f"{self.canvas_width}x500+{root.winfo_x()}+{root.winfo_y()}")
        
        # self.duration = 10*60*1000  # 기본값 10분
        # self.duration_interval = 40  # 0.04초
        # self.after(0, self.check_update)

        self.prev_x, self.prev_y = 0, 0
        
        # canvas 만들고
        self.canvas = tk.Canvas(self, width=self.canvas_width, highlightthickness=0, borderwidth=0, bd=0, bg='#306198')
        self.canvas.pack()
        self.create_text(self.text)
        self.create_image()

        self.close_btn = tk.Label(self, image=close_img, cursor="hand2", bg='#BEF08C')
        self.close_btn.place(x=self.canvas_width - 28, y=3)
        self.close_btn.bind("<Button-1>", lambda e: self.kill_balloon())

        # 우측 하단 버튼들
        self.btns = list()
        buttons = [
            # ("수정", img_modify, None, False),  # $$$ 후순위
            ("승인", check_img, self.send, True)
        ]
        x_offset = self.canvas_width - (25 * len(buttons)) - 3  # 버튼들을 오른쪽 하단에 정렬하기 위해 x 위치 계산
        y_offset = self.canvas_height - 30  # 버튼들의 y 위치
        i = 0
        for text, img, command, is_able in buttons:
            if is_able:
                btn = tk.Label(self, image=img, cursor="hand2", bg='#BEF08C')
            else:
                btn = tk.Label(self, image=img, cursor="hand2", bg='#696969')
            btn.place(x=x_offset + (i * 25), y=y_offset)
            self.btns.append(btn)
            i += 1
            if command and is_able:
                btn.bind("<Button-1>", lambda e, cmd=command: cmd())  # $$$ 일단은 함수 하나 뿐이니까...
        
        self.canvas.bind("<Button-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        
    def create_text(self, text):
        self.text_label = self.canvas.create_text(self.canvas_width // 2, 0, text=text, anchor='center', fill="black", width=self.canvas_width - 60, font=("Noto Sans", 12, "bold"))
        x0, y0, x1, y1 = self.canvas.bbox(self.text_label)
        self.canvas_height = int(y1 - y0 + 60)
        self.canvas.config(height=self.canvas_height)
        self.canvas.move(self.text_label, 0, self.canvas_height // 2)
        self.geometry(f"{self.canvas_width}x{self.canvas_height}+{root.winfo_x()}+{root.winfo_y() - self.canvas_height - 30}")

    def create_image(self):
        global img_ask_balloon
        img_ask_balloon_resized = img_ask_balloon.resize((self.canvas_width, self.canvas_height))
        self.photo = ImageTk.PhotoImage(img_ask_balloon_resized)
        self.canvas_image = self.canvas.create_image(self.canvas_width // 2, 0, anchor='n', image=self.photo)
        self.canvas.itemconfig(self.canvas_image, image=self.photo)
        self.canvas.tag_raise(self.text_label, self.canvas_image)
        
    def reloc_btns(self):
        # 버튼 재정렬
        x_offset = self.canvas_width - (25 * len(self.btns)) - 3  # 버튼들을 오른쪽 하단에 정렬하기 위해 x 위치 계산
        y_offset = self.canvas_height - 30  # 버튼들의 y 위치
        i = 0
        for btn in self.btns:
            btn.place(x=x_offset + (i * 25), y=y_offset)
            i += 1        

    def modify_text(self, modified_text):
        self.canvas.delete(self.text_label)
        self.canvas.delete(self.canvas_image)
        self.text = modified_text
        self.create_text(modified_text)
        self.create_image()
        self.reloc_btns()

    def kill_balloon(self):
        global ask_balloon, is_chatting
        is_chatting= False
        ask_balloon = None
        self.photo = None
        self.destroy()  
        
    def on_press(self, event):
        self.prev_x, self.prev_y = event.x, event.y

    def on_drag(self, event):
        deltax = event.x - self.prev_x
        deltay = event.y - self.prev_y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def on_double_click(self, event):
        self.clipboard_clear()
        selected_text = self.canvas.itemcget(self.text_label, "text")
        self.clipboard_append(selected_text)
    
    def send(self):
        # root.after(0, show_status_balloon)    
        # show_status_balloon()
        self.kill_balloon()
            
        global is_chatting
        is_chatting=True
        conversation_web(self.trans_question)
        
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

# 이펙터
class Effecter(tk.Toplevel):
    def __init__(self, images=None, duration=0.2, center=None, **kwargs):
        super().__init__(**kwargs)
        
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
            x = int(root.winfo_x())# + root.winfo_width()/2)
            y = int(root.winfo_y())# + root.winfo_height()/2)
            self.geometry(f"+{x}+{y}")

    def show_next_image(self):
        if self.current_index < len(self.images):
            image = self.images[self.current_index]
            self.label.configure(image=image)
            self.current_index += 1
            self.after(int(self.duration * 1000), self.show_next_image)
        else:
            self.destroy()

# 로딩, 상태표시용 말풍선
class StatusBalloon(tk.Toplevel):
    def __init__(self, image_folder=None, master=None, duration=120, **kwargs):
        super().__init__(master, **kwargs)
        
        self.attributes('-topmost', 99)
        self.wm_attributes('-transparentcolor', '#f0f0f0')
        self.overrideredirect(True)
        self.title('balloon')
        
        # self.size_width = master.winfo_width() * 0.5 if master else 100
        # print('master.winfo_width()', master.winfo_width())
        self.rate = 1
        if master:
            self.rate = master.winfo_width() / 250
        else:
            master = root
        self.size_width = max(int(100*self.rate), 20)
        self.size_height = int(self.size_width * 0.81)       
        balance_x = max(int(40*self.rate), 8)
        balance_y = max(int(40*self.rate), 8)
        self.inner_img_size_x = max(int(30*self.rate), 6)
        self.inner_img_size_y = max(int(30*self.rate), 6)
        self.geometry(f"{int(self.size_width)}x{int(self.size_height)}+{int(root.winfo_x()+root.winfo_width()-balance_x)}+{root.winfo_y()-balance_y}")
        
        self.duration = duration  # 기본 최대 10분
        self.master = master
        
        self.canvas = tk.Canvas(self, width=self.size_width, height=self.size_height, bg='#f0f0f0')
        self.canvas.pack()
        
        self.bg_image_file = Image.open("./assets/png/balloon.png")
        self.bg_image_resized = ImageTk.PhotoImage(self.bg_image_file.resize((self.size_width, self.size_height)))
        self.canvas.create_image(0, 0, anchor="nw", image=self.bg_image_resized)  # 바탕그림
        
        # 말풍선 속 이미지 있을 경우
        if image_folder:
            self.set_image_folder(image_folder)

        else:
            self.duration = 5  # 이미지가 없을 경우 5초 후 아웃 $$$

        # master 있을 경우 따라다니기 (위에서 master없을 경우 root로 치환, 유지할 경우 self. 제외)
        if self.master:
            self.after(0, self.update_position)
            
    def update_position(self):
        global status_balloon
        if status_balloon:
            self.geometry(f"{int(self.size_width)}x{int(self.size_height)}+{int(root.winfo_x()+root.winfo_width()-40)}+{root.winfo_y()-40}")
            self.after(20, self.update_position)
            
    def set_image_folder(self, image_folder):
        self.content_image = self.canvas.create_image(max(int(35*self.rate), 7), max(int(20*self.rate), 4), anchor="nw", image=self.bg_image_resized)
        image_paths = [os.path.join(image_folder, file) for file in os.listdir(image_folder) if file.endswith(".png")]
        self.images = [Image.open(image_path).resize((self.inner_img_size_x, self.inner_img_size_y)) for image_path in image_paths]
        self.images_resized = [ImageTk.PhotoImage(image.resize((self.inner_img_size_x, self.inner_img_size_y))) for image in self.images]
        self.image_current_index = 0
        self.image_duration = 0.04
        self.after(0, self.show_next_image)
            
    def show_next_image(self):      
        global status_balloon
        if status_balloon:  
            self.canvas.itemconfig(self.content_image, image=self.images_resized[self.image_current_index])
            self.image_current_index = (self.image_current_index + 1) % len(self.images_resized)
            self.after(int(self.image_duration * 1000), self.show_next_image)
            
            # 여기서 지속시간도 체크
            self.duration -= self.image_duration
            if self.duration <= 0:
                self.kill_balloon()

    def kill_balloon(self):
        global status_balloon
        for image in self.images:  # Data 
            image.close()
        self.bg_image_file.close()
        status_balloon = None
        self.destroy()

# 클래스 리퀘스트

######################################################################
       
# tkinter animation 관련
def get_animation_assets_info(anim_name):
    global char_info
 
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
        animation_assets_info['animation_width'] = root_idle_width  # 최초 길이 : idle 버전
    if 'animation_height' not in animation_assets_info:
        animation_assets_info['animation_height'] = root_idle_height  # 최초 길이 : idle 버전
    if 'animation_size' not in animation_assets_info or not (0<animation_assets_info['animation_size']<=2):
        animation_assets_info['animation_size'] = 0.5
    if 'animation_ground' not in animation_assets_info:  # 범위 0~0.8
        animation_assets_info['animation_ground'] = 0
        
    char_info['animation_assets_info'][char_info['animation_assets']][anim_name] = animation_assets_info  

def get_idle_info():
    global root_idle_width, root_idle_height
    dir = './animation/' + 'arona_imagine31_2' + '/idle'  # ./animation/(arona_png)/(idle_2)      
    files = os.listdir(dir)
    png_files = [file for file in files if file.endswith('.png')]
    first_png_file = os.path.join(dir, png_files[0])
    image = Image.open(first_png_file)
    root_idle_width, root_idle_height = image.size
    image.close()

# rate 배율로 수정 (기준 좌하)
def set_size(rate):
    # 좌측 하단 모서리 위치
    x = root.winfo_x()
    y = root.winfo_y() + root.winfo_height()

    # 새로운 창 크기
    global root_frame_width, root_frame_height
    root_width = int(root_frame_width*rate)
    root_height = int(root_frame_height*rate)
    y -= root_height
    
    root.geometry(f"{root_width}x{root_height}+{int(x)}+{int(y)}")  
    print('set_size', f"{root_width}x{root_height}+{int(x)}+{int(y)}")
    

def init_anim():
    global char_info
    setting_size = loaded_settings['setting_size']
    animation_assets_name = char_info['animation_assets']

    get_idle_info()
    global anim, anim_set
    anim = dict()
    anim_set= set()
    root_folder = './animation/' + animation_assets_name
    for image_root, dirs, _ in os.walk(root_folder):  
        # 모든 animation info 세팅
        for folder_name in dirs:  # idle_1
            get_animation_assets_info(folder_name) 
            anim_name = folder_name.split('_')[0]  # idle

            animation_assets_info = char_info['animation_assets_info'][animation_assets_name][folder_name]
            if not animation_assets_info['is_animation_use']:
                continue           
            root_width = int(animation_assets_info['animation_width']*animation_assets_info['animation_size']*setting_size)
            root_height = int(animation_assets_info['animation_height']*animation_assets_info['animation_size']*setting_size)

            folder_root = os.path.join(image_root, folder_name)
            for _, _, files in os.walk(folder_root):  
                # 이미지 주소 체크
                images = []
                for image in files:
                    if image.lower().endswith('.png'):
                        images.append(image)

                # anim[anim_name][idx]로 img_info에 관한 정보 생성
                if images:
                    # 특수로직 'walk' 계열 ($$$)
                    if anim_name == 'walk':
                        if 'walk_left' not in anim:
                            anim['walk_left'] = list()
                            anim['walk_right'] = list()
                            anim_set.add('walk_left')
                            anim_set.add('walk_right')

                        # 이미지 정보 매핑 (왼)
                        images_info = list()                
                        images.sort()
                        for image in images:
                            image_info = dict()
                            image_info['name'] = folder_name + '_left'
                            img_loc = os.path.join(folder_root, image)
                            image_info['frame_length'] = 1000  # 1초
                            if len(image.split('_')) >= 2:
                                try:
                                    image_info['frame_length'] = int(image.split('_')[-1].strip('.png'))  # 프레임 지속시간
                                except:
                                    image_info['frame_length'] = 1000
                            image_file = Image.open(img_loc)
                            image_info['image'] = image_file
                            image_info['image_resized'] = ImageTk.PhotoImage(image_file.resize((root_width, root_height)))
                            image_info['animation_ground'] = animation_assets_info['animation_ground']
                            image_info['animation_len'] = animation_assets_info['animation_len']
                            # image_file.close() # $$$

                            images_info.append(image_info)
                        anim['walk_left'].append(images_info)

                        # 이미지 정보 매핑 (오)
                        images_info2 = list()                
                        for image in images:
                            image_info2 = dict()
                            image_info2['name'] = folder_name + '_right'
                            img_loc = os.path.join(folder_root, image)
                            image_info2['frame_length'] = 1000  # 1초
                            if len(image.split('_')) >= 2:
                                try:
                                    image_info2['frame_length'] = int(image.split('_')[-1].strip('.png'))  # 프레임 지속시간
                                except:
                                    image_info2['frame_length'] = 1000
                            image_file2 = Image.open(img_loc)
                            image_info2['image'] = image_file2.transpose(Image.FLIP_LEFT_RIGHT)
                            image_info2['image_resized'] = ImageTk.PhotoImage(image_file2.transpose(Image.FLIP_LEFT_RIGHT).resize((root_width, root_height)))
                            image_info2['animation_ground'] = animation_assets_info['animation_ground']
                            image_info2['animation_len'] = animation_assets_info['animation_len']
                            # image_file2.close() # $$$

                            images_info2.append(image_info2)
                        anim['walk_right'].append(images_info2)

                    else:
                        # 없을경우 리스트 추가
                        if anim_name not in anim:
                            anim[anim_name] = list()
                            anim_set.add(anim_name)
                        # - 있을 경우 중간에 심심하게 나오는 무언가(idle-anim)

                        # 이미지 정보 매핑
                        images_info = list()                
                        images.sort()
                        for image in images:
                            image_info = dict()
                            image_info['name'] = folder_name
                            img_loc = os.path.join(folder_root, image)
                            image_info['frame_length'] = 1000  # 1초
                            if len(image.split('_')) >= 2:
                                try:
                                    image_info['frame_length'] = int(image.split('_')[-1].strip('.png'))  # 프레임 지속시간
                                except:
                                    image_info['frame_length'] = 1000
                            image_file = Image.open(img_loc)
                            image_info['image'] = image_file
                            image_info['image_resized'] = ImageTk.PhotoImage(image_file.resize((root_width, root_height)))
                            image_info['animation_ground'] = animation_assets_info['animation_ground']
                            image_info['animation_len'] = animation_assets_info['animation_len']
                            # image_file.close() # $$$

                            images_info.append(image_info)

                        # 해당내용 추가
                        anim[anim_name].append(images_info)
                else:
                    # png가 없는 빈 폴더
                    continue

    return anim, anim_set

def update_anim():
    global loaded_settings, char_info
    animation_assets_name = char_info['animation_assets']

    # image_resized 갱신
    for anim_info in anim.values():
        for image_infos in anim_info:
            for image_info in image_infos:
                image_info_name = image_info['name']
                image_info_name = image_info_name.replace('_left', '')  # walk_left 등
                image_info_name = image_info_name.replace('_right', '')  # walk_right 등
                get_animation_assets_info(image_info_name)
                animation_assets_info = char_info['animation_assets_info'][animation_assets_name][image_info_name]
                root_width = int(animation_assets_info['animation_width']*animation_assets_info['animation_size']*loaded_settings['setting_size'])
                root_height = int(animation_assets_info['animation_height']*animation_assets_info['animation_size']*loaded_settings['setting_size'])
                image_info['image_resized'] = ImageTk.PhotoImage(image_info['image'].resize((root_width, root_height)))
    
    # update 후 root 이미지 다시 불러오기
    if status != 'idle':
        set_status('idle')
    else:
        set_status('smile')

def set_status(change_status):
    global status, anim_idx, duration_anim, duration_frame, frame_idx, anim_ground
    global char_info
    
    # Lock (change animation으로 상태가 변하지 않음 + 애니메이션 내의 변동은 있음)
    global anim_lock
    anim_lock = False
    if change_status.endswith('_lock'):
        change_status = change_status.rstrip('_lock')
        anim_lock = True    
    elif change_status == status:  # 이미 그 상태 + lock 아님 = 상태 유지
        return

    # cascade 하게 체크 
    anim_status = change_status
    if anim_status in ('fall') and anim_status not in anim_set:
        if 'pick' in anim_set:
            anim_status = 'pick'
        else:
            anim_status = 'idle'
    if anim_status in ('smile') and anim_status not in anim_set:
        if 'pick' in anim_set:
            anim_status = 'think'
        else:
            anim_status = 'idle'
    # 최종형태
    if anim_status not in anim_set:
        if anim_status in ('think', 'pick', 'fall', 'sit'):  # 애니메이션 없으면 idle로 교체
            anim_status = 'idle'
        else:
            print('no such status : ' + change_status)
            return
    status = anim_status
    
    anim_idx = random.randint(0, len(anim[anim_status])-1)
    frame_idx = 0

    duration_anim = anim[anim_status][anim_idx][frame_idx]['animation_len']  # 애니메이션 지속시간
    duration_frame = anim[anim_status][anim_idx][frame_idx]['frame_length']  #  frame 지속시간
    new_anim_ground = anim[anim_status][anim_idx][frame_idx]['animation_ground']  #  땅에서부터 G 판정까지의 높이
    
    # root 정보 변경
    animation_assets_name = char_info['animation_assets']
    image_info_name = anim[anim_status][anim_idx][frame_idx]['name']
    image_info_name = image_info_name.replace('_left', '')  # walk_left 등
    image_info_name = image_info_name.replace('_right', '')  # walk_right 등
    animation_assets_info = char_info['animation_assets_info'][animation_assets_name][image_info_name]
    root_width = int(animation_assets_info['animation_width']*animation_assets_info['animation_size']*loaded_settings['setting_size'])
    root_height = int(animation_assets_info['animation_height']*animation_assets_info['animation_size']*loaded_settings['setting_size'])
    
    # root size 변경
    x = root.winfo_x() + root.winfo_width()/2 - root_width/2
    y = root.winfo_y() + (1-anim_ground) * root.winfo_height() - (1-new_anim_ground)*root_height # 기존  
    global window_bottom
    if anim_ground != new_anim_ground and window_bottom:  # 높이 변동이 있는 애니메이션 경우, 만약에 박힌 상태면 탈출
        y = min(y, window_bottom - (1-new_anim_ground)*root_height)
    # print('###', change_status, anim_status)
    # print('ha', x, y, anim_ground, new_anim_ground)
    anim_ground = new_anim_ground   
    root.geometry(f"{root_width}x{root_height}+{int(x)}+{int(y)}")  
    
    # 전역변수 저장 (setting size 미적용)
    global root_frame_width, root_frame_height
    root_frame_width = int(animation_assets_info['animation_width']*animation_assets_info['animation_size'])
    root_frame_height = int(animation_assets_info['animation_height']*animation_assets_info['animation_size'])

    # 애니메이션 재생
    frame = anim[anim_status][anim_idx][frame_idx]['image_resized']
    label.configure(image=frame)
    
    # root 다시 topmost
    root.wm_attributes('-topmost', 90)

# 현재 root가 속해있는 모니터 반환
def get_monitor_current():
    global monitor_main
    monitors = get_monitors()  # trouble shooting : 자주부르면 app 터짐 > 드래그종료, 처음소환때만 세팅
    for monitor in monitors:
        if (monitor.x <= root.winfo_x() < monitor.x + monitor.width) and (monitor.y <= root.winfo_y() < monitor.y + monitor.height):
            return monitor
    if monitor_main == None:
        for monitor in monitors:
            if monitor.is_primary:
                monitor_main = monitor
                break
    return monitor_main  # 어떤 모니터에도 속해있지 않음, 모니터 사이에 걸쳐있음 (메인모니터로 처리)

# 모니터 정보 setting 후 global로 사용
def set_monitor_info(monitor):
    global monitor_current, monitor_adj_x, monitor_adj_y, monitor_screen_width, monitor_screen_height
    monitor_current = monitor
    # x, y 모니터 대비 상대적 위치 계산용
    monitor_adj_x = monitor_current.x
    monitor_adj_y = monitor_current.y
    # 화면 가로 세로 크기 재설정
    monitor_screen_width = monitor_current.width
    monitor_screen_height = monitor_current.height

def get_random_monitor():
    monitors = get_monitors()
    return monitors[random.randint(0, len(monitors)-1)]

def on_drag_start(event):
    global is_dragging, is_drag_cool
    is_dragging = True
    is_drag_cool = False
    # 마우스 버튼을 누를 때 윈도우의 현재 위치를 기록합니다.
    root.x = event.x
    root.y = event.y

def on_drag_motion(event):
    global is_drag_cool
    def drag_cool():
        global is_drag_cool
        root.after(20, drag_coolend)
        is_drag_cool = True
    
    def drag_coolend():
        global is_drag_cool
        is_drag_cool = False

    if not is_drag_cool:
        # 마우스를 이동할 때 윈도우의 새 위치를 계산하여 이동합니다.
        deltax = event.x - root.x
        deltay = event.y - root.y
        x = root.winfo_x() + deltax
        y = root.winfo_y() + deltay
        root.geometry(f"+{x}+{y}")
        drag_cool()

def on_drag_release(event):
    global is_dragging
    is_dragging = False
    set_monitor_info(get_monitor_current())
    if loaded_settings['setting_is_gravity']:
        set_status('fall')
    else:
        set_status('idle')

def update(delta):
    # current, peak = tracemalloc.get_traced_memory()
    # print(f"Current memory usage: {current / 10**6} MB, Peak usage: {peak / 10**6} MB")
    def update_frame_event(delta):
        global status, duration_anim, is_dragging, is_chatting, is_falling, is_waiting, anim_idx
        if is_dragging or is_chatting or is_falling or is_waiting:
            return

        # duration_anim 감소
        duration_anim -= delta
        # 상태 변화     
        global anim_lock
        if duration_anim < 0:
            prob = random.randint(0, 99)
            if status == 'idle':
                if prob < 15*int(loaded_settings['setting_mobility']): # 0~30
                    set_status('walk_left')
                elif prob < 30*int(loaded_settings['setting_mobility']):
                    set_status('walk_right')
                else:
                    prob = random.randint(0, 99)
                    if prob <= 40:  # 눈깜빡
                        set_status('sit')
                    elif prob <= 80:  # 상태유지
                        duration_anim = 1000  
                    else:  # 동일 자세 내 변경
                        anim_idx = random.randint(0, len(anim[status])-1)
                        duration_anim = 1000  
            elif status == 'walk_left':
                if anim_lock:
                    duration_anim = 1000  # 상태유지
                elif prob <= 100 - 35*int(loaded_settings['setting_mobility']): # 30~100% 확률로 이동정지
                    set_status('idle')
                else:
                    duration_anim = 1000  # 상태유지
            elif status == 'walk_right':
                if anim_lock:
                    duration_anim = 1000  # 상태유지
                elif prob <= 100 - 35*int(loaded_settings['setting_mobility']): # 30~100% 확률로 이동정지
                    set_status('idle')
                else:
                    duration_anim = 1000  # 상태유지
            elif status == 'sit':
                if anim_lock:
                    set_status('sit_lock')  # 같은 sit 내에서 자세만 변경
                elif prob <= 50:
                    set_status('idle')
                else:
                    duration_anim = 1000  # 상태유지
            else:
                print('update frame error : ', status)
                set_status('idle')
    
    # 초기화
    global status, frame_idx, duration_anim, duration_frame, is_dragging, is_chatting, is_falling, is_waiting
    root.after(delta, update, delta)  # 다음 update

    # 상태/변화 갱신
    update_frame_event(delta)

    # 프레임 재생
    duration_frame -= delta
    if duration_frame < 0:
        if len(anim[status][anim_idx]) == 1:  # 단일 프레임일 경우 생략
            return
        # Frame 재생 후 숫자 증가
        frame = anim[status][anim_idx][frame_idx]['image_resized']
        frame_idx = (frame_idx + 1) % len(anim[status][anim_idx])
        duration_frame = anim[status][anim_idx][frame_idx]['frame_length'] 

        # 애니메이션 재생
        label.configure(image=frame)

# 0.1초마다 이동 제어
def update_physics_move():
    global is_dragging, is_falling, FALL_SPEED, FALL_GSPEED, status

    if not loaded_settings['setting_is_gravity'] and loaded_settings['setting_mobility'] == 0:  # 중력도 이동빈도도 없으면 return
        root.after(1000, update_physics_move)  # 1초마다 작동
        return
    
    # 창의 현재 위치와 창의 크기
    x, y = root.winfo_x(), root.winfo_y()
    wx, wy = root.winfo_width(), root.winfo_height()
    
    # 소속 모니터 정보 가져오기
    global monitor_current, monitor_adj_x, monitor_adj_y, monitor_screen_width, monitor_screen_height
    if monitor_current:
        # x, y 상대적 위치 재계산
        monitor_adj_x = monitor_current.x
        monitor_adj_y = monitor_current.y
        # 화면 가로 세로 크기 재설정
        monitor_screen_width = monitor_current.width
        monitor_screen_height = monitor_current.height

    # 충돌 지점으로 잡을 여덟 곳 (좌상단 기점 시계 방향)
    global anim_ground  # 지상에서부터의 높이
    points = list()
    points.append((x, y))
    points.append((x+wx/2, y))
    points.append((x+wx, y))
    points.append((x+wx, y+wy*(1-anim_ground)/2))
    points.append((x+wx, y+wy*(1-anim_ground)))
    points.append((x+wx/2, y+wy*(1-anim_ground)))
    points.append((x, y+wy*(1-anim_ground)))
    points.append((x, y+wy*(1-anim_ground)/2))

    windows = None
    if False: # loaded_settings['setting_is_gravity']: # 충돌중력여부
        # 충돌판정있는 windows들
        windows = get_collision_windows()

        # 충돌에 따른 이동 방향 (UDLR)
        direction, direction_target = get_dir_from_collisions(points, windows)
        # print('here', x, y, direction, direction_target, status)
        
        # 선이 아래로 뚫고 갔는지 체크
        # direction, direction_target = get_dir_from_line(points, windows)
            # 위로 올라가는 지 (4, 5, 6 하나라도 충돌, 다시 튕기고 떨어지고 반복하지 않게 보수적으로)
        global window_bottom
        if windows:      
            _, root_bottom = points[4]  # root 최하단
            window_bottom = monitor_screen_height  # 윈도우 있다고 믿어도 되는거지
            for window in windows:
                rect = win32gui.GetWindowRect(window)
                if rect[1] >= 15:  # 작업표시줄 왼쪽 위쪽 대처 (애초에 캐릭터 크기도 생각을 해야함...)
                    window_bottom = min(window_bottom, rect[1])  # 작업표시줄 윗부분
            if window_bottom + 15 <= root_bottom:  # 캐릭터 origin y가 작업표시줄 윗부분(-5)보다 높으면 살리기
                direction, direction_target = 'U', rect[1]
    else:
        direction, direction_target = 'G', None

    # 이동 로직
    global fall_delta, status_delta
    is_falling = False
    if not is_dragging:
        if y-monitor_adj_y<=monitor_screen_height-wy*(1-anim_ground): #and 0<=x-monitor_adj_x<=monitor_screen_width-wx:
            status_delta = 0  # 안정적
            if direction == 'G':  # 지상
                fall_delta = 300  # 지상에 있었을 경우 0.300초 이상은 갑자기 fall로 전환되지 않음
                FALL_GSPEED = 0
                if status == 'walk_left':
                    x -= (1 + loaded_settings['setting_moving_speed'])   # 왼쪽으로 1/2
                    if 0<=x-monitor_adj_x<=monitor_screen_width-wx:
                        root.geometry(f"+{x}+{y}") 
                    else:
                        # pass
                        x += 5
                        root.geometry(f"+{x}+{y}") 
                        set_status('idle')
                elif status == 'walk_right':
                    x += (1 + loaded_settings['setting_moving_speed'])   # 오른쪽로 1/2
                    if 0<=x-monitor_adj_x<=monitor_screen_width-wx:
                        root.geometry(f"+{x}+{y}") 
                    else:
                        # pass
                        x -= 5
                        root.geometry(f"+{x}+{y}") 
                        set_status('idle')
                elif status == 'fall':
                    set_status('idle')
            elif direction == 'U':
                distance = min(5, y+wy-direction_target-1)
                root.geometry(f"+{x}+{y-distance}")  # 위로 최대 5
                FALL_GSPEED = 0
            elif direction == 'D':
                root.geometry(f"+{x}+{y+5}")  # 아래로 5
                FALL_GSPEED = 0
            elif direction == 'L':
                x-=5 # 왼쪽으로 5
                if 0<=x-monitor_adj_x<=monitor_screen_width-wx:
                    root.geometry(f"+{x}+{y}")  
                FALL_GSPEED = 0
            elif direction == 'R':
                x += 5 # 오른쪽로 5
                if 0<=x-monitor_adj_x<=monitor_screen_width-wx:
                    root.geometry(f"+{x}+{y}")  
                FALL_GSPEED = 0
            else:   
                fall_delta -= 10      
                if fall_delta <= 0:
                    set_status('fall')
                root.geometry(f"+{x}+{y + FALL_SPEED}")  # 자유 낙하
                is_falling = True
                FALL_GSPEED = max(FALL_GSPEED + 1, 10)  # 가속 최대 10(기존 2배)
        else:
            if not windows:  # 충돌대상이 없으면 지상 (하드코딩적 성격)
                fall_delta = 300  # 지상에 있었을 경우 0.300초 이상은 갑자기 fall로 전환되지 않음
                FALL_GSPEED = 0
                if status == 'walk_left':
                    x -= (1 + loaded_settings['setting_moving_speed'])   # 왼쪽으로 1/2
                    if 0<=x-monitor_adj_x<=monitor_screen_width-wx:
                        root.geometry(f"+{x}+{y}") 
                    else:
                        pass
                        # set_status('idle')
                elif status == 'walk_right':
                    x += (1 + loaded_settings['setting_moving_speed'])   # 오른쪽로 1/2
                    if 0<=x-monitor_adj_x<=monitor_screen_width-wx:
                        root.geometry(f"+{x}+{y}") 
                    else:
                        pass
                        # set_status('idle')
                elif status == 'fall':
                    set_status('idle')
            else:
                if direction == 'G':  # 지상
                    fall_delta = 300  # 지상에 있었을 경우 0.300초 이상은 갑자기 fall로 전환되지 않음
                    FALL_GSPEED = 0
                    if status == 'walk_left':
                        x -= (1 + loaded_settings['setting_moving_speed'])   # 왼쪽으로 1/2
                        if 0<x-monitor_adj_x<monitor_screen_width-wx:
                            root.geometry(f"+{x}+{y}") 
                        else:
                            # pass
                            x += 5
                            root.geometry(f"+{x}+{y}") 
                            set_status('idle')
                    elif status == 'walk_right':
                        x += (1 + loaded_settings['setting_moving_speed'])   # 오른쪽로 1/2
                        print('a', x, x-monitor_adj_x, monitor_screen_width-wx)
                        if 0<x-monitor_adj_x<monitor_screen_width-wx:
                            root.geometry(f"+{x}+{y}") 
                        else:
                            # pass
                            x -= 5
                            root.geometry(f"+{x}+{y}") 
                            set_status('idle')
                    elif status == 'fall':
                        set_status('idle')
                elif direction == 'U':         
                    distance = min(5, y+wy-direction_target-1)
                    root.geometry(f"+{x}+{y-distance}")  # 위로 최대 5
                    FALL_GSPEED = 0
                else:
                    status_delta += 10
                    if status_delta >= 100:
                        status_delta = 0
                        FALL_GSPEED = 0
                        set_status('idle')
    else: 
        FALL_GSPEED = 0      
        set_status('pick') 
    
    # 공유자원 침범의 냄새가 나는데...
    root.after(10, update_physics_move)  # 10밀리초마다 작동 (100프레임)

# 답변용 말풍선
def show_answer_balloon(sound_length, answer, question=None):
    global is_chatting, answer_balloon  
    if answer_balloon:
        answer_balloon.kill_balloon()
    answer_balloon = AnswerBalloon(answer, question)

    # 상태 변경
    set_status('talk')

# send_chat 포함 일말의 과정 정리 (동일한 코드 있고, 이걸로 수정할 예정)
def send_chat_wrapper(text):
    sound_length, answer = send_chat(text)
    if answer:
        sound_length = 999  # $$$ 임시
        root.after(0, show_answer_balloon, sound_length, answer)

def send_chat(text):
    global is_chatting, is_use_cuda
    
    # 생각하는 상태
    is_chatting = True  # $$$ 영향력 조사 없이 추가
    set_status('think')
    
    result, result_jp, result_ko = conversation(text)
    if not result:
        return None, None
    
    audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_ko, use_cuda=is_use_cuda, type='single', sid=0)
    sound_length = play_wav(audio, loaded_settings['setting_volume'])
    # is_chatting = False  # $$$ 전공정 종료 시점?  # 발언 목소리를 다시 들어버리네...
    
    if not result:
        return 999, None 

    global setting_lang
    if setting_lang == 'jp':
        answer_language = result_jp
    elif setting_lang == 'ko':
        answer_language = result_ko
    else:
        answer_language = result
        setting_lang = 'en'
    # if loaded_settings['setting_chat_language'] == '한국어': 
    #     answer_language = translate(answer_jp, 'ko')
    # if loaded_settings['setting_chat_language'] == 'English':
    #     answer_language = answer

    # if loaded_settings['setting_history_folder']:
    #     update_history_log(loaded_settings['setting_name']+" : "+text)
    #     update_history_log(loaded_settings['setting_char']+" : "+answer_language)

    # return sound_length, answer_language
    answer = dict()
    answer['setting_lang'] = setting_lang
    answer['answer_en'] = result
    answer['answer_ko'] = result_ko
    answer['answer_jp'] = result_jp
    return 8, answer # * 1000 하더라

# Thread 관련
# 자연소리일 경우는 4글자 이상의 길이단어가 연달아 3번이상 반복...!  > 같은 단어가 나오는지 확인해야 하는 데 그게 누락 된듯
def check_if_repeated(text):
    length = len(text)
    half_length = length // 2
    sub_string = ""
    
    # 가능한 패턴 길이를 4부터 half_length까지 확인
    for i in range(4, half_length + 1):
        for j in range(half_length - i + 1):
            sub_string = text[j:j + i]
            repeats = text.count(sub_string)
            chk1 = text[j+i:j+2*i]
            chk2 = text[j+2*i:j+3*i]

            if repeats >= 3 and sub_string == chk1 == chk2:
                print(sub_string, repeats)
                return False
    # print(sub_string, repeats)
    return True

def chat_key_listener():
    global is_chat_key_thread_activated
    hook = keyboard.on_press_key(loaded_settings['setting_chat_key'], on_click_async)
    
    while is_chat_key_thread_activated:  
        time.sleep(0.2)  # 0.2초 대기 후 다음 반복
    keyboard.unhook(hook) # 쓰레드가 종료될 때 이벤트 리스너 제거

def talk_listener():
    global is_talk_thread_activated, is_dragging, is_chatting, is_waiting
    global recognizer
    global chat_question
    global loaded_settings, ask_balloon, status_balloon
    try:
        with sr.Microphone() as source:  
            while is_talk_thread_activated:  
                if loaded_settings['setting_talk_mode'] == "Manual":
                    if not is_dragging and not is_chatting and not is_waiting:
                        try:
                            if keyboard.is_pressed(loaded_settings['setting_talk_key']):  # scroll lock 키가 눌리면 음성 인식 시작
                                print("Manual - key input")
                                is_chatting = True
                                set_status('think')
                                # show_status_balloon(image_folder='./assets/fx/loading2')
                                try:
                                    audio = recognizer.listen(source)
                                    print("Manual - listen end")
                                    # print("음성을 텍스트로 변환 중...")  # 여기서 'whisper'를 사용
                                    if loaded_settings['setting_talk_language'] == '日本語':
                                        text = recognizer.recognize_fasterwhisper(audio, language="ja", model=loaded_settings['setting_talk_quality']) 
                                    elif loaded_settings['setting_talk_language'] == 'English':
                                        text = recognizer.recognize_fasterwhisper(audio, language="en", model=loaded_settings['setting_talk_quality']) 
                                    elif loaded_settings['setting_talk_language'] == '한국어':
                                        text = recognizer.recognize_fasterwhisper(audio, language="ko", model=loaded_settings['setting_talk_quality'])
                                    else:
                                        text = recognizer.recognize_fasterwhisper(audio, language="ja", model=loaded_settings['setting_talk_quality'])  
                                    print("recognize_fasterwhisper end")
                                    kill_status_balloon()
                                    if text and not is_dragging and check_if_repeated(text):
                                        print("인식된 텍스트: {}".format(text))
                                        is_chatting = True
                                        set_status('think')
                                        # sound_length, answer = send_chat(text)
                                        # root.after(0, show_answer_balloon, sound_length, answer)  # tkinter은 메인 쓰레드에서만 사용하기 때문에 queue에 함수 저장
                                        chat_question = text  # chat_listener가 가져감
                                    else:
                                        print('말 없음')
                                        is_chatting = False
                                        set_status('idle')
                                        time.sleep(0.2)
                                except sr.WaitTimeoutError as e:
                                    # print(e)
                                    # print('time out')
                                    pass
                                except sr.UnknownValueError:
                                    print("음성을 인식할 수 없습니다.")
                                except sr.RequestError as e:
                                    print("Google API 요청에 실패했습니다. 에러: {}".format(e))
                        except Exception:
                            print('no key')
                            is_chatting = False
                            set_status('idle')
                elif loaded_settings['setting_talk_mode'] == "Auto":
                    if not is_dragging and not is_chatting:
                        print("Auto : 말하세요...")
                        try:                            
                            # if loaded_settings['setting_ai_sr'] == "TikiTaka":
                            #     recognizer.adjust_for_ambient_noise(source)
                            #     try:
                            #         audio = recognizer.listen_in_background(source, talk_tikitaka_callback)  
                            #     except:
                            #         time.sleep(1)
                            # else:
                            root.after(0, show_status_balloon)
                            # audio = recognizer.listen(source, timeout=3)  
                            audio = recognizer.listen(source, timeout=1)  
                            print("Auto : listen 종료...")
                            if status_balloon:
                                status_balloon.set_image_folder('./assets/fx/loading2')
                            # print("음성을 텍스트로 변환 중...")  # 여기서 'whisper'를 사용
                            if loaded_settings['setting_talk_language'] == '日本語':
                                text = recognizer.recognize_fasterwhisper(audio, language="ja", model=loaded_settings['setting_talk_quality']) 
                            elif loaded_settings['setting_talk_language'] == 'English':
                                text = recognizer.recognize_fasterwhisper(audio, language="en", model=loaded_settings['setting_talk_quality']) 
                            elif loaded_settings['setting_talk_language'] == '한국어':
                                text = recognizer.recognize_fasterwhisper(audio, language="ko", model=loaded_settings['setting_talk_quality'])
                            else:
                                text = recognizer.recognize_fasterwhisper(audio, language="ja", model=loaded_settings['setting_talk_quality'])   
                            if text and not is_dragging and check_if_repeated(text):
                                if status_balloon:
                                    status_balloon.kill_balloon()
                                # $$$ 대화
                                print("인식된 텍스트: {}".format(text))
                                
                                if loaded_settings['setting_ai_sr'] == "check":
                                    ask_balloon = SRBalloon(text)
                                    while ask_balloon:
                                        time.sleep(0.2)  # 취소시 재녹음을 위해 조금 서두를 필요는 있음
                                else:                              
                                    is_chatting = True
                                    set_status('think')      
                                    # sound_length, answer = send_chat(text)
                                    # root.after(0, show_answer_balloon, sound_length, answer)  # tkinter은 메인 쓰레드에서만 사용하기 때문에 queue에 함수 저장
                                    # chat_question = text  # chat_listener가 가져감
                                    sound_length, answer = send_chat(text)
                                    if answer:
                                        sound_length = 999  # $$$ 임시
                                        root.after(0, show_answer_balloon, sound_length, answer)
                            else:
                                time.sleep(0.2)
                                is_chatting = False
                                set_status('idle')
                        except sr.WaitTimeoutError as e:
                            time.sleep(0.2)
                        except sr.UnknownValueError:
                            print("음성을 인식할 수 없습니다.")
                        except sr.RequestError as e:
                            print("음성 인식 엔진에 오류가 발생했습니다. 에러: {}".format(e))
                time.sleep(0.2)  # 0.2초 대기 후 다음 반복
    except Exception as e:
        print(e)
        print('감지 오디오 기기 없음')
        is_talk_thread_activated = False

def talk_tikitaka_callback(recognizer, audio):
    print('callbacked!')
    global loaded_settings
    if loaded_settings['setting_talk_language'] == '日本語':
        text = recognizer.recognize_fasterwhisper(audio, language="ja", model=loaded_settings['setting_talk_quality']) 
    elif loaded_settings['setting_talk_language'] == 'English':
        text = recognizer.recognize_fasterwhisper(audio, language="en", model=loaded_settings['setting_talk_quality']) 
    elif loaded_settings['setting_talk_language'] == '한국어':
        text = recognizer.recognize_fasterwhisper(audio, language="ko", model=loaded_settings['setting_talk_quality'])
    else:
        text = recognizer.recognize_fasterwhisper(audio, language="ja", model=loaded_settings['setting_talk_quality'])   
    if text and not is_dragging and check_if_repeated(text):
        sound_length, answer = send_chat(text)
        if answer:
            sound_length = 999  # $$$ 임시
            root.after(0, show_answer_balloon, sound_length, answer)
        
        # # $$$ 대화
        # print("인식된 텍스트: {}".format(text))
        
        # if loaded_settings['setting_ai_sr'] == "check":
        #     ask_balloon = SRBalloon(text)
        #     while ask_balloon:
        #         time.sleep(0.2)  # 취소시 재녹음을 위해 조금 서두를 필요는 있음
        # else:                              
        #     is_chatting = True
        #     set_status('think')      
        #     # sound_length, answer = send_chat(text)
        #     # root.after(0, show_answer_balloon, sound_length, answer)  # tkinter은 메인 쓰레드에서만 사용하기 때문에 queue에 함수 저장
        #     # chat_question = text  # chat_listener가 가져감
        #     sound_length, answer = send_chat(text)
        #     if answer:
        #         sound_length = 999  # $$$ 임시
        #         root.after(0, show_answer_balloon, sound_length, answer)


def talk_listener_test():
    global recognizer, is_sr_test, sr_test_text, is_talk_thread_activated
    try:
        with sr.Microphone() as source:  
            while is_talk_thread_activated and is_sr_test:  
                try:
                    print("Test - input")
                    try:
                        audio = recognizer.listen(source)
                        print("Test - listen end")
                        # print("음성을 텍스트로 변환 중...")  # 여기서 'whisper'를 사용
                        if loaded_settings['setting_talk_language'] == '日本語':
                            sr_test_text = recognizer.recognize_fasterwhisper(audio, language="ja", model=loaded_settings['setting_talk_quality']) 
                        elif loaded_settings['setting_talk_language'] == 'English':
                            sr_test_text = recognizer.recognize_fasterwhisper(audio, language="en", model=loaded_settings['setting_talk_quality']) 
                        elif loaded_settings['setting_talk_language'] == '한국어':
                            sr_test_text = recognizer.recognize_fasterwhisper(audio, language="ko", model=loaded_settings['setting_talk_quality'])
                        else:
                            sr_test_text = recognizer.recognize_fasterwhisper(audio, language="ja", model=loaded_settings['setting_talk_quality'])  
                        print("recognize_fasterwhisper end")
                        if sr_test_text and check_if_repeated(sr_test_text):
                            print("인식된 텍스트: {}".format(sr_test_text))
                        else:
                            print('말 없음')
                            time.sleep(0.2)
                    except sr.WaitTimeoutError as e:
                        print('time out')
                        pass
                    except sr.UnknownValueError:
                        print("음성을 인식할 수 없습니다.")
                    except sr.RequestError as e:
                        print("Google API 요청에 실패했습니다. 에러: {}".format(e))
                except Exception as e:
                    print(e)
                    print('no key')
                time.sleep(0.2)  # 0.2초 대기 후 다음 반복
    except Exception as e:
        print(e)
        print('감지 오디오 기기 없음')
        is_talk_thread_activated = False

# 메뉴 / 설정 관련
######################################################################
def save_settings():
    global loaded_settings
    # config 폴더가 없으면 생성
    os.makedirs('config', exist_ok=True)  
    # 설정을 JSON 형식으로 저장
    with open('config/setting.json', 'w', encoding='utf-8') as file:
        json.dump(loaded_settings, file, ensure_ascii=False, indent=4)
    print('save settings in config/setting.json')

import os
import json
import uuid

# 저장된 설정을 불러오는 함수
def load_settings():
    # 최초언어 로딩 세팅
    init_lang = ''
    try:
        with open('config/install.json', 'r', encoding='utf-8') as file:
            settings_install = json.load(file)
            init_lang = settings_install['language']
    except:
        pass       
    
    # 로딩 세팅
    try:
        with open('config/setting.json', 'r', encoding='utf-8') as file:
            settings = json.load(file)
            
            # Installer에서 정한 이름 (변경시 그쪽도 갱신)
            if 'version' not in settings:
                settings['version'] = 1
                print('load_settings: version error')
            if 'version_name' not in settings:
                settings['version_name'] = '1.0.0'
                print('load_settings: version_name error')
            # 로딩옵션
            if 'setting_load_option' not in settings or settings['setting_load_option'] not in ["Fast", "Normal", "Custom"]:
                settings['setting_load_option'] = "Normal"
                print('load_settings: setting_load_option error')
            if 'setting_program_type' not in settings or settings['setting_program_type'] not in ["CPU", "GPU"]:
                settings['setting_program_type'] = "CPU"
                print('load_settings: setting_program_type error')
            if 'setting_load_option_customlist' not in settings:
                settings['setting_load_option_customlist'] = ['conversation']                    
            # Setting 원본         
            if 'setting_language' not in settings or settings['setting_language'] not in ["日本語", "English", "한국어"]:
                settings['setting_language'] = init_lang if init_lang else "한국어"
                print('load_settings: setting_language error')
            if 'setting_name' not in settings:
                settings['setting_name'] = 'Sensei'
            if 'setting_uid' not in settings:
                settings['setting_uid'] = str(uuid.uuid4())
            if 'setting_char' not in settings:
                settings['setting_char'] = 'arona'
                print('load_settings: setting_char error')
            if 'setting_size' not in settings or not (0 < settings['setting_size'] <= 2):
                settings['setting_size'] = 1
                print('load_settings: setting_size error')
            if 'setting_size_effecter' not in settings or not (0 <= settings['setting_size_effecter'] <= 1):
                settings['setting_size_effecter'] = 0
                print('load_settings: setting_size_effecter error')
            if 'setting_chat_mode' not in settings or settings['setting_chat_mode'] not in ["OFF", "Click", "Key"]:
                settings['setting_chat_mode'] = 'Click'
                print('load_settings: setting_chat_mode error')
            if 'setting_chat_key' not in settings:
                settings['setting_chat_key'] = ''
                print('load_settings: setting_chat_key error')
            if 'setting_chat_language' not in settings or settings['setting_chat_language'] not in ["日本語", "English", "한국어"]:
                settings['setting_chat_language'] = init_lang if init_lang else "한국어"
                print('load_settings: setting_chat_language error')
            if 'setting_chat_click_sensitivity' not in settings:
                settings['setting_chat_click_sensitivity'] = 100
                print('load_settings: setting_chat_click_sensitivity error')
            if 'setting_voice_mode' not in settings or settings['setting_voice_mode'] not in ["OFF", "CPU", "GPU"]:
                settings['setting_voice_mode'] = 'CPU'
                print('load_settings: setting_voice_mode error')
            if 'setting_volume' not in settings or not (0 <= settings['setting_volume'] <= 200):
                settings['setting_volume'] = 75
                print('load_settings: setting_volume error')
            if 'setting_is_volume_on' not in settings:
                settings['setting_is_volume_on'] = True
                print('load_settings: setting_is_volume_on error')
            if 'setting_is_gravity' not in settings:
                settings['setting_is_gravity'] = False
                print('load_settings: setting_is_gravity error')
            if 'setting_mobility' not in settings or not (0 <= settings['setting_mobility'] <= 2):
                settings['setting_mobility'] = 1
                print('load_settings: setting_mobility error')
            if 'setting_moving_speed' not in settings or not (0 <= settings['setting_moving_speed'] <= 1):
                settings['setting_moving_speed'] = 0
                print('load_settings: setting_moving_speed error')
            if 'setting_collision' not in settings:
                settings['setting_collision'] = 'Task bar'
                print('load_settings: setting_collision error')
            if 'setting_ai' not in settings or settings['setting_ai'] not in ["Inworld", "chatGPT", "bard"]:
                settings['setting_ai'] = 'Inworld'
                print('load_settings: setting_ai error')
            if 'setting_translator' not in settings or settings['setting_translator'] not in ["Google", "DeepL"]:
                settings['setting_translator'] = 'Google'
                print('load_settings: setting_translator error')
            if 'setting_talk_mode' not in settings or settings['setting_talk_mode'] not in ["OFF", "Auto", "Manual"]:
                settings['setting_talk_mode'] = 'OFF'
                print('load_settings: setting_talk_mode error')
            if 'setting_talk_key' not in settings:
                settings['setting_talk_key'] = ''
                print('load_settings: setting_talk_key error')
            if 'setting_talk_language' not in settings or settings['setting_talk_language'] not in ["日本語", "English", "한국어"]:
                settings['setting_talk_language'] = init_lang if init_lang else "한국어"
                print('load_settings: setting_talk_language error')
            if 'setting_talk_quality' not in settings or settings['setting_talk_quality'] not in ["tiny", "base", "small", "medium"]:
                settings['setting_talk_quality'] = 'base'
                print('load_settings: setting_talk_quality error')
            if 'setting_can_stop_chat' not in settings:
                settings['setting_can_stop_chat'] = False
                print('load_settings: setting_can_stop_chat error')
            if 'setting_history_folder' not in settings:
                settings['setting_history_folder'] = './history'
                print('load_settings: setting_history_folder error')
            # Eden쪽 세팅
            if 'setting_language' not in settings or settings['setting_language'] not in ["日本語", "English", "한국어"]:
                settings['setting_language'] = init_lang if init_lang else "한국어"
                print('load_settings: setting_language error')
            if 'setting_preload_voice' not in settings:
                settings['setting_preload_voice'] = False
                print('load_settings: setting_preload_voice error')
            if 'setting_preload_sr' not in settings:
                settings['setting_preload_sr'] = False
                print('load_settings: setting_preload_sr error')
            # deepL Key쪽 세팅
            if 'setting_key_deepL' not in settings:
                settings['setting_key_deepL'] = ''
                print('load_settings: setting_key_deepL error') 
            # AI쪽 세팅
            if 'setting_ai_stream' not in settings:
                settings['setting_ai_stream'] = 'on'
                print('load_settings: setting_ai_stream error') 
            if 'setting_ai_sr' not in settings:  # "send", "check", "TikiTaka"
                settings['setting_ai_sr'] = 'send'
                print('load_settings: setting_ai_sr error') 
            if 'setting_ai_web' not in settings:
                settings['setting_ai_web'] = 'off'
                print('load_settings: setting_ai_web error') 
            if 'setting_ai_story' not in settings:
                settings['setting_ai_story'] = 'off'
                print('load_settings: setting_ai_story error') 
            if 'setting_ai_memory' not in settings:
                settings['setting_ai_memory'] = 'off'
                print('load_settings: setting_ai_memory error') 
            # if 'setting_ai_image' not in settings:
            #     settings['setting_ai_image'] = 'off'
            #     print('load_settings: setting_ai_image error') 
            return settings
    except FileNotFoundError:
        # 파일이 없을 경우 기본값 설정
        settings = {
            # Installer에서 정한 이름 (변경시 그쪽도 갱신)
            "version": 1,
            "version_name": '1.0.0',
            # 로딩옵션
            "setting_load_option" : "Normal",
            "setting_load_option_customlist" : ['conversation'],      
            "setting_program_type" : "CPU",
            # Main 세팅
            "setting_name": 'sensei',
            "setting_uid": str(uuid.uuid4()),
            "setting_char": 'arona',
            "setting_size": 1,
            "setting_size_effecter": 0,
            "setting_chat_mode": "Click",
            "setting_chat_key": "",
            "setting_chat_language": init_lang if init_lang else "日本語",
            "setting_chat_click_sensitivity": 100,
            "setting_voice_mode": "CPU",
            "setting_volume": 75,
            "setting_is_volume_on": True,
            "setting_is_gravity": False,
            "setting_mobility": 1,
            "setting_moving_speed": 0,
            "setting_collision": 'Task bar',
            "setting_ai": 'Inworld',
            "setting_translator": 'Google',
            "setting_talk_mode": 'OFF',
            "setting_talk_key": '',
            "setting_talk_language": init_lang if init_lang else "日本語",
            "setting_talk_quality": 'base',
            "setting_can_stop_chat": False,
            "setting_history_folder": './history',
            "setting_language": init_lang if init_lang else "日本語",
            "setting_preload_voice": False,
            "setting_preload_sr": False,
            "setting_key_deepL": "",
            # AI 관련 설정
            "setting_ai_stream" : "on",
            "setting_ai_sr" : "send",  # "send", "check". "TikiTaka"
            "setting_ai_web" : "off",
            "setting_ai_story" : "off",
            "setting_ai_memory" : "off",
            # "setting_ai_image" : "off",
        }
        return settings

def get_message(text, is_special=False):
    global loaded_settings
    return getMessage(text, loaded_settings['setting_language'], is_special)

def show_status_balloon(e=None, image_folder='./assets/fx/loading1'):
    global status_balloon
    if status_balloon:
        status_balloon.kill_balloon()
    status_balloon = StatusBalloon(image_folder=image_folder, master=root)

def kill_status_balloon():
    global status_balloon
    if status_balloon:
        status_balloon.kill_balloon()

def open_settings(e=None):
    settings_window = tk.Toplevel(root, padx=5, pady=5)
    settings_window.title("Settings")
    # settings_window.geometry("560x535")  # 풀 옵션
    settings_window.geometry("510x300")
    
    global settings_keyboard_hooks
    settings_keyboard_hooks = list()  # 세팅 중 키보드 이벤트들
    def on_closing():
        global settings_keyboard_hooks
        for hook in settings_keyboard_hooks:
            keyboard.unhook(hook)
        settings_keyboard_hooks = list()
        save_settings()
        settings_window.destroy()
    settings_window.protocol("WM_DELETE_WINDOW", on_closing) 

    # 초기화
    frame_row_idx = 0

    # Frame : Player
    frame_player = tk.Frame(settings_window, padx=10)#, borderwidth=1, relief=tk.SOLID)
    frame_player.grid(row=frame_row_idx, column=0, sticky="nsew")
    frame_row_idx+=1

    name_label = tk.Label(frame_player, text=get_message("Name"), width=8, anchor='w')
    name_label.grid(row=0, column=0, padx=10, pady=(4,8), sticky="w")
    HoverTip(name_label, "User name")

    def on_name_text_changed(event):
        loaded_settings['setting_name'] = name_text.get("1.0", "end-1c") 
        save_settings()
    name_text = tk.Text(frame_player, wrap="none", width=16, height=1)
    name_text.grid(row=0, column=1, padx=10, pady=2, sticky="e")
    name_text.insert("1.0", loaded_settings['setting_name'])
    name_text.bind("<KeyRelease>", on_name_text_changed)

    # Frame : Conversation
    frame_conversation = tk.Frame(settings_window, padx=10, borderwidth=1, relief=tk.SOLID)
    frame_conversation.grid(row=frame_row_idx, column=0, sticky="nsew")
    frame_row_idx+=1

    # Frame : Conversation > Language > Label, desc
    frame_language = tk.Frame(frame_conversation)
    frame_language.grid(row=0, column=0, sticky="we", pady=(2,0))
    frame_language_label = tk.Frame(frame_language)
    frame_language_label.grid(row=0, column=0, sticky="we")
    frame_language_desc = tk.Frame(frame_language)
    frame_language_desc.grid(row=0, column=1, sticky="we")

    language_label = tk.Label(frame_language_label, text="Language", anchor='w', width=8)
    language_label.grid(row=0, column=0, padx=5, sticky="w")
    HoverTip(language_label, "Languages to use in UI/Settings")

    def update_language():
        loaded_settings['setting_language'] = language_var.get()
        save_settings()
        # 언어에 맞춰 세팅 초기화
        name_label.config(text=get_message("Name"))
        # talk_quality_download_btn.config(text=get_message("Download"))
        # talk_quality_test_btn.config(text=get_message("Test"))
        # chat_click_sensitivity_label.config(text=get_message("Click Reaction"))
        # update_setting_translator() # translator_btn_input_key

    language_var = tk.StringVar(value=loaded_settings['setting_language'])
    for column_idx, lang in enumerate(["한국어", "English", "日本語"]):
        lang_frame = tk.Frame(frame_language_desc)
        lang_frame.grid(row=0, column=column_idx, sticky="we", padx=20)
        lang_radio = tk.Radiobutton(lang_frame, text=lang, variable=language_var, value=lang, command=update_language)
        lang_radio.grid(row=0, column=0, sticky="we")

    # Frame : Conversation > Voice > Label, desc
    frame_voice = tk.Frame(frame_conversation)
    frame_voice.grid(row=1, column=0, sticky="we")
    frame_voice_label = tk.Frame(frame_voice)
    frame_voice_label.grid(row=0, column=0, sticky="we")
    frame_voice_desc = tk.Frame(frame_voice)
    frame_voice_desc.grid(row=0, column=1, sticky="we")
    # frame_voice_desc_mode = tk.Frame(frame_voice_desc)
    # frame_voice_desc_mode.grid(row=0, column=0, sticky="we")
    frame_voice_desc_volume = tk.Frame(frame_voice_desc)
    frame_voice_desc_volume.grid(row=0, column=0, sticky="we")  # desc_mode 비활성화로 1>0으로
    
    
    voice_label = tk.Label(frame_voice_label, text="Voice", anchor='w', width=8)
    voice_label.grid(row=0, column=0, padx=5, pady=(0,5), sticky="w")
    HoverTip(voice_label, "Volume")
    
    # GPU 관련 옵션 추가시 활성화 할 것
    # def update_voice_mode():
    #     loaded_settings['setting_voice_mode'] = voice_mode_var.get()
    #     save_settings()
    #     if voice_mode_var.get() == "GPU":
    #         ask_question_box = MessageBoxAskQuestion(settings_window, "Confirm", "Want to enable GPU acceleration to voice generation right now?")
    #         settings_window.wait_window(ask_question_box)
    #         if ask_question_box.result:   
    #             activate_gpu()
    #     else:
    #         # 가속 켜져있으면 끄기
    #         deactivate_gpu()
        
    # voice_mode_var = tk.StringVar(value=loaded_settings['setting_voice_mode'])
    # for column_idx, voice_mode in enumerate(["OFF", "CPU", "GPU"]):
    #     voice_mode_frame = tk.Frame(frame_voice_desc_mode, width=12)
    #     voice_mode_frame.grid(row=0, column=column_idx, sticky="w", padx=20,pady=(5,0))
    #     voice_mode_radio = tk.Radiobutton(voice_mode_frame, text=voice_mode, variable=voice_mode_var, value=voice_mode, command=update_voice_mode)
    #     voice_mode_radio.grid(row=0, column=0, sticky="w")


    def update_volume(value):
        loaded_settings['setting_volume'] = float(volume_slider.get())
        save_settings()
    def toggle_volume():
        loaded_settings['setting_is_volume_on'] = not loaded_settings['setting_is_volume_on']
        if loaded_settings['setting_is_volume_on']:
            volume_button.config(image=img_volume_on)
        else:
            volume_button.config(image=img_volume_off)
        save_settings()

    # img_volume_off = ImageTk.PhotoImage(Image.open('./assets/png/speaker_off.png').resize((15, 15)))
    # img_volume_on = ImageTk.PhotoImage(Image.open('./assets/png/speaker_on.png').resize((15, 15)))
    volume_button = tk.Button(frame_voice_desc_volume, image=img_volume_on, command=toggle_volume, width=18, height=18)
    if not loaded_settings['setting_is_volume_on']:
        volume_button.config(image=img_volume_off)
    volume_button.grid(row=0, column=5, padx=(20,0), sticky="w")
    HoverTip(volume_button, "Mute")

    volume_slider = Scale(frame_voice_desc_volume, length=200, from_=0, to=100, resolution=1, orient=tk.HORIZONTAL) #, command=update_size)
    volume_slider.set(loaded_settings['setting_volume'])  # 기본값 설정
    volume_slider.grid(row=0, column=6, padx=(5,10), sticky="w")
    volume_slider.bind("<ButtonRelease-1>", update_volume)  # 슬라이더에서 손 땠을때 이벤트 동작하게

    # Frame : Conversation > Chat > Label, desc
    frame_chat = tk.Frame(frame_conversation)
    frame_chat.grid(row=2, column=0, sticky="we", pady=(0,2))
    frame_chat_label = tk.Frame(frame_chat)
    frame_chat_label.grid(row=0, column=0, sticky="we")
    frame_chat_desc = tk.Frame(frame_chat)
    frame_chat_desc.grid(row=0, column=1, sticky="we")
    frame_chat_desc_volume = tk.Frame(frame_chat_desc)
    frame_chat_desc_volume.grid(row=0, column=0, sticky="we")
    frame_chat_desc_mode = tk.Frame(frame_chat_desc)
    frame_chat_desc_mode.grid(row=1, column=0, sticky="we")
    frame_chat_click_sensitivity = tk.Frame(frame_chat_desc)
    frame_chat_click_sensitivity.grid(row=2, column=0, sticky="we")
    
    chat_label = tk.Label(frame_chat_label, text="Chat", anchor='w', width=8)
    chat_label.grid(row=0, column=0, padx=5, pady=(0,35), sticky="w")

    def update_chat_mode():
        global is_chat_key_thread_activated, chat_key_thread  
        global settings_keyboard_hooks
        loaded_settings['setting_chat_mode'] = chat_mode_var.get()
        save_settings()
        if chat_mode_var.get() == "OFF":
            chat_key_entry.config(state=tk.DISABLED)
            # talk_key_entry.config(state=tk.DISABLED)
            for hook in settings_keyboard_hooks:
                keyboard.unhook(hook)
            settings_keyboard_hooks = list()

        elif chat_mode_var.get() == "Click":
            chat_key_entry.config(state=tk.DISABLED)
            # talk_key_entry.config(state=tk.DISABLED)
            for hook in settings_keyboard_hooks:
                keyboard.unhook(hook)
            settings_keyboard_hooks = list()
        elif chat_mode_var.get() == "Key":
            chat_key_entry.config(state=tk.NORMAL)
            # talk_key_entry.config(state=tk.DISABLED)
            chat_key_entry.focus_set()
            for hook in settings_keyboard_hooks:
                keyboard.unhook(hook)
            settings_keyboard_hooks = list()
            hook = keyboard.hook(update_chat_key)
            settings_keyboard_hooks.append(hook)
        # 기존 chat_key_thread 있을 경우 종료.
        is_chat_key_thread_activated = False
        if chat_key_thread and chat_key_thread.is_alive():
            chat_key_thread.join()
        
    def update_chat_key(event):
        global is_chat_key_thread_activated, chat_key_thread  
        global settings_keyboard_hooks  
        chat_key_old = chat_key_var.get()  # 키 변경 실패시 돌릴 키
        chat_key_entry.delete(0, tk.END)
        chat_key_entry.config(state=tk.DISABLED)
        for hook in settings_keyboard_hooks:
            keyboard.unhook(hook)
        settings_keyboard_hooks = list()
        if event.name == 'enter':
            MessageBoxShowInfo(settings_window, "Error", "key [ENTER] is not allowed.")
            chat_key_var.set(chat_key_old)
            return
        if event.name != loaded_settings['setting_chat_key']:
            chat_key_var.set(event.name)
            loaded_settings['setting_chat_key'] = chat_key_var.get()
            save_settings()
        else:
            chat_key_var.set(chat_key_old)
        # chat_key_thread 시작 (0.2초 후)
        time.sleep(0.2)  
        if not chat_key_thread or not chat_key_thread.is_alive():
            is_chat_key_thread_activated = True
            chat_key_thread = threading.Thread(target=chat_key_listener)
            chat_key_thread.start()
        else:
            # 기존 thread 종료하고 새로 시작
            is_chat_key_thread_activated = False
            chat_key_thread.join()
            chat_key_thread = threading.Thread(target=chat_key_listener)
            chat_key_thread.start()                
        
    chat_mode_var = tk.StringVar(value=loaded_settings['setting_chat_mode'])
    for column_idx, chat_mode in enumerate(["OFF", "Click", "Key"]):
        chat_mode_frame = tk.Frame(frame_chat_desc_mode)
        chat_mode_frame.grid(row=0, column=column_idx, sticky="we", padx=20)
        chat_mode_radio = tk.Radiobutton(chat_mode_frame, text=chat_mode, variable=chat_mode_var, value=chat_mode, command=update_chat_mode)
        chat_mode_radio.grid(row=0, column=0, sticky="we")
        if chat_mode == "Click":
            HoverTip(chat_mode_radio, "Start chat with a single left click")
        if chat_mode == "Key":
            HoverTip(chat_mode_radio, "keyboard key to start chat\n(click also applies)")
            
    chat_key_var = tk.StringVar(value=loaded_settings['setting_chat_key'])
    chat_key_entry = tk.Entry(frame_chat_desc_mode, state=tk.DISABLED, width=10, textvariable=chat_key_var)
    chat_key_entry.grid(row=0, column=4, padx=10, pady=2, sticky="we")

    def update_chat_language():
        loaded_settings['setting_chat_language'] = chat_language_var.get()
        save_settings()
    chat_language_var = tk.StringVar(value=loaded_settings['setting_chat_language'])
    for column_idx, chat_language in enumerate(["한국어", "English", "日本語"]):
        chat_language_frame = tk.Frame(frame_chat_desc_mode)
        chat_language_frame.grid(row=1, column=column_idx, sticky="we", padx=20)
        chat_language_radio = tk.Radiobutton(chat_language_frame, text=chat_language, variable=chat_language_var, value=chat_language, command=update_chat_language)
        chat_language_radio.grid(row=0, column=0, sticky="we")
        HoverTip(chat_language_radio, "Chat response language\n(Questions can be asked in any language)")

    # def update_chat_click_sensitivity(value):
    #     loaded_settings['setting_chat_click_sensitivity'] = int(chat_click_sensitivity_slider.get())
    #     save_settings()
    # chat_click_sensitivity_label = tk.Label(frame_chat_click_sensitivity, text=get_message("Click Reaction"), width=13)
    # chat_click_sensitivity_label.grid(row=0, column=0, padx=10, sticky="w")
    # chat_click_sensitivity_slider = Scale(frame_chat_click_sensitivity, from_=50, to=1000, resolution=10, orient=tk.HORIZONTAL) #, command=update_size)
    # chat_click_sensitivity_slider.set(loaded_settings['setting_chat_click_sensitivity'])  
    # chat_click_sensitivity_slider.grid(row=0, column=1, padx=10, sticky="w")
    # chat_click_sensitivity_slider.bind("<ButtonRelease-1>", update_chat_click_sensitivity)  # 슬라이더에서 손 땠을때 이벤트 동작하게

    # Frame : Conversation > Talk > Label, desc
    # frame_talk = tk.Frame(frame_conversation)
    # frame_talk.grid(row=3, column=0, sticky="we", pady=2)
    # frame_talk_label = tk.Frame(frame_talk)
    # frame_talk_label.grid(row=0, column=0, sticky="we")
    # frame_talk_desc = tk.Frame(frame_talk)
    # frame_talk_desc.grid(row=0, column=1, sticky="we")
    # frame_talk_desc_quality = tk.Frame(frame_talk_desc)
    # frame_talk_desc_quality.grid(row=0, column=0, sticky="we")
    # frame_talk_desc_mode = tk.Frame(frame_talk_desc)
    # frame_talk_desc_mode.grid(row=1, column=0, sticky="we")

    # talk_label = tk.Label(frame_talk_label, text="Talk", anchor='w', width=8)
    # talk_label.grid(row=0, column=0, padx=5, pady=(0, 50), sticky="w")
    
    # def update_setting_talk_quality(event):
    #     loaded_settings['setting_talk_quality'] = talk_quality_dropdown.get()
    #     save_settings()
    # def get_talk_quality_options():
    #     talk_quality_options = list()
    #     for sound_option in ['tiny', 'base', 'small', 'medium']:
    #         os.makedirs('whisper', exist_ok=True)
    #         path = './whisper/' + sound_option + '.pt'
    #         if os.path.exists(path):
    #             talk_quality_options.append(sound_option)    
    #     return talk_quality_options
    # talk_quality_options = get_talk_quality_options()
    # if not talk_quality_options:
    #     loaded_settings['setting_talk_quality'] = ""
    # if loaded_settings['setting_talk_quality'] not in talk_quality_options:
    #     loaded_settings['setting_talk_quality'] = "base"
    # talk_quality_dropdown = ttk.Combobox(frame_talk_desc_quality, values=talk_quality_options, state="readonly", width=8)
    # talk_quality_dropdown.set(loaded_settings['setting_talk_quality'])
    # talk_quality_dropdown.grid(row=0, column=0, padx=(25,0), pady=(8,5), sticky="w")
    # talk_quality_dropdown.bind("<<ComboboxSelected>>", update_setting_talk_quality)
    
    # def on_subwindow_close(button_name, window):
    #     talk_quality_dropdown['values'] = get_talk_quality_options() # 옵션 갱신 Download쪽인데 그냥하자
    #     open_subwindows.remove(button_name)
    #     window.destroy()
    
    # def create_sr_download_window():
    #     # 기존 창 열려있는게 없을 경우. (있을 경우 포커스 잡아주려면 추가 변수 설정하기)
    #     if "Sound Recognition Download" not in open_subwindows:
    #         subwindow = tk.Toplevel(settings_window)
    #         subwindow.title("Sound Recognition Download")
    #         subwindow.protocol("WM_DELETE_WINDOW", lambda: on_subwindow_close("Sound Recognition Download", subwindow))
    #         open_subwindows.add("Sound Recognition Download")
    #         subwindow.geometry(f"330x240+{settings_window.winfo_x() + 50}+{settings_window.winfo_y() + 50}")        
            
    #         sound_title_label = tk.Label(subwindow, text=get_message('sound option title'))
    #         sound_title_label.grid(row=0, column=0, pady=5, sticky="nwe")   
            
    #         sound_separator = ttk.Separator(subwindow, orient="horizontal")
    #         sound_separator.grid(row=1, column=0, sticky="nswe", padx=8)

    #         sound_options = ['tiny', 'base', 'small', 'medium']
    #         for i, sound_option in enumerate(sound_options):  
    #             frame_sound = tk.Frame(subwindow, padx=10)
    #             frame_sound.grid(row=i+2, column=0, sticky="nsw")
                
    #             path = './whisper/' + sound_option + '.pt'
    #             status = "YES" if os.path.exists(path) else "NONE"
                
    #             sound_option_label = tk.Label(frame_sound,  anchor="w", text=sound_option, width=6)
    #             sound_option_label.grid(row=0, column=0, pady=5, sticky="e")
                        
    #             sound_option_desc_label = tk.Label(frame_sound,  anchor="w", text=get_message("sound option " + sound_option, is_special=True), width=24)
    #             sound_option_desc_label.grid(row=0, column=1, pady=5, sticky="e", padx=5)
    #             if status == "NONE":
    #                 sound_download_button = tk.Button(frame_sound, text=get_message("Download"), command=lambda option = sound_option, parent=subwindow:download_from_url(parent, 'https://huggingface.co/mingu4969/windows-archive-dist/resolve/main/whisper/'+option+'.pt?download=true','whisper/'+option+'.pt')) # lazy init 방지용
    #                 sound_download_button.grid(row=0, column=2, sticky="w")
                    
    # def create_sr_test_window():
    #     if loaded_settings['setting_talk_mode'] in ["Auto", "Manual"]:
    #         MessageBoxShowInfo(settings_window, "Info", "Please set [Talk] Option to OFF to avoid conflicts.")
    #         return
    #     if "Sound Recognition Test" not in open_subwindows:
    #         subwindow = tk.Toplevel(settings_window)
    #         subwindow.title("Sound Recognition Test")
    #         subwindow.protocol("WM_DELETE_WINDOW", lambda: on_subwindow_close("Sound Recognition Test", subwindow))
    #         open_subwindows.add("Sound Recognition Test")
    #         subwindow.geometry(f"320x90+{settings_window.winfo_x() + 50}+{settings_window.winfo_y() + 50}")
            
    #         sr_test_text_base = get_message("Current setting : ") + talk_quality_dropdown.get() +" / "+loaded_settings['setting_talk_language']+"\n"
    #         sr_test_label = tk.Label(subwindow, text=sr_test_text_base, anchor='nw', justify='left', width=40, height=2, padx=5)
    #         sr_test_label.grid(row=0, column=0, pady=5, sticky="nwe")   
            
    #         sound_separator = ttk.Separator(subwindow, orient="horizontal")
    #         sound_separator.grid(row=1, column=0, sticky="nswe", padx=8)

    #         def sr_test_equip():
    #             sr_test_label.config(text = sr_test_text_base + "Finding Microphone...")
    #             if check_speech_recognition_status():
    #                 sr_test_label.config(text = sr_test_text_base + "Device Detected.")
    #             else:
    #                 sr_test_label.config(text = sr_test_text_base + "No Device Detected.")

    #         def sr_test():
    #             global is_talk_thread_activated, is_sr_test, talk_thread_test, sr_test_text
    #             if talk_thread_test and talk_thread_test.is_alive():
    #                 is_sr_test = False
    #                 is_talk_thread_activated = False
    #                 # talk_thread_test.join()  # $$$ 무한로딩??
    #                 time.sleep(0.5)
    #                 sr_test_label.config(text = sr_test_text_base + sr_test_text)
    #                 return
    #             if is_talk_thread_activated:
    #                 sr_test_label.config(text = sr_test_text_base + "Speech recognition is already working.")
    #                 return
    #             sr_test_label.config(text = sr_test_text_base + "Say Something...(Click Once more to finish)")
                
    #             is_sr_test = True
    #             is_talk_thread_activated = True
    #             talk_thread_test = threading.Thread(target=talk_listener_test)
    #             talk_thread_test.start()

                
    #         frame_sound_test_button = tk.Frame(subwindow)
    #         frame_sound_test_button.grid(row=2, column=0, sticky="we", padx=20)      
    #         sound_test_button = tk.Button(frame_sound_test_button, text="Check Equip", width=12, padx=2, command=lambda :sr_test_equip())
    #         sound_test_button.grid(row=0, column=0, sticky="we", padx=20 ,pady=5)
    #         sound_test_button = tk.Button(frame_sound_test_button, text="Test", width=12, padx=2, command=lambda :sr_test())
    #         sound_test_button.grid(row=0, column=1, sticky="we", padx=20 ,pady=5)

    # open_subwindows = set()
    # talk_quality_download_btn = tk.Button(frame_talk_desc_quality, text=get_message("Download"), width=12, height=1, command=lambda: create_sr_download_window())
    # talk_quality_download_btn.grid(row=0, column=1, sticky="ew", padx=(40,10), pady=2)
    # talk_quality_test_btn = tk.Button(frame_talk_desc_quality, text=get_message("Test"), width=8, height=1, command=lambda: create_sr_test_window())
    # talk_quality_test_btn.grid(row=0, column=2, sticky="ew", padx=5, pady=2)
    
    # def update_talk_mode():
    #     global settings_keyboard_hooks
    #     global is_talk_thread_activated
    #     loaded_settings['setting_talk_mode'] = talk_mode_var.get()
    #     save_settings()
    #     if talk_mode_var.get() == "OFF":
    #         chat_key_entry.config(state=tk.DISABLED)
    #         talk_key_entry.config(state=tk.DISABLED)
    #         for hook in settings_keyboard_hooks:
    #             keyboard.unhook(hook)
    #         settings_keyboard_hooks = list()
    #         deactivate_speech_recognition()
    #     elif talk_mode_var.get() == "Auto":
    #         chat_key_entry.config(state=tk.DISABLED)
    #         talk_key_entry.config(state=tk.DISABLED)
    #         for hook in settings_keyboard_hooks:
    #             keyboard.unhook(hook)
    #         settings_keyboard_hooks = list()
    #         if not is_talk_thread_activated:
    #             ask_question_box = MessageBoxAskQuestion(settings_window, "Confirm", "Want to enable voice recognition right now?")
    #             settings_window.wait_window(ask_question_box)
    #             if ask_question_box.result:   
    #                 activate_speech_recognition()
    #     elif talk_mode_var.get() == "Manual":
    #         chat_key_entry.config(state=tk.DISABLED)
    #         talk_key_entry.config(state=tk.NORMAL)
    #         talk_key_entry.focus_set()
    #         for hook in settings_keyboard_hooks:
    #             keyboard.unhook(hook)
    #         settings_keyboard_hooks = list()
    #         hook = keyboard.hook(update_talk_key)
    #         settings_keyboard_hooks.append(hook)

    # def update_talk_key(event):
    #     global is_talk_thread_activated
    #     talk_key_entry.delete(0, tk.END)
    #     talk_key_entry.config(state=tk.DISABLED)
    #     if event.name != chat_key_var.get():        
    #         talk_key_var.set(event.name)
    #         loaded_settings['setting_talk_key'] = talk_key_var.get()
    #         save_settings()
    #     else:
    #         talk_key_var.set(talk_key_old)
    #         return
    #     global settings_keyboard_hooks
    #     for hook in settings_keyboard_hooks:
    #         keyboard.unhook(hook)
    #     settings_keyboard_hooks = list()
    #     if not is_talk_thread_activated:
    #         ask_question_box = MessageBoxAskQuestion(settings_window, "Confirm", "Want to enable voice recognition right now?")
    #         settings_window.wait_window(ask_question_box)
    #         if ask_question_box.result:   
    #             activate_speech_recognition()
        
    # talk_mode_var = tk.StringVar(value=loaded_settings['setting_talk_mode'])
    # for column_idx, talk_mode in enumerate(["OFF", "Auto", "Manual"]):
    #     talk_mode_frame = tk.Frame(frame_talk_desc_mode)
    #     talk_mode_frame.grid(row=0, column=column_idx, sticky="we", padx=20)
    #     talk_mode_radio = tk.Radiobutton(talk_mode_frame, text=talk_mode, variable=talk_mode_var, value=talk_mode, command=update_talk_mode)
    #     talk_mode_radio.grid(row=0, column=0, sticky="we")
    # talk_key_var = tk.StringVar(value=loaded_settings['setting_talk_key'])
    # talk_key_old = talk_key_var.get()
    # talk_key_entry = tk.Entry(frame_talk_desc_mode, state=tk.DISABLED, width=10, textvariable=talk_key_var)
    # talk_key_entry.grid(row=0, column=4, padx=10, pady=2, sticky="we")

    # def update_talk_language():
    #     loaded_settings['setting_talk_language'] = talk_language_var.get()
    #     save_settings()
    # talk_language_var = tk.StringVar(value=loaded_settings['setting_talk_language'])
    # for column_idx, talk_language in enumerate(["한국어", "English", "日本語"]):
    #     talk_language_frame = tk.Frame(frame_talk_desc_mode)
    #     talk_language_frame.grid(row=1, column=column_idx, sticky="we", padx=20)
    #     talk_language_radio = tk.Radiobutton(talk_language_frame, text=talk_language, variable=talk_language_var, value=talk_language, command=update_talk_language)
    #     talk_language_radio.grid(row=0, column=0, sticky="we")

    # Frame : Conversation > Translator > Label, desc
    # frame_translator = tk.Frame(frame_conversation)
    # frame_translator.grid(row=4, column=0, sticky="we", pady=2)
    # frame_translator_label = tk.Frame(frame_translator)
    # frame_translator_label.grid(row=0, column=0, sticky="we")
    # frame_translator_desc = tk.Frame(frame_translator)
    # frame_translator_desc.grid(row=0, column=1, sticky="we")
    
    # translator_label = tk.Label(frame_translator_label, text="translator", anchor='w', width=8)
    # translator_label.grid(row=0, column=0, padx=5, sticky="w")

    # def update_setting_translator(event=None):
    #     loaded_settings['setting_translator'] = translator_dropdown.get() # 선택된 드롭다운 값에 해당하는 AI 내용물
    #     if loaded_settings['setting_translator'] == "Google":
    #         # 버튼
    #         translator_btn_input_key["state"] = "disabled"
    #         translator_btn_input_key.config(text=get_message("Free"))
    #         # 라벨
    #         translator_label_key_status.config(text="")
    #     elif loaded_settings['setting_translator'] == "DeepL":
    #         # 버튼
    #         translator_btn_input_key["state"] = "normal"
    #         translator_btn_input_key.config(text=get_message("Input"))
    #         # 라벨
    #         if loaded_settings['setting_key_deepL']:
    #             translator_label_key_status.config(text=get_message("Exist"))
    #         else:
    #             translator_label_key_status.config(text="N/A")
    #     else:
    #         # 버튼
    #         translator_btn_input_key["state"] = "disabled"
    #         # 라벨
    #         translator_label_key_status.config(text="N/A")
    #     save_settings()
    
    # def open_trans_api_dialog():
    #     dialog_window_trans = tk.Toplevel(settings_window)
    #     dialog_window_trans.title("API Key (DeepL)")
    #     dialog_window_trans.geometry(f"350x90+{settings_window.winfo_x() + 50}+{settings_window.winfo_y() + 50}")

    #     global loaded_settings

    #     # 하이퍼 링크 함수
    #     def open_link_trans(event):
    #         # messagebox.showinfo("Info", "Creating a video for guidance...")
    #         webbrowser.open_new("https://www.youtube.com/channel/UCTHcOeshRex_2SHkdmqjYqQ")  # 여기에 원하는 링크 주소 입력

    #     # 하이퍼 링크를 표시할 라벨
    #     link_label_trans = tk.Label(dialog_window_trans, text="Need help?", fg="blue", cursor="hand2")
    #     link_label_trans.grid(row=0, column=1, sticky="e")
    #     link_label_trans.bind("<Button-1>", open_link_trans)  # 링크 클릭 시 함수 실행

    #     label_trans = tk.Label(dialog_window_trans, text="Enter KEY:")
    #     label_trans.grid(row=1, column=0, pady=5, sticky="e")

    #     entry_trans = tk.Entry(dialog_window_trans, width=40)
    #     entry_trans.grid(row=1, column=1, pady=5, sticky="w")
    #     entry_trans.focus_force()
    #     if loaded_settings['setting_translator'] == 'DeepL':
    #         entry_trans.insert(0, loaded_settings['setting_key_deepL'])

    #     def test_trans_api_key():
    #         test_key = entry_trans.get()
    #         test_translator = deepl.Translator(test_key)
    #         start_time = time.time()
    #         try:
    #             result = test_translator.translate_text('hello', target_lang="KO").text
    #             end_time = time.time()
    #             MessageBoxShowInfo(settings_window, "Task Success", f"DeepL Test Finished!\n\nResult : Success\nTime : {(end_time-start_time):.2f} sec")
    #         except:
    #             MessageBoxShowInfo(settings_window, "Error", "DeepL Test Finished!\n\nResult : Failed\n"+get_message("The key is not valid, or the connection is poor."))

    #     def save_trans_api_key():
    #         loaded_settings['setting_key_deepL'] = entry_trans.get()
    #         save_settings()
    #         display_trans_text(entry_trans.get())
    #         MessageBoxShowInfo(settings_window, "Task Success", "DeepL API KEY Saved!")

    #     frame_trans_btn = tk.Frame(dialog_window_trans)
    #     frame_trans_btn.grid(row=2, column=1, pady=2, sticky="e")
    #     confirm_button_trans = tk.Button(frame_trans_btn, text="Test", command=test_trans_api_key)
    #     confirm_button_trans.grid(row=0, column=0, padx=(0,10), pady=2, sticky="e")
    #     confirm_button_trans = tk.Button(frame_trans_btn, text="Confirm", command=save_trans_api_key)
    #     confirm_button_trans.grid(row=0, column=1, pady=2, sticky="e")

    #     def display_trans_text(text):
    #         # showing_text = text
    #         # if len(text) > 10:
    #         #     showing_text = text[:10] + "..."
    #         # translator_label_key_status.config(text=showing_text)
    #         if text:
    #             translator_label_key_status.config(text='Exist')

    
    # translator_options = ["Google", "DeepL"]  
    # if loaded_settings['setting_translator'] not in translator_options:
    #     loaded_settings['setting_translator'] = "Google"
    # translator_dropdown = ttk.Combobox(frame_translator, values=translator_options, state="readonly", width=16)
    # translator_dropdown.set(loaded_settings['setting_translator'])
    # translator_dropdown.grid(row=0, column=1, padx=10, pady=2, sticky="w")
    # translator_dropdown.bind("<<ComboboxSelected>>", update_setting_translator)

    # translator_label_key = tk.Label(frame_translator, text="Key:", width=3)
    # translator_label_key.grid(row=0, column=2, padx=10, pady=2, sticky="e")
    # translator_label_key_status = tk.Label(frame_translator, text="N/A", width=10)
    # translator_label_key_status.grid(row=0, column=3, padx=1, pady=2, sticky="w")
    
    # translator_btn_input_key = tk.Button(frame_translator, text="Input", command=open_trans_api_dialog, width=9)
    # translator_btn_input_key.grid(row=0, column=4, padx=10, pady=2, sticky="we")
    # update_setting_translator()
    
    # 프레임간 여백 추가
    frame_space = tk.Frame(settings_window, height=8)
    frame_space.grid(row=frame_row_idx, column=0, sticky="nsew")
    frame_row_idx+=1
    
    # Frame : Action
    frame_action = tk.Frame(settings_window, padx=10, pady=5, borderwidth=1, relief=tk.SOLID)
    frame_action.grid(row=frame_row_idx, column=0, sticky="nsew")
    frame_row_idx+=1

    # Frame : Action > Size/Effecter > Label, desc
    frame_size = tk.Frame(frame_action)
    frame_size.grid(row=0, column=0, sticky="we")
    
    def update_size(value):
        loaded_settings['setting_size'] = float(size_slider.get())
        save_settings()
        set_size(loaded_settings['setting_size'])
        update_anim()
    size_label = tk.Label(frame_size, text="Size", width=6)
    size_label.grid(row=0, column=0, padx=10, sticky="w")
    size_slider = Scale(frame_size, from_=0.2, to=2, resolution=0.1, orient=tk.HORIZONTAL) #, command=update_size)
    size_slider.set(loaded_settings['setting_size'])  
    size_slider.grid(row=0, column=1, padx=10, sticky="w")
    size_slider.bind("<ButtonRelease-1>", update_size)  # 슬라이더에서 손 땠을때 이벤트 동작하게
    
    def update_size_effecter(value):
        loaded_settings['setting_size_effecter'] = float(size_effecter_slider.get())
        # if size_effecter_slider.get() <= 0:  # show Value False하고 label 일일히 update 칠거면 이걸로
        #     size_effecter_slider.config(label='None')
        save_settings()
    size_effecter_label = tk.Label(frame_size, text="Effecter", width=6)
    size_effecter_label.grid(row=0, column=2, padx=10, sticky="w")
    size_effecter_slider = Scale(frame_size, from_=0, to=1, resolution=0.1, orient=tk.HORIZONTAL) #, command=update_size)
    size_effecter_slider.set(loaded_settings['setting_size_effecter'])  
    size_effecter_slider.grid(row=0, column=3, padx=10, sticky="w")
    size_effecter_slider.bind("<ButtonRelease-1>", update_size_effecter)  # 슬라이더에서 손 땠을때 이벤트 동작하게

    # Frame : Action > Gravity, Mobility, Speed > Label, desc
    frame_physics = tk.Frame(frame_action)
    frame_physics.grid(row=1, column=0, sticky="we")
    
    def update_mobility(value):
        loaded_settings['setting_mobility'] = int(value)
        mobility_slider.config(label=mobility_dic[loaded_settings['setting_mobility']])
        save_settings()
    mobility_label = tk.Label(frame_physics, text="Mobility", width=6)
    mobility_label.grid(row=0, column=0, padx=10, sticky="w")
    mobility_dic = {
        0: "Never",
        1: "Sometimes",
        2: "Often"
    }
    mobility_slider = Scale(frame_physics, from_=min(mobility_dic), to=max(mobility_dic), orient=tk.HORIZONTAL, showvalue=False, command=update_mobility)
    mobility_slider.config(label=mobility_dic[loaded_settings['setting_mobility']])
    mobility_slider.set(loaded_settings['setting_mobility'])  # 기본값 설정
    mobility_slider.grid(row=0, column=1, padx=10, sticky="w")

    def update_moving_speed(value):
        loaded_settings['setting_moving_speed'] = int(value)
        moving_speed_slider.config(label=moving_speed_dic[loaded_settings['setting_moving_speed']])
        save_settings()       
    moving_speed_label = tk.Label(frame_physics, text="Speed", width=6)
    moving_speed_label.grid(row=0, column=2, padx=10, sticky="w")
    moving_speed_dic = {
        0: "Slow",
        1: "Fast"
    }
    moving_speed_slider = Scale(frame_physics, from_=min(moving_speed_dic), to=max(moving_speed_dic), orient=tk.HORIZONTAL, showvalue=False, command=update_moving_speed)
    moving_speed_slider.config(label=moving_speed_dic[loaded_settings['setting_moving_speed']])
    moving_speed_slider.set(loaded_settings['setting_moving_speed'])  # 기본값 설정
    moving_speed_slider.grid(row=0, column=3, padx=10, sticky="w")

    # def toggle_gravity():
    #     loaded_settings['setting_is_gravity'] = not loaded_settings['setting_is_gravity']
    #     gravity_text = "Enable" if loaded_settings['setting_is_gravity'] else "Disable"
    #     gravity_btn.config(text=gravity_text)  
    # gravity_label = tk.Label(frame_physics, text="Gravity", width=6)
    # gravity_label.grid(row=0, column=5, padx=10, sticky="w")
    # gravity_text = "Enable" if loaded_settings['setting_is_gravity'] else "Disable"
    # gravity_btn = tk.Button(frame_physics, text=gravity_text, command=toggle_gravity, width=6)
    # gravity_btn.grid(row=0, column=6, padx=10, sticky="we")

    # Frame : Action > Gravity, Mobility, Speed > Label, desc
    # frame_collision = tk.Frame(frame_action)
    # frame_collision.grid(row=2, column=0, sticky="we")
    # collision_label = tk.Label(frame_collision, text="Collision", width=8, justify='left')
    # collision_label.grid(row=0, column=0, padx=5, sticky="w")
    # def update_collision():
    #     loaded_settings['setting_collision'] = collision_var.get()
    #     save_settings()
    # collision_var = tk.StringVar(value=loaded_settings['setting_collision'])
    # for column_idx, collision in enumerate(["OFF", "Task bar"]):
    #     collision_frame = tk.Frame(frame_collision)
    #     collision_frame.grid(row=0, column=column_idx+1, sticky="we", padx=20)
    #     collision_radio = tk.Radiobutton(collision_frame, text=collision, variable=collision_var, value=collision, command=update_collision)
    #     collision_radio.grid(row=0, column=0, sticky="we")

    # 프레임간 여백 추가
    frame_space = tk.Frame(settings_window, height=8)
    frame_space.grid(row=frame_row_idx, column=0, sticky="nsew")
    frame_row_idx+=1

    # # Frame : Option
    # frame_option = tk.Frame(settings_window, padx=10, borderwidth=1, relief=tk.SOLID)
    # frame_option.grid(row=frame_row_idx, column=0, sticky="nsew")
    # frame_row_idx+=1

    # # Frame : Option > 이것저것 > Label, desc
    # frame_history = tk.Frame(frame_option)
    # frame_history.grid(row=0, column=0, sticky="we", pady=(2,0))
    # frame_history_label = tk.Frame(frame_history, width=8)
    # frame_history_label.grid(row=0, column=0, sticky="we")
    # frame_history_desc = tk.Frame(frame_history)
    # frame_history_desc.grid(row=0, column=1, sticky="we")
    
    
    # def choose_history_folder():
    #     # 문자열 비교로 하위 폴더인지 확인해보기.
    #     def is_subdirectory(path, base):
    #         return os.path.abspath(path).startswith(os.path.abspath(base))

    #     initial_dir = './'
    #     history_folder_path = filedialog.askdirectory(initialdir=initial_dir)
    #     if history_folder_path:
    #         if is_subdirectory(history_folder_path, os.getcwd()):
    #             relative_path = os.path.relpath(history_folder_path).replace("\\", "/")
    #             relative_path = './' + relative_path
    #             loaded_settings['setting_history_folder'] = relative_path
    #             history_path_label.config(text = loaded_settings['setting_history_folder'])
    #             save_settings()
    #         else:
    #             MessageBoxShowInfo(settings_window,"Error", "You can only store them in the main.exe subfolder.")
    # def initialize_history_folder():
    #     loaded_settings['setting_history_folder'] = './history'
    #     history_path_label.config(text = loaded_settings['setting_history_folder'])
    #     save_settings()
    # history_label = tk.Label(frame_history_label, text="History", anchor='w', width=8)
    # history_label.grid(row=0, column=0, sticky="w")
    # history_path_label = tk.Label(frame_history_desc, text=loaded_settings['setting_history_folder'], anchor='w', width=30)
    # history_path_label.grid(row=0, column=0, pady=2, sticky="w")
    # history_button = tk.Button(frame_history_desc, text=get_message('Change'), command=lambda: choose_history_folder(), width=9)
    # history_button.grid(row=0, column=1, padx=10, pady=2, sticky="e")
    # history_initalize_button = tk.Button(frame_history_desc, text=get_message('Initialize'), command=lambda: initialize_history_folder(), width=9)
    # history_initalize_button.grid(row=0, column=2, padx=10, pady=2, sticky="e")

# wav재생
def play_wav(file_path, volume=100):
    global is_program_ended, global_sound
    sound = pygame.mixer.Sound(file_path)
    global_sound = sound
    sound.set_volume(volume/100)
    sound_length = sound.get_length()


    if not loaded_settings:
        sound.play()
    elif loaded_settings['setting_is_volume_on'] and not is_program_ended:
        sound.play()
    return sound_length

# wav file로 재생
def play_wav_file(file_sound, volume=100):
    global is_program_ended
    file_sound.set_volume(volume/100)
    sound_length = file_sound.get_length()

    if not loaded_settings:
        file_sound.play()
    elif loaded_settings['setting_is_volume_on'] and not is_program_ended:
        file_sound.play()
    return sound_length

# 다시 재생
def play_wav_queue_history():
    global wav_event, global_sound_queue_history
    clear_wav_queue()  # 현재 재생 정지 및 queue 비우기
    for sound_file in global_sound_queue_history:  # queue에 다시 넣기
        global_sound_queue.put(sound_file)
    wav_event.set()

def play_wav_queue():
    global wav_event, global_sound_queue, answer_balloon, global_sound_queue_history
    while True:
        wav_event.wait() 
        while not global_sound_queue.empty():
            next_file = global_sound_queue.get()
            play_wav_file(next_file)
            while pygame.mixer.Channel(0).get_busy():
                # time.sleep(0.1)  # Wait until the current music finishes
                pygame.time.wait(100)
        wav_event.clear()
        # if answer_balloon:  # 고정을 위한 수단 체크
        #     answer_balloon.kill_balloon()

# 정지시 등으로 queue 비우기
def clear_wav_queue():
    global global_sound_queue
    while not global_sound_queue.empty():
        global_sound_queue.get()
    try:
        pygame.mixer.Channel(0).stop()
    except:
        pass

# wav file 다수 재생 (stream 반환용.)
def play_wav_queue_add(file_path):
    global wav_thread, wav_event, global_sound_queue
    # 최초실행시 Thread 시작
    if not wav_thread:
        wav_event = threading.Event()
        wav_thread = threading.Thread(target=play_wav_queue, daemon=True)
        wav_thread.start() 
    sound_file = pygame.mixer.Sound(file_path)
    global_sound_queue.put(sound_file)
    global_sound_queue_history.append(sound_file)
    wav_event.set()
    

def stop_wav():
    global global_sound
    if global_sound is not None:
        global_sound.stop()
        global_sound = None  # sound 객체 초기화

def open_ai_settings():
    global loaded_settings
    ai_settings_window = tk.Toplevel(root, padx=5, pady=5)
    ai_settings_window.title("AI Settings")
    ai_settings_window.geometry("400x300")
    
    frame_row_idx = 0
    
    def update_setting(setting_key, value):
        loaded_settings[setting_key] = value
        save_settings()
        
    # Stream settings  # 기본 on
    # frame_stream = tk.Frame(ai_settings_window, padx=10)
    # frame_stream.grid(row=frame_row_idx, column=0, sticky="nsew")
    # stream_label = tk.Label(frame_stream, text="Stream", width=10, anchor='w')
    # stream_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    # stream_var = tk.StringVar(value=loaded_settings['setting_ai_stream'])
    # for col_idx, option in enumerate(["off", "on"]):
    #     stream_radio = tk.Radiobutton(frame_stream, text=option, variable=stream_var, value=option, command=lambda: update_setting('setting_ai_stream', stream_var.get()))
    #     stream_radio.grid(row=0, column=col_idx + 1, padx=5, pady=5, sticky="w")
    # frame_row_idx += 1
    
    # sr settings
    frame_sr = tk.Frame(ai_settings_window, padx=10)
    frame_sr.grid(row=frame_row_idx, column=0, sticky="nsew")
    sr_label = tk.Label(frame_sr, text="S.R.", width=10, anchor='w')
    sr_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    sr_var = tk.StringVar(value=loaded_settings['setting_ai_sr'])
    for col_idx, option in enumerate(["send", "check"]):
        sr_radio = tk.Radiobutton(frame_sr, text=option, variable=sr_var, value=option, command=lambda: update_setting('setting_ai_sr', sr_var.get()))
        sr_radio.grid(row=0, column=col_idx + 1, padx=5, pady=5, sticky="w")
    frame_row_idx += 1
    
    # Web settings
    frame_web = tk.Frame(ai_settings_window, padx=10)
    frame_web.grid(row=frame_row_idx, column=0, sticky="nsew")
    web_label = tk.Label(frame_web, text="Web", width=10, anchor='w')
    web_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    web_var = tk.StringVar(value=loaded_settings['setting_ai_web'])
    for col_idx, option in enumerate(["off", "on", "force"]):
        web_radio = tk.Radiobutton(frame_web, text=option, variable=web_var, value=option, command=lambda: update_setting('setting_ai_web', web_var.get()))
        web_radio.grid(row=0, column=col_idx + 1, padx=5, pady=5, sticky="w")
    frame_row_idx += 1

    # # Story settings (Advanced RAG때 돌아오겠음)
    # frame_story = tk.Frame(ai_settings_window, padx=10)
    # frame_story.grid(row=frame_row_idx, column=0, sticky="nsew")
    # story_label = tk.Label(frame_story, text="Story", width=10, anchor='w')
    # story_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    # story_var = tk.StringVar(value=loaded_settings['setting_ai_story'])
    # for col_idx, option in enumerate(["off", "on", "force"]):
    #     story_radio = tk.Radiobutton(frame_story, text=option, variable=story_var, value=option, command=lambda: update_setting('setting_ai_story', story_var.get()))
    #     story_radio.grid(row=0, column=col_idx + 1, padx=5, pady=5, sticky="w")
    # frame_row_idx += 1

    # Memory settings
    frame_memory = tk.Frame(ai_settings_window, padx=10)
    frame_memory.grid(row=frame_row_idx, column=0, sticky="nsew")
    memory_label = tk.Label(frame_memory, text="Memory", width=10, anchor='w')
    memory_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    memory_var = tk.StringVar(value=loaded_settings['setting_ai_memory'])
    for col_idx, option in enumerate(["off", "on", "force"]):
        memory_radio = tk.Radiobutton(frame_memory, text=option, variable=memory_var, value=option, command=lambda: update_setting('setting_ai_memory', memory_var.get()))
        memory_radio.grid(row=0, column=col_idx + 1, padx=5, pady=5, sticky="w")
        memory_radio.configure(state = tk.DISABLED)  # Todo
    frame_row_idx += 1

    # # Image settings
    # frame_image = tk.Frame(ai_settings_window, padx=10)
    # frame_image.grid(row=frame_row_idx, column=0, sticky="nsew")
    # image_label = tk.Label(frame_image, text="Image", width=10, anchor='w')
    # image_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    # image_var = tk.StringVar(value=loaded_settings['setting_ai_image'])
    # for col_idx, option in enumerate(["off", "on", "force"]):
    #     image_radio = tk.Radiobutton(frame_image, text=option, variable=image_var, value=option, command=lambda: update_setting('setting_ai_image', image_var.get()))
    #     image_radio.grid(row=0, column=col_idx + 1, padx=5, pady=5, sticky="w")
    # frame_row_idx += 1


    def erase_history():
        # Implement the logic to erase history
        print("History erased")
        # For example:
        # loaded_settings['history'] = ""
        # save_settings()
        
    # History settings
    frame_history = tk.Frame(ai_settings_window, padx=10)
    frame_history.grid(row=frame_row_idx, column=0, sticky="nsew")
    history_label = tk.Label(frame_history, text="History", width=10, anchor='w')
    history_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
    erase_button = tk.Button(frame_history, text="Erase", command=erase_history)
    erase_button.grid(row=0, column=1, padx=5, pady=5, sticky="w")

def audio_callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    audio_queue.put(indata.copy())

def check_speech_recognition_status():
    global recognizer
    try:
        with sr.Microphone() as mic:
            recognizer.adjust_for_ambient_noise(mic)
            return True
    except:
        return False

def activate_speech_recognition():
    global is_talk_thread_activated, talk_thread
    if loaded_settings['setting_talk_mode'] not in ["Auto", "Manual"]:
        MessageBoxShowInfo(root, 'Error', 'Set up Talk in [Settings].')
        return
    if is_talk_thread_activated:
        MessageBoxShowInfo(root, 'Error', 'Speech recognition is already enabled.')
        return
    # if not check_speech_recognition_status():
    #     MessageBoxShowInfo(root, 'Error', 'The microphone is not detected.')
    #     return            
    is_talk_thread_activated = True
    talk_thread = threading.Thread(target=talk_listener)
    talk_thread.start()
    time.sleep(0.2)  # thread 조금 가동
    if is_talk_thread_activated:
        MessageBoxShowInfo(root, 'Task Success', "Speech recognition is enabled.")
        try:
            menu.entryconfig("Activate Speech Recognition", label="Deactivate Speech Recognition", command=lambda: deactivate_speech_recognition())
        except:
            pass
    else:
        MessageBoxShowInfo(root, 'Error', "Speech recognition is not enabled.")
        
def deactivate_speech_recognition():
    global is_talk_thread_activated, talk_thread
    if is_talk_thread_activated:
        MessageBoxShowInfo(root, 'Task Success', "Speech recognition is disabled.")  # 기존에 켜져있어야 메시지
    is_talk_thread_activated = False
    if talk_thread and talk_thread.is_alive():
        talk_thread.join()
    try:
        menu.entryconfig("Deactivate Speech Recognition", label="Activate Speech Recognition", command=lambda: activate_speech_recognition())
    except:
        pass

# 이미지 인식 활성화
def active_focus():    
    global is_focus, screenshotApp, screenshotApp_thread
    result = screenshotApp.toggle_continuous_save()
    if result == 'No':
        # 스크린샷 모드 될때까지 대기 (최대 1200초)
        screenshotApp_thread = threading.Thread(target=change_to_focus_mode)
        screenshotApp_thread.start()    
    
def change_to_focus_mode():
    global is_focus, screenshotApp
    def find_menu_index(menu_name, menu):
        for index in range(menu.index("end") + 1):
            # print('menutype', index, menu.type(index))
            if menu.type(index) == "command":
                # print('menu label', menu.entrycget(index, "label"))
                label = menu.entrycget(index, "label")
                if label == menu_name:
                    return index
        return -1
    
    while True:
        if screenshotApp.screenshot_rect:
            screenshotApp.active_continuous_save_thread()
            break
        else:
            time.sleep(1)
    
    # 메뉴 토글
    activate_index = find_menu_index("Activate Focus", menu)
    menu.entryconfig("Activate Focus", label="Deactivate Focus", command=lambda: deactive_focus())
    # 메뉴 추가
    menu.insert_command(activate_index+1, label="Show Focus Area", command=lambda: screenshotApp.show_screenshot_rect())
    is_focus = True
    
    root.after(0, show_answer_balloon_simple, "I'll focus on the focus area, sensei!")

def deactive_focus():
    def find_menu(menu_name):
        for index in range(menu.index("end") + 1):
            if menu.type(index) == "command":
                label = menu.entrycget(index, "label")
                if label == menu_name:
                    return True
        return False
    
    global is_focus, screenshotApp
    screenshotApp.toggle_continuous_save()
    
    # 메뉴 토글
    menu.entryconfig("Deactivate Focus", label="Activate Focus", command=lambda: active_focus())
    # 추가메뉴 삭제
    if find_menu("Show Focus Area"):
        menu.delete("Show Focus Area")

    is_focus = False
    
    MessageBoxShowInfo(root, 'Info', "Focus mode Deactivated")

# 티키타카
def active_tikitaka():
    global faster_whisper_listener, tikitaka_status_thread, tikitaka_thread, llama_server
    from llama_server import LlamaServer    
    if llama_server:
        ask_question_box = MessageBoxAskQuestion(root, "Confirm", "It's already running. Do you want to restart it?")
        root.wait_window(ask_question_box)
        if ask_question_box.result: 
            try:
                llama_server.stop()
                llama_server = None
            except:
                MessageBoxShowInfo(root, 'Error', "Restart failed, please try again later.")
                return
    if loaded_settings['setting_program_type'] == 'CPU':
        llama_server = LlamaServer(use_gpu=False)
    else:
        ai_singleton.release()  # 기존 GPU release
        llama_server = LlamaServer(use_gpu=True)
    llama_server.start()
    
    def get_tikitaka_status_listener():
        global faster_whisper_listener, is_chatting, is_program_ended
        while not is_program_ended:
            try:
                if not faster_whisper_listener:
                    time.sleep(1)
                status = faster_whisper_listener.status
                if status:
                    is_chatting = True  # 채팅관련 시작
                    root.after(0, set_status, status)
                    faster_whisper_listener.status = None
                else:
                    time.sleep(0.25)
            except:
                time.sleep(2)

    def start_tikitaka_listener():
        global faster_whisper_listener
        from faster_whisper_listener import FasterWhisperListener
        lang = 'en'
        if loaded_settings['setting_chat_language'] == '日本語':
            lang = 'ja'
        elif loaded_settings['setting_chat_language'] == '한국어':
            lang = 'ko'
        faster_whisper_listener = FasterWhisperListener(lang=lang, root=root, program_type=loaded_settings['setting_program_type'])
        root.after(0, show_answer_balloon_simple, "I'm ready to talk, sensei.")
        faster_whisper_listener.completion_url = llama_server.completion_url
        faster_whisper_listener.start_listen_event_loop() 
    
    tikitaka_thread = threading.Thread(target=start_tikitaka_listener)
    tikitaka_thread.start()
    
    tikitaka_status_thread = threading.Thread(target=get_tikitaka_status_listener)
    tikitaka_status_thread.start()
    
def show_answer_balloon_simple(text):
    AnswerBalloonSimple(text)

def on_click(event=None):
    global is_dragging, is_chatting, chat_window
    
    if not is_dragging and not is_chatting:
        is_chatting = True  # 채팅관련 시작
        set_status('think')

        global chat_window
        chat_window = ChatBalloon()

def on_click_async(event=None):
    global chat_window, is_chatting, answer_balloon
    if not is_chatting and answer_balloon:
        answer_balloon.kill_balloon()
    
    if chat_window != None:
        chat_window.destroy()
        is_chatting = False
        chat_window = None
        set_status('idle')
    else:
        root.after(100, on_click, event)  # 0.1초후 on_click 호출
        
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
    set_status('smile')
    menu.post(event.x_root, event.y_root)
    check_menu_visibility()

######################################################################

def make_loading_option_screen():
    # global is_loading, loading_option_root
    # is_loading = True

    loading_option_root = tk.Tk()
    loading_option_screen = LoadingOptionScreen(loading_option_root)
    loading_option_root.mainloop()  # Tkinter의 mainloop 실행

def make_loading_screen():
    global is_loading, loading_screen_text, loading_root
    if not DEV_MODE:
        is_loading = True
        loading_screen_text = "Loading Start..."

        loading_root = tk.Tk()
        loading_screen = LoadingScreen(loading_root)
        loading_root.mainloop()  # Tkinter의 mainloop 실행

        loading_screen.anim_thread.join()
        loading_screen.text_thread.join()

# CPU 버전만 해당 방식으로 로드
def load_models():
    global loading_screen_text, recognizer, loaded_settings, is_use_cuda
    gc.collect()
    
    if loaded_settings['setting_load_option'] == 'Normal':
        load_models_cnt = '5'
        i = 1
        loading_screen_text = "Loading ai_conversation... ("+str(i)+"/"+load_models_cnt+")"
        ai_conversation.load_model(is_use_cuda)  
        i += 1
        loading_screen_text = "Loading ai_web... ("+str(i)+"/"+load_models_cnt+")"
        ai_web_search.load_model(is_use_cuda)     
        # i += 1 
        # loading_screen_text = "Loading ai_story... ("+str(i)+"/"+load_models_cnt+")"
        # ai_rag_story.load_model(is_use_cuda)   
        i += 1
        ai_intent_reader.load_model(is_use_cuda)
        loading_screen_text = "Loading ai_sound_recognizer... ("+str(i)+"/"+load_models_cnt+")"
        recognizer = sr.Recognizer() 
        try:
            dummy_audio = AudioData(b'\x01\x01\x01\x01\x01\x01\x01\x01',44100,2)
            recognizer.recognize_fasterwhisper(dummy_audio, language="en", model="base") 
        except:
            pass
        i+=1
        loading_screen_text = "Loading ai_voices... ("+load_models_cnt+"/"+load_models_cnt+")"
        synthesize_char('korean', '안녕하세요.', use_cuda=is_use_cuda, type='single', sid=0)
    elif loaded_settings['setting_load_option'] == 'Custom':
        setting_load_option_customlist = loaded_settings['setting_load_option_customlist']  # conversation, web, story, translation, S.memory, L.memory, image.R, sound.R
        print('setting_load_option_customlist', setting_load_option_customlist)
        load_models_cnt = str(len(setting_load_option_customlist) + 1)
        i = 1
        if "conversation" in setting_load_option_customlist:
            loading_screen_text = "Loading ai_conversation... ("+str(i)+"/"+load_models_cnt+")"
            ai_conversation.load_model(is_use_cuda)
            i+=1
        intent_flag = False
        if "web" in setting_load_option_customlist:
            loading_screen_text = "Loading ai_web... ("+str(i)+"/"+load_models_cnt+")"
            ai_web_search.load_model(is_use_cuda)
            intent_flag = True
            i+=1
        if "story" in setting_load_option_customlist:
            loading_screen_text = "Loading ai_story... ("+str(i)+"/"+load_models_cnt+")"
            # ai_rag_story.load_model(is_use_cuda)
            intent_flag = True
            i+=1
        if intent_flag:
            ai_intent_reader.load_model(is_use_cuda)
        if "translation" in setting_load_option_customlist:
            loading_screen_text = "Loading ai_translation... ("+str(i)+"/"+load_models_cnt+")"
            # ai_translation_jp.load_model(is_use_cuda)
            # ai_translation_ko.load_model(is_use_cuda)
            # ai_translation_en.load_model(is_use_cuda)
            i+=1
        if "S.memory" in setting_load_option_customlist:
            i+=1
            pass
        if "L.memory" in setting_load_option_customlist:
            i+=1
            pass
        if "image.R" in setting_load_option_customlist:
            i+=1
            pass  # 로딩시점에 시작
        if "sound.R" in setting_load_option_customlist:
            loading_screen_text = "Loading ai_sound_recognizer... ("+str(i)+"/"+load_models_cnt+")"
            recognizer = sr.Recognizer() 
            try:
                dummy_audio = AudioData(b'\x01\x01\x01\x01\x01\x01\x01\x01',44100,2)
                recognizer.recognize_fasterwhisper(dummy_audio, language="en", model="base") 
            except:
                pass
            i+=1
        loading_screen_text = "Loading ai_voices... ("+load_models_cnt+"/"+load_models_cnt+")"
        synthesize_char('korean', '안녕하세요', use_cuda=is_use_cuda, type='single', sid=0)
    else:  # Fast
        loading_screen_text = "Loading ai_conversation..." + " (1/2)"
        ai_conversation.load_model(is_use_cuda)
        loading_screen_text = "Loading ai_voices..." + " (2/2)"
        synthesize_char('korean', '안녕하세요', use_cuda=is_use_cuda, type='single', sid=0)

def clean_models():
    global llama_server
    if llama_server:
        try:
            llama_server.stop()  # 켜지는 중일 경우 대비
        except:
            pass
    ai_conversation.clean_model()
    MessageBoxShowInfo(root, 'Info', 'Cleaned Preloaded Models')
    ai_singleton.release()
    

def json_decoder(input_string):
    try:
        # 문자열을 JSON으로 파싱
        data = json.loads(input_string)
        
        # JSON 객체에 'say' 키가 있는지 확인
        if 'say' in data:
            result = data['say']
            result = result.strip()
            if not result:
                return input_string
            return result
        else:
            return input_string
    except:
        # JSON 파싱에 실패한 경우 원래 문자열 반환
        return input_string

# regenerate
def regenerate(question):
    # 답변 음성 queue 초기화
    global global_sound_queue_history, is_use_cuda
    global_sound_queue_history = list()  # 대답 queue 초기화
    
    # 그전 문답 중 답변만 삭제
    memory.delete_recent_dialogue()  # AI 대답'만' 지우고 regenerate
    
    global latest_ai_module
    if latest_ai_module == 'conversation_web':  # 웹 검색
        conversation_web(question)
    elif latest_ai_module == 'ai_img':  # 이미지 검색
        if is_focus or os.path.exists('./image/external.png'):
            latest_ai_module = 'ai_img'  # for regenerate flag
            if is_focus:
                file_path = './image/screenshot.png'   
            else:
                file_path = './image/external.png'
            last_reply_len = 0
            answer = dict()
            answer['answer_en'] = ''                 
            answer['answer_ko'] = ''
            answer['answer_jp'] = ''
            for j, reply_list in enumerate(ai_conversation.process_stream(question, 'm9dev', 'Arona', True, False, info_img=file_path)):
                if last_reply_len < len(reply_list):
                    # 새로운 문장  
                    last_reply_len = len(reply_list)    
                    if len(reply_list) == 1:  # 최초 문장      
                        reply_new = reply_list[-1]
                        result_ko = translator_google.translate(reply_new, dest='ko').text
                        result_ko = change_to_ko(result_ko)
                        result_jp = translator_google.translate(reply_new, dest='ja').text    
                        result_jp = change_to_jp(result_jp)
                        answer['setting_lang'] = 'en'
                        if loaded_settings['setting_chat_language'] == '日本語':
                            answer['setting_lang'] = 'jp'
                        elif loaded_settings['setting_chat_language'] == '한국어':
                            answer['setting_lang'] = 'ko'
                        answer['answer_en'] = reply_new                 
                        answer['answer_ko'] = result_ko
                        answer['answer_jp'] = result_jp
                        sound_length = 999
                        # 음성합성 추가
                        audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_ko, use_cuda=is_use_cuda, type='single', sid=0)
                        play_wav_queue_add(audio)
                        # show_answer_balloon(sound_length, answer)   
                        # root.after(0, show_answer_balloon, 999, answer)       
                        # 말풍선 추가      
                        answer_balloon = AnswerBalloon(answer, question)
                        # 상태 변경
                        set_status('talk')   
                    else:          
                        reply_new = reply_list[-1]
                        result_ko = translator_google.translate(reply_new, dest='ko').text
                        result_ko = change_to_ko(result_ko)
                        result_jp = translator_google.translate(reply_new, dest='ja').text
                        result_jp = change_to_jp(result_jp)
                        # 음성합성 추가
                        audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_ko, use_cuda=is_use_cuda, type='single', sid=0)
                        play_wav_queue_add(audio)
                        
                        answer['answer_en'] = answer['answer_en'] + ' ' + reply_new.lstrip()
                        answer['answer_ko'] = answer['answer_ko'] + ' ' + result_ko.lstrip()
                        answer['answer_jp'] = answer['answer_jp'] + '' + result_jp.lstrip()
                            
                        # 말풍선 갱신                                                           
                        answer_balloon.modify_text_from_answer(answer)
                    # tkinter 창 업데이트
                    answer_balloon.update_idletasks()
                    answer_balloon.update()
            answer_text = answer['answer_en']
            if loaded_settings['setting_chat_language'] == '日本語':
                answer_text = answer['answer_jp']
            elif loaded_settings['setting_chat_language'] == '한국어':
                answer_text = answer['answer_ko']
            memory.save_conversation_memory('character', answer_text, answer['answer_en'])
            
            return None, None, None  # 이후 재생하지 말 것 이라는 소리           
    else:  # 기본값('conversation')    
        # regenerate
        last_reply_len = 0
        answer = dict()
        answer['answer_en'] = ''                 
        answer['answer_ko'] = ''
        answer['answer_jp'] = ''
        for j, reply_list in enumerate(ai_conversation.process_stream(question, 'm9dev', 'Arona', True, True)):
            if last_reply_len < len(reply_list):
                # 새로운 문장  
                last_reply_len = len(reply_list)    
                if len(reply_list) == 1:  # 최초 문장      
                    reply_new = reply_list[-1]
                    result_ko = translator_google.translate(reply_new, dest='ko').text
                    result_ko = change_to_ko(result_ko)
                    result_jp = translator_google.translate(reply_new, dest='ja').text    
                    result_jp = change_to_jp(result_jp)
                    answer['setting_lang'] = 'en'
                    if loaded_settings['setting_chat_language'] == '日本語':
                        answer['setting_lang'] = 'jp'
                    elif loaded_settings['setting_chat_language'] == '한국어':
                        answer['setting_lang'] = 'ko'
                    answer['answer_en'] = reply_new                 
                    answer['answer_ko'] = result_ko
                    answer['answer_jp'] = result_jp
                    sound_length = 999
                    # 음성합성 추가
                    audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_ko, use_cuda=is_use_cuda, type='single', sid=0)
                    play_wav_queue_add(audio)
                    # show_answer_balloon(sound_length, answer)   
                    # root.after(0, show_answer_balloon, 999, answer)       
                    # 말풍선 추가      
                    answer_balloon = AnswerBalloon(answer, question)
                    # 상태 변경
                    set_status('talk')   
                else:          
                    reply_new = reply_list[-1]
                    result_ko = translator_google.translate(reply_new, dest='ko').text
                    result_ko = change_to_ko(result_ko)
                    result_jp = translator_google.translate(reply_new, dest='ja').text
                    result_jp = change_to_jp(result_jp)
                    # 음성합성 추가
                    audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_ko, use_cuda=is_use_cuda, type='single', sid=0)
                    play_wav_queue_add(audio)
                    
                    answer['answer_en'] = answer['answer_en'] + ' ' + reply_new.lstrip()
                    answer['answer_ko'] = answer['answer_ko'] + ' ' + result_ko.lstrip()
                    answer['answer_jp'] = answer['answer_jp'] + '' + result_jp.lstrip()
                        
                    # 말풍선 갱신                                                           
                    answer_balloon.modify_text_from_answer(answer)
                # tkinter 창 업데이트
                answer_balloon.update_idletasks()
                answer_balloon.update()
        answer_text = answer['answer_en']
        if loaded_settings['setting_chat_language'] == '日本語':
            answer_text = answer['answer_jp']
        elif loaded_settings['setting_chat_language'] == '한국어':
            answer_text = answer['answer_ko']
        memory.save_conversation_memory('character', answer_text, answer['answer_en'])
        
        # 여기서 처리
        # global is_chatting  # 음성인식때문에 관두는게 좋긴 함
        # is_chatting = False
        # 정지버튼 제거
        if answer_balloon and answer_balloon.btns:
            stop_btn = answer_balloon.btns.pop(0)
            stop_btn.destroy()
            answer_balloon.reloc_btns()
            answer_balloon.update_idletasks()
            answer_balloon.update()

# 의도 되물은 후에 대답
def conversation_web(trans_question):
    global latest_ai_module, global_sound_queue_history
    latest_ai_module = 'conversation_web'  # regenerate 용
    
    global_sound_queue_history = list()  # 대답 queue 초기화
    
    kill_status_balloon()
            
    last_reply_len = 0
    answer = dict()
    answer['answer_en'] = ''                 
    answer['answer_ko'] = ''
    answer['answer_jp'] = ''
    for j, reply_list in enumerate(ai_web_search.process(trans_question)):
        if last_reply_len < len(reply_list):
            # 새로운 문장  
            last_reply_len = len(reply_list)    
            if len(reply_list) == 1:  # 최초 문장      
                reply_new = reply_list[-1]
                result_ko = translator_google.translate(reply_new, dest='ko').text
                result_ko = change_to_ko(result_ko)
                result_jp = translator_google.translate(reply_new, dest='ja').text    
                result_jp = change_to_jp(result_jp)
                answer['setting_lang'] = 'en'
                if loaded_settings['setting_chat_language'] == '日本語':
                    answer['setting_lang'] = 'jp'
                elif loaded_settings['setting_chat_language'] == '한국어':
                    answer['setting_lang'] = 'ko'
                answer['answer_en'] = reply_new                 
                answer['answer_ko'] = result_ko
                answer['answer_jp'] = result_jp
                sound_length = 999
                # 음성합성 추가
                audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_ko, use_cuda=is_use_cuda, type='single', sid=0)
                play_wav_queue_add(audio)
                # show_answer_balloon(sound_length, answer)   
                # root.after(0, show_answer_balloon, 999, answer)       
                # 말풍선 추가      
                answer_balloon = AnswerBalloon(answer, question)
                # 상태 변경
                set_status('talk')   
            else:          
                reply_new = reply_list[-1]
                result_ko = translator_google.translate(reply_new, dest='ko').text
                result_ko = change_to_ko(result_ko)
                result_jp = translator_google.translate(reply_new, dest='ja').text
                result_jp = change_to_jp(result_jp)
                # 음성합성 추가
                audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_ko, use_cuda=is_use_cuda, type='single', sid=0)
                play_wav_queue_add(audio)
                
                answer['answer_en'] = answer['answer_en'] + ' ' + reply_new.lstrip()
                answer['answer_ko'] = answer['answer_ko'] + ' ' + result_ko.lstrip()
                answer['answer_jp'] = answer['answer_jp'] + '' + result_jp.lstrip()
                    
                # 말풍선 갱신                                                           
                answer_balloon.modify_text_from_answer(answer)
            # tkinter 창 업데이트
            answer_balloon.update_idletasks()
            answer_balloon.update()
    
    return answer['answer_en'], answer['answer_jp'], answer['answer_ko']


def conversation(user_input):
    global query_ai_translation_question, query_ai_intent, query_ai_rag_story, query_ai_conversation, query_ai_translation_jp, query_ai_translation_ko, query_ai_translation_en
    global translator_google
    global is_focus
    global answer_balloon
    global global_sound_queue_history
    global is_use_cuda
    
    global latest_ai_module
    latest_ai_module = 'conversation'  # regenerate 용
    
    # 초기화
    state.set_is_stop_requested(False)
    stream_idx = 0  # stream 반환시 현재 list의 몇번째까지 번역/queue에 input 되었는지를 기재
    global_sound_queue_history = list()
    
    player = 'm9dev'
    character = 'arona'
    
    log = dict()
      
    trans_question = ''
    if True: # 우선 구글 번역으로 통일 (translate_google 참조)
        trans_question = translator_google.translate(user_input, dest='en').text  
    else:
        trans_question = ai_translation_question.process(user_input)
        trans_question = trans_question.split('translation: ')[1].split('\n')[0]
        
    # Focus mode / external.png가 있음 : 화면 인식 모드
    if is_focus or os.path.exists('./image/external.png'):
        latest_ai_module = 'ai_img'  # for regenerate flag
        if is_focus:
            file_path = './image/screenshot.png'   
        else:
            file_path = './image/external.png'
        last_reply_len = 0
        answer = dict()
        answer['answer_en'] = ''                 
        answer['answer_ko'] = ''
        answer['answer_jp'] = ''
        for j, reply_list in enumerate(ai_conversation.process_stream(trans_question, 'm9dev', 'Arona', True, False, info_img=file_path)):
            if last_reply_len < len(reply_list):
                # 새로운 문장  
                last_reply_len = len(reply_list)    
                if len(reply_list) == 1:  # 최초 문장      
                    reply_new = reply_list[-1]
                    result_ko = translator_google.translate(reply_new, dest='ko').text
                    result_ko = change_to_ko(result_ko)
                    result_jp = translator_google.translate(reply_new, dest='ja').text    
                    result_jp = change_to_jp(result_jp)
                    answer['setting_lang'] = 'en'
                    if loaded_settings['setting_chat_language'] == '日本語':
                        answer['setting_lang'] = 'jp'
                    elif loaded_settings['setting_chat_language'] == '한국어':
                        answer['setting_lang'] = 'ko'
                    answer['answer_en'] = reply_new                 
                    answer['answer_ko'] = result_ko
                    answer['answer_jp'] = result_jp
                    sound_length = 999
                    # 음성합성 추가
                    audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_ko, use_cuda=is_use_cuda, type='single', sid=0)
                    play_wav_queue_add(audio)
                    # show_answer_balloon(sound_length, answer)   
                    # root.after(0, show_answer_balloon, 999, answer)       
                    # 말풍선 추가      
                    answer_balloon = AnswerBalloon(answer, trans_question)
                    # 상태 변경
                    set_status('talk')   
                else:          
                    reply_new = reply_list[-1]
                    result_ko = translator_google.translate(reply_new, dest='ko').text
                    result_ko = change_to_ko(result_ko)
                    result_jp = translator_google.translate(reply_new, dest='ja').text
                    result_jp = change_to_jp(result_jp)
                    # 음성합성 추가
                    audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_ko, use_cuda=is_use_cuda, type='single', sid=0)
                    play_wav_queue_add(audio)
                    
                    answer['answer_en'] = answer['answer_en'] + ' ' + reply_new.lstrip()
                    answer['answer_ko'] = answer['answer_ko'] + ' ' + result_ko.lstrip()
                    answer['answer_jp'] = answer['answer_jp'] + '' + result_jp.lstrip()
                        
                    # 말풍선 갱신                                                           
                    answer_balloon.modify_text_from_answer(answer)
                # tkinter 창 업데이트
                answer_balloon.update_idletasks()
                answer_balloon.update()
        answer_text = answer['answer_en']
        if loaded_settings['setting_chat_language'] == '日本語':
            answer_text = answer['answer_jp']
        elif loaded_settings['setting_chat_language'] == '한국어':
            answer_text = answer['answer_ko']
        memory.save_conversation_memory('player', user_input, message_trans = trans_question)
        memory.save_conversation_memory('character', answer_text, answer['answer_en'])
        
        return None, None, None  # 이후 재생하지 말 것 이라는 소리
    
    
    # $$$ setting 상황 보고 intent 프롬프트 조합해서 보내기
    intent_response = ''
    if loaded_settings["setting_ai_web"] == "on" or loaded_settings["setting_ai_story"] == "on" or loaded_settings["setting_ai_memory"] == "on" :
        intent_response = ai_intent_reader.process(trans_question)
        print('intent_response', intent_response)
        
    response_web_result = None
    if "web: True" in intent_response:
        # 의도 되묻기
        global ask_balloon
        text = 'can I do a web search? sensei? Instead, a web search takes time.'
        if loaded_settings['setting_chat_language'] == '日本語':
            text = 'ウェブ検索してもいいですか？先生？ 検索には時間がかかりますよ。'
        elif loaded_settings['setting_chat_language'] == '한국어':
            text = '웹 검색을 해도 될까요? 선생님? 대신 웹 검색에는 시간이 걸려요.'
        # 음성합성 추가
        audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', '웹 검색을 해도 될까요? 선생님? 대신 웹 검색에는 시간이 걸려요.', use_cuda=is_use_cuda, type='single', sid=0)
        play_wav_queue_add(audio)
        # 풍선보이기
        ask_balloon = AskBalloon(text, trans_question)
        return None, None, None
        
    elif loaded_settings["setting_ai_web"] == "force":  # 강제웹검색
        conversation_web(trans_question)
        return None, None, None
    else:
        log['web'] = 'False'
        
    # response_rag_result = None  
    # if "rag: True" in intent_response or loaded_settings["setting_ai_story"] == "force":
    #     response_rag_result, rag_sources = ai_rag_story.process(user_input)
    #     log['rag'] = 'True'
    #     log['response_rag_result'] = response_rag_result  # Log에는 반환값 그대로
    #     log['rag_sources'] = rag_sources
    #     # log['rag_sources'] = rag_sources[0]['metadata']['source'] + "/" + rag_sources[1]['metadata']['source']
        
    #     if "[No]" in response_rag_result.split('\n')[0]:  # 첫줄에 [NO]가 있으면 안쓰씀
    #         log['rag'] = 'Denied'
    #         print('response_rag_result denied', response_rag_result)
    #         response_rag_result = None
    #     else:
    #         response_rag_result = response_rag_result.split('\n')[0].split('[No]')[0]  # 정제
    # else:
    #     log['rag'] = 'False'

    # Stream 일반 답변 (표준)
    last_reply_len = 0
    answer = dict()
    answer['answer_en'] = ''                 
    answer['answer_ko'] = ''
    answer['answer_jp'] = ''
    for j, reply_list in enumerate(ai_conversation.process_stream(trans_question, 'm9dev', 'Arona', True, False)):
        # print('reply_list', reply_list)
        if last_reply_len < len(reply_list):
            # 새로운 문장  
            last_reply_len = len(reply_list)    
            if len(reply_list) == 1:  # 최초 문장      
                reply_new = reply_list[-1]
                result_ko = translator_google.translate(reply_new, dest='ko').text
                result_ko = change_to_ko(result_ko)
                result_jp = translator_google.translate(reply_new, dest='ja').text    
                result_jp = change_to_jp(result_jp)
                answer['setting_lang'] = 'en'
                if loaded_settings['setting_chat_language'] == '日本語':
                    answer['setting_lang'] = 'jp'
                elif loaded_settings['setting_chat_language'] == '한국어':
                    answer['setting_lang'] = 'ko'
                answer['answer_en'] = reply_new                 
                answer['answer_ko'] = result_ko
                answer['answer_jp'] = result_jp
                sound_length = 999
                # 음성합성 추가
                audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_ko, use_cuda=is_use_cuda, type='single', sid=0)
                play_wav_queue_add(audio)
                # show_answer_balloon(sound_length, answer)   
                # root.after(0, show_answer_balloon, 999, answer)       
                # 말풍선 추가      
                answer_balloon = AnswerBalloon(answer, trans_question)
                # 상태 변경
                set_status('talk')   
            else:          
                reply_new = reply_list[-1]
                result_ko = translator_google.translate(reply_new, dest='ko').text
                result_ko = change_to_ko(result_ko)
                result_jp = translator_google.translate(reply_new, dest='ja').text
                result_jp = change_to_jp(result_jp)
                # 음성합성 추가
                audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_ko, use_cuda=is_use_cuda, type='single', sid=0)
                play_wav_queue_add(audio)
                
                answer['answer_en'] = answer['answer_en'] + ' ' + reply_new.lstrip()
                answer['answer_ko'] = answer['answer_ko'] + ' ' + result_ko.lstrip()
                answer['answer_jp'] = answer['answer_jp'] + '' + result_jp.lstrip()
                    
                # 말풍선 갱신                                                           
                answer_balloon.modify_text_from_answer(answer)
            # tkinter 창 업데이트
            answer_balloon.update_idletasks()
            answer_balloon.update()
    answer_text = answer['answer_en']
    if loaded_settings['setting_chat_language'] == '日本語':
        answer_text = answer['answer_jp']
    elif loaded_settings['setting_chat_language'] == '한국어':
        answer_text = answer['answer_ko']
    memory.save_conversation_memory('player', user_input, message_trans = trans_question)
    memory.save_conversation_memory('character', answer_text, answer['answer_en'])
    
    # 여기서 처리
    # global is_chatting  # 음성인식때문에 관두는게 좋긴 함
    # is_chatting = False
    
    # 정지버튼 제거
    if answer_balloon and answer_balloon.btns:
        stop_btn = answer_balloon.btns.pop(0)
        stop_btn.destroy()
        answer_balloon.reloc_btns()
        answer_balloon.update_idletasks()
        answer_balloon.update()
    
    return None, None, None     


def active_trigger(trigger='idle'):
    import ai_trigger
    answer = dict()
    answer['answer_en'] = ''                 
    answer['answer_ko'] = ''
    answer['answer_jp'] = ''
    last_reply_len = 0
    for j, reply_list in enumerate(ai_trigger.process_stream('idle', 'm9dev', 'Arona', True, True)):
        if last_reply_len < len(reply_list):
            # 새로운 문장  
            last_reply_len = len(reply_list)    
            if len(reply_list) == 1:  # 최초 문장      
                reply_new = reply_list[-1]
                result_ko = translator_google.translate(reply_new, dest='ko').text
                result_ko = change_to_ko(result_ko)
                result_jp = translator_google.translate(reply_new, dest='ja').text    
                result_jp = change_to_jp(result_jp)
                answer['setting_lang'] = 'en'
                if loaded_settings['setting_chat_language'] == '日本語':
                    answer['setting_lang'] = 'jp'
                elif loaded_settings['setting_chat_language'] == '한국어':
                    answer['setting_lang'] = 'ko'
                answer['answer_en'] = reply_new                 
                answer['answer_ko'] = result_ko
                answer['answer_jp'] = result_jp
                sound_length = 999
                # 음성합성 추가
                audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_ko, use_cuda=is_use_cuda, type='single', sid=0)
                play_wav_queue_add(audio)
                # show_answer_balloon(sound_length, answer)   
                # root.after(0, show_answer_balloon, 999, answer)       
                # 말풍선 추가      
                answer_balloon = AnswerBalloon(answer, question)
                # 상태 변경
                set_status('talk')   
            else:          
                reply_new = reply_list[-1]
                result_ko = translator_google.translate(reply_new, dest='ko').text
                result_ko = change_to_ko(result_ko)
                result_jp = translator_google.translate(reply_new, dest='ja').text
                result_jp = change_to_jp(result_jp)
                # 음성합성 추가
                audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_ko, use_cuda=is_use_cuda, type='single', sid=0)
                play_wav_queue_add(audio)
                
                answer['answer_en'] = answer['answer_en'] + ' ' + reply_new.lstrip()
                answer['answer_ko'] = answer['answer_ko'] + ' ' + result_ko.lstrip()
                answer['answer_jp'] = answer['answer_jp'] + '' + result_jp.lstrip()
                    
                # 말풍선 갱신                                                           
                answer_balloon.modify_text_from_answer(answer)
            # tkinter 창 업데이트
            answer_balloon.update_idletasks()
            answer_balloon.update()
    answer_text = answer['answer_en']
    if loaded_settings['setting_chat_language'] == '日本語':
        answer_text = answer['answer_jp']
    elif loaded_settings['setting_chat_language'] == '한국어':
        answer_text = answer['answer_ko']
    memory.save_conversation_memory('character', answer_text, answer['answer_en'])
    

def open_versions(e=None):
    def get_membership_list():
        membership_list = list()    
        
        # membership 참조
        membership_list.append("釉薬")
        membership_list.append("Aggregate Demand")
        membership_list.append("Zn Hey")
        membership_list.append("平田明")
        membership_list.append("Copper Brass")
        membership_list.append("スターフルーツ・カブ")
        membership_list.append("96mochi.")
        membership_list.append("ティーパーティー")
        membership_list.append("キラ サカザキ")
        membership_list.append("fu")
        membership_list.append("飛.")
        
        # 후원자 참조
        membership_list.append("최명진")
        membership_list.append("しらぬいかや")
        
        return membership_list

    # 변수 확인
    version_num = 0
    version_name = ''
    version_name = '1.0.0'
    # try:
    #     with open('./config/setting.pickle', 'rb') as file:
    #         data = pickle.load(file)
    #         if 'version_num' in data:
    #             print('version_num', version_num)
    #             version_num = data['version']
    #         if 'version_name' in data:
    #             print('version_name', version_name)
    #             version_name = data['version_name']
    # except:
    #     print(get_message('There is a problem with the metafile information\nPlease report it so I can handle it.'))
        
    ## $$$ New Asset Available => setting에 asset available 추가
    
    version_window_y = 450
    versions_window = tk.Toplevel(root, padx=5, pady=5)
    versions_window.title("Versions")
    versions_window.geometry(f"350x{version_window_y}")  # 400 + 한줄 20
    
    # 초기화
    frame_row_idx = 0

    # Frame : Player
    frame_version = tk.Frame(versions_window, padx=10)#, borderwidth=1, relief=tk.SOLID)
    frame_version.grid(row=frame_row_idx, column=0, sticky="nsew")
    frame_row_idx+=1

    version_label = tk.Label(frame_version, text="Version " + version_name,  anchor='w', justify='left', width=30)
    version_label.grid(row=0, column=0, padx=10, pady=4, sticky="w")
    version_update_label = tk.Label(frame_version, text=get_message("Latest"),  anchor='e', justify='right')
    version_update_label.grid(row=0, column=1, padx=10, pady=4, sticky="w")
    
    # 최신버전 여부 확인 후 label 갱신
    # meta_version_setting = 0
    # meta_version_setting_name = ''
    # meta_version_setting, meta_version_setting_name = get_meta_data()

    # if meta_version_setting and meta_version_setting >= version_num:
    #     # 최신 버전 있음. 업데이트 필요
    #     version_update_label.config(text=get_message("Updateable"))
    #     # 안내문 줄 추가 및 길이 업데이트
    #     frame_version_guide = tk.Frame(versions_window, padx=10)#, borderwidth=1, relief=tk.SOLID)
    #     frame_version_guide.grid(row=frame_row_idx, column=0, sticky="nsew")
    #     frame_row_idx+=1
    #     version_label = tk.Label(frame_version_guide, text=get_message("Run install.exe for the update."),  anchor='w', justify='left')
    #     version_label.grid(row=0, column=0, padx=10, pady=4, sticky="w")
    #     version_window_y+=30
    #     versions_window.geometry(f"350x{version_window_y}")  # 400 + 한줄 20
    
    version_separator = ttk.Separator(versions_window, orient="horizontal")
    version_separator.grid(row=frame_row_idx, column=0, sticky="nswe", padx=8)
    frame_row_idx+=1

    # Frame : Membership (감당 안되면 명예의 전당이 생김)
    frame_membership = tk.Frame(versions_window)
    frame_membership.grid(row=frame_row_idx, column=0, pady=(10,10), sticky="nsew")
    frame_row_idx+=1
    
    membership_title_label = tk.Label(frame_membership, text="Special Thanks",  anchor='n', justify='center')
    membership_title_label.grid(row=0, column=0, padx=10, pady=((4,8)), sticky="w")
    frame_membership_desc = tk.Frame(frame_membership, padx=5, pady=10)
    frame_membership_desc.grid(row=1, column=0, sticky="nsew")
    
    membership_list = get_membership_list()
    membership_column_max = 2  # 2열 종대
    membership_column = 0
    membership_row = 0
    for member in membership_list:
        membership_desc_label = tk.Label(frame_membership_desc, text=member, width=20, anchor='w', justify='left')
        membership_desc_label.grid(row=membership_row, column=membership_column, padx=5, pady=4, sticky="w")
        
        # 다음
        if membership_column + 1 >= membership_column_max:
            membership_column = 0
            membership_row += 1
        else:
            membership_column += 1
            
    membership_separator = ttk.Separator(versions_window, orient="horizontal")
    membership_separator.grid(row=frame_row_idx, column=0, sticky="nswe", padx=8)
    frame_row_idx+=1      
    
    # Frame : Guidance
    frame_guidance = tk.Frame(versions_window, borderwidth=3, relief=tk.SOLID)
    frame_guidance.grid(row=frame_row_idx, column=0, sticky="nsew", pady=5)
    frame_row_idx+=1
    
    # 투명한 배경을 가진 캔버스 위젯을 생성합니다.
    canvas = tk.Canvas(frame_guidance, width=330, highlightthickness=0, borderwidth=0, bd=0, bg='#1e90ff')
    canvas.pack()

    # 텍스트 표시 후 높이 측정하여 canvas 높이 계산
    guidance_text = get_message("The program is free to use and is supported by many generous donors.")
    text_label = canvas.create_text(330//2, 0, text=guidance_text, anchor='center', width=330-20, font=("Noto Sans", 12, "bold"))
    x0, y0, x1, y1 = canvas.bbox(text_label)  # text label 높이
    canvas_height = int(y1 - y0 + 60)
    canvas.config(height=canvas_height)
    canvas.move(text_label, 0, canvas_height//2)    

def show_update_message(e=None):
    MessageBoxShowInfo(root, "Info", "Under updating...")

if __name__ == "__main__":
    # 초기화
    is_program_ended = False
    loaded_settings = load_settings()  # 설정 세팅 로드
    
    # 로딩옵션 정리
    loading_option_root = tk.Tk()
    loading_option_screen = LoadingOptionScreen(loading_option_root)
    loading_option_root.mainloop()  # Tkinter의 mainloop 실행
    
    if not loading_option_screen.confirmed:
        sys.exit()
    
    # loading_option_screen_thread = threading.Thread(target=make_loading_option_screen)
    # loading_option_screen_thread.start()   
    
    # 로딩화면 시작
    if not DEV_MODE:
        loading_screen_thread = threading.Thread(target=make_loading_screen)
        loading_screen_thread.start()
        
    if loaded_settings['setting_program_type'] == 'GPU':
        ai_singleton.get_llm()  # GPU 용 싱글톤 로드 (옵션 X)
    else:
        load_models()  # 모델과 쓰레드 로드
    
    loading_screen_text = "Loading extra..."
    pygame.mixer.init()  # 음성 재생 전에 선언되어야 함
    
    # 로딩화면 종료
    loading_screen_text = "Loading Finished!"
    is_loading = False    
    if loading_screen_thread and loading_screen_thread.is_alive():
        loading_screen_thread.join()
    time.sleep(0.5)  # 새로운 tk 사이에 안전책용 (필요없긴 함)
    
    # Tkinter 세팅
    root = tk.Tk()
    root.config(highlightbackground='#306198')

    label = tk.Label(root, bd=0, bg='#306198')  # Label 설정
    root.overrideredirect(True)
    root.wm_attributes('-topmost', 90)
    root.wm_attributes('-transparentcolor', '#306198')
    label.pack()  # 라벨 배치

    # UI 이미지 로딩
    AnswerBalloon.set_images()
    img_input = Image.open("./assets/png/input2.png")
    img_output = Image.open('./assets/png/output2.png') 
    img_ask_balloon = Image.open('./assets/png/ask2.png') 
    
    close_img = ImageTk.PhotoImage(Image.open("./assets/png/close.png").resize((20, 20)))
    image_img = ImageTk.PhotoImage(Image.open("./assets/png/image.png").resize((20, 20)))
    search_img = ImageTk.PhotoImage(Image.open("./assets/png/search.png").resize((20, 20)))
    send_img = ImageTk.PhotoImage(Image.open("./assets/png/send.png").resize((20, 20)))
    answer_balloon_stop_img = ImageTk.PhotoImage(Image.open("./assets/png/stop.png").resize((20, 20)))
    answer_balloon_speaker_img = ImageTk.PhotoImage(Image.open("./assets/png/speak.png").resize((20, 20)))
    answer_balloon_question_view_img = ImageTk.PhotoImage(Image.open("./assets/png/faq.png").resize((20, 20)))
    answer_balloon_detail_img = ImageTk.PhotoImage(Image.open("./assets/png/detail.png").resize((20, 20)))
    answer_balloon_regenerate_img = ImageTk.PhotoImage(Image.open("./assets/png/refresh.png").resize((20, 20)))
    answer_balloon_translate_img = ImageTk.PhotoImage(Image.open("./assets/png/translate.png").resize((20, 20)))
    answer_balloon_cancel_img = ImageTk.PhotoImage(Image.open("./assets/png/delete.png").resize((20, 20)))
    answer_balloon_copy_img = ImageTk.PhotoImage(Image.open("./assets/png/copy.png").resize((20, 20)))    
    img_modify = ImageTk.PhotoImage(Image.open('./assets/png/modify.png').resize((20, 20)))
    check_img = ImageTk.PhotoImage(Image.open('./assets/png/check.png').resize((20, 20)))  # $$$ 비행기 같은 모양으로 변경
    
    img_volume_off = ImageTk.PhotoImage(Image.open('./assets/png/speaker_off.png').resize((15, 15)))  # 세팅 쪽 토글
    img_volume_on = ImageTk.PhotoImage(Image.open('./assets/png/speaker_on.png').resize((15, 15)))
    
    # 애니메이션 세팅
    anim, anim_set = init_anim()
    set_status('idle')
    
    # 우클릭 메뉴 생성
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Setting", command=open_settings)
    menu.add_command(label="AI Setting", command=open_ai_settings)
    menu.add_separator()  
    menu.add_command(label="Idle", command=lambda: set_status("idle"))
    menu.add_command(label="Idle Talk", command=lambda: active_trigger("idle"))
    menu.add_command(label="Go Left", command=lambda: set_status("walk_left_lock"))
    menu.add_command(label="Go Right", command=lambda: set_status("walk_right_lock"))
    menu.add_command(label="Sit", command=lambda: set_status("sit_lock"))
    menu.add_separator()  # 구분선 추가
    # if is_talk_thread_activated:
    #     menu.add_command(label="Deactivate Speech Recognition", command=lambda: deactivate_speech_recognition())
    # else:
    #     menu.add_command(label="Activate Speech Recognition", command=lambda: activate_speech_recognition())
    menu.add_command(label="Activate TikiTaka", command=lambda: active_tikitaka())
    # 스크린샷 기능 추가
    menu.add_separator()  
    screenshotApp = ScreenshotApp(root, menu)
    menu.add_command(label="Activate Focus", command=lambda: active_focus())
    menu.add_separator()  
    menu.add_command(label="Load models", command=lambda: load_models())
    menu.add_command(label="Clean models", command=lambda: clean_models())
    # menu.add_separator()  
    # menu.add_command(label="S.Balloon", command=lambda: show_status_balloon(image_folder='./assets/fx/loading2'))
    # menu.add_command(label="K.Balloon", command=kill_status_balloon)
    menu.add_separator()  
    # if DEV_MODE:
    #     menu.add_command(label="History", command=lambda: history.open_history_screen(root))
    # else:
    #     menu.add_command(label="History", command=lambda: show_update_message())
    menu.add_command(label="Clear Conversation", command=memory.reset_conversation_memory)
    # menu.add_separator()  
    # menu.add_command(label="Version", command=open_versions)

    # 종료    
    menu.add_separator()  
    menu.add_command(label="Exit", command=lambda: root.destroy())
    
    # 마우스 버튼 클릭 및 이동 이벤트
    root.bind("<Button-1>", on_click_async)
    root.bind("<Button-1>", on_drag_start, add='+')
    # root.bind("<Button-1>", lambda event: show_effect_on_click(event, 'pop'), add='+')
    root.bind("<B1-Motion>", on_drag_motion)
    root.bind("<ButtonRelease-1>", on_drag_release)
    root.bind("<Button-3>", on_right_click)  # 더블클릭으로 열기 (우클릭과 같이 있을 경우 메뉴 고장날 수 있음)
    # root.bind("<Double-Button-1>", on_right_click)  # 우클릭말고도 더블클릭으로도 메뉴
    

    
    # root 초기 위치 설정
    monitor_screen_width, monitor_screen_height = 1920, 1080  # 화면 가로 세로 크기 재설정
    # rx = random.randint(0 + 20, monitor_screen_width - 20) // 2
    rx = 500
    ry = monitor_screen_height // 2
    root.geometry(f"+{int(rx)}+{int(ry)}")
    
    # 기동
    root.after(10, update, 20)  # 상태 관련. 0.02초마다 실행
    root.after(10, update_physics_move) 

    root.mainloop()

    # 메인프로그램 종료
    is_program_ended = True

    # thread 종료
    is_talk_thread_activated = False
    if talk_thread and talk_thread.is_alive():
        talk_thread.join()
    is_chat_key_thread_activated = False
    if chat_key_thread and chat_key_thread.is_alive():
        chat_key_thread.join()
    if faster_whisper_listener:
        faster_whisper_listener.set_shutdown_event()
    if llama_server:
        llama_server.stop()
    
    # 현재 티키타카 쪽이 잘 정리되지 않고 있음
    # sys.exit()
    os._exit(0)
    
    print('a_tikitaka_thread', tikitaka_thread)
    if tikitaka_thread and tikitaka_thread.is_alive():
        tikitaka_thread.join()
    print('a_tikitaka_status_thread', tikitaka_status_thread)
    if tikitaka_status_thread and tikitaka_status_thread.is_alive():
        tikitaka_status_thread.join()
    print('a_screenshotApp', screenshotApp)
    if screenshotApp and screenshotApp.continuous_save_running:
        screenshotApp.toggle_continuous_save()  # 연속저장 종료시 알아서 thread join

