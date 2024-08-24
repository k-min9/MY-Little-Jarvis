import tkinter as tk
import json
import uuid

from messages import getMessage

loading_message_box = None

def load_settings():
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
            # Setting 원본         
            if 'setting_language' not in settings or settings['setting_language'] not in ["日本語", "English", "한국어"]:
                settings['setting_language'] = '日本語'
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
                settings['setting_chat_language'] = '日本語'
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
                settings['setting_is_gravity'] = True
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
                settings['setting_talk_language'] = '日本語'
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
                settings['setting_language'] = '日本語'
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
            if 'setting_ai_sr' not in settings:  # "send", "check"
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
            return settings
    except FileNotFoundError:
        # 파일이 없을 경우 기본값 설정
        settings = {
            # Installer에서 정한 이름 (변경시 그쪽도 갱신)
            "version": 1,
            "version_name": '1.0.0',
            # Main 세팅
            "setting_name": 'sensei',
            "setting_uid": str(uuid.uuid4()),
            "setting_char": 'arona',
            "setting_size": 1,
            "setting_size_effecter": 0,
            "setting_chat_mode": "Click",
            "setting_chat_key": "",
            "setting_chat_language": "日本語",
            "setting_chat_click_sensitivity": 100,
            "setting_voice_mode": "CPU",
            "setting_volume": 75,
            "setting_is_volume_on": True,
            "setting_is_gravity": True,
            "setting_mobility": 1,
            "setting_moving_speed": 0,
            "setting_collision": 'Task bar',
            "setting_ai": 'Inworld',
            "setting_translator": 'Google',
            "setting_talk_mode": 'OFF',
            "setting_talk_key": '',
            "setting_talk_language": '日本語',
            "setting_talk_quality": 'base',
            "setting_can_stop_chat": False,
            "setting_history_folder": './history',
            "setting_language": '日本語',
            "setting_preload_voice": False,
            "setting_preload_sr": False,
            "setting_key_deepL": "",
            # AI 관련 설정
            "setting_ai_stream" : "on",
            "setting_ai_sr" : "send",  # "send", "check"
            "setting_ai_web" : "off",
            "setting_ai_story" : "off",
            "setting_ai_memory" : "off",
        }
        return settings


def get_message(text, is_special=False):
    loaded_settings = load_settings()
    
    return getMessage(text, loaded_settings['setting_language'], is_special)

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

def test_ask():
    ask_question_box = MessageBoxAskQuestion(root, "Confirm", "YES / NO")
    root.wait_window(ask_question_box)
    if ask_question_box.result:   
        print('yes')
    else:
        print('no')

def test_show():
    MessageBoxShowInfo(root, "Error", "key [ENTER] is not allowed.")


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
    
    menu = tk.Menu(root, tearoff=0)
    menu.add_command(label="Ask", command=test_ask)
    menu.add_command(label="Show", command=test_show)
    
    root.bind("<Button-3>", on_right_click)


    root.mainloop()
    
    

    


