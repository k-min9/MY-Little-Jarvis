import os
import json
import uuid

# 프로그램 설정 불러오기
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

# 프로그램에서 사용하는 캐릭터 설정(eden) 불러오기
def load_settings_eden():
    try:
        with open('config/eden.json', 'rb') as file:
            settings_eden = json.load(file)
            if 'version' not in settings_eden:
                settings_eden['version'] = 1
            if 'version_name' not in settings_eden:
                settings_eden['version_name'] = '1.0.0'
            if 'char_main' not in settings_eden:
                settings_eden['char_main'] = ''
            if 'char_list' not in settings_eden:
                settings_eden['char_list'] = ['arona', 'mari']
            return settings_eden
    except FileNotFoundError:
        settings_eden = dict()
        settings_eden['version'] = 1
        settings_eden['version_name'] = '1.0.0'
        settings_eden['char_main'] = ''
        settings_eden['char_list'] = ['arona', 'mari']
        return settings_eden
    
####
# 저장
def save_settings(loaded_settings):
    # config 폴더가 없으면 생성
    os.makedirs('config', exist_ok=True)  
    # 설정을 JSON 형식으로 저장
    with open('config/setting.json', 'w', encoding='utf-8') as file:
        json.dump(loaded_settings, file, ensure_ascii=False, indent=4)
    print('save settings in config/setting.json')

def save_settings_eden(loaded_settings_eden):
    # config 폴더가 없으면 생성
    os.makedirs('config', exist_ok=True)  
    # 설정을 JSON 형식으로 저장
    with open('config/eden.json', 'w', encoding='utf-8') as file:
        json.dump(loaded_settings_eden, file, ensure_ascii=False, indent=4)
    print('save settings_eden in config/eden.json')