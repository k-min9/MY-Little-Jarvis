# 프로그램 내 변수 형상관리
is_stop_requested = False  # Stream 대답 중, 대답 중지

def get_is_stop_requested():
    global is_stop_requested
    return is_stop_requested

def set_is_stop_requested(value=True):
    global is_stop_requested
    is_stop_requested = value
