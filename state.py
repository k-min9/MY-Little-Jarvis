# 프로그램 내 변수 형상관리
is_stop_requested = False  # Stream 대답 중, 대답 중지
is_screenshot_area_selecting = False  # 현재 스크린샷 범위 설정 중

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