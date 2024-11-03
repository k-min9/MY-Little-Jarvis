'''
프로그램 내 변수 형상관리
'''
import json


is_stop_requested = False  # Stream 대답 중, 대답 중지
is_screenshot_area_selecting = False  # 현재 스크린샷 범위 설정 중

use_gpu_percent = 0 

g_language = 'ko'  # 언어 : ["日本語", "English", "한국어"] to ['ja', 'en', 'ko']
g_language_init = ''  # 최초 프로그램 기동시의 언어

def get_is_stop_requested():
    global is_stop_requested
    return is_stop_requested

def set_is_stop_requested(value=True):
    global is_stop_requested
    is_stop_requested = value

def get_is_screenshot_area_selecting():
    global is_screenshot_area_selecting
    return is_screenshot_area_selecting

def set_is_screenshot_area_selecting(value=True):
    global is_screenshot_area_selecting
    is_screenshot_area_selecting = value

# setting의 UI 언어
def get_g_language():
    global g_language
    g_language = 'ko'  # ["日本語", "English", "한국어"]
    try:
        with open('config/setting.json', 'r', encoding='utf-8') as file:
            settings = json.load(file)
            if 'setting_language' in settings:
                if settings['setting_language'] == '한국어':
                    g_language = 'ko'
                elif settings['setting_language'] == '日本語':
                    g_language = 'ja'
    except:
        pass
    return g_language

# 최초 로딩시 언어 세팅 후 그 언어만 사용 / 메뉴용
def get_g_language_init():
    global g_language_init
    if not g_language_init:
        g_language_init = 'ko'  # ["日本語", "English", "한국어"]
        try:
            with open('config/setting.json', 'r', encoding='utf-8') as file:
                settings = json.load(file)
                if 'setting_language' in settings:
                    if settings['setting_language'] == '한국어':
                        g_language_init = 'ko'
                    elif settings['setting_language'] == '日本語':
                        g_language_init = 'ja'
                    elif settings['setting_language'] == 'English':
                        g_language_init = 'en'
        except:
            pass
    return g_language_init


def get_use_gpu_percent():
    global use_gpu_percent
    return use_gpu_percent

def set_use_gpu_percent(use_vram):
    global use_gpu_percent
    use_gpu_percent = use_vram * 100 / 8