import requests
import json
import subprocess
import os

def start_server_python():
    # 서버를 백그라운드에서 실행
    return subprocess.Popen(
        ['python', 'server_interface.py'], 
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )
    
def start_server():
    # 실행 파일 경로
    executable_path = './server_interface.exe'  # TODO serverfile naming needed
    
    # 서버를 백그라운드에서 실행
    return subprocess.Popen(
        [executable_path],
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
    )

def check_server_health(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.RequestException:
        return False

# 반환없이 Test용
def fetch_streaming_data(url, data):
    headers = {
        'Content-Type': 'application/json'
    }
    with requests.post(url, headers=headers, data=json.dumps(data), stream=True) as response:
        if response.status_code == 200:
            for line in response.iter_lines():
                if line:
                    try:
                        json_data = json.loads(line.decode('utf-8'))
                        print(json_data)
                    except json.JSONDecodeError as e:
                        print(f'JSON decode error: {e}')
        else:
            print(f'Error: {response.status_code} - {response.reason}')

if __name__ == '__main__':
    # start_server_python()
    # start_server()
    
    # from time import time
    # health_url = 'http://127.0.0.1:5000/health'
    # while not check_server_health(health_url):
    #     print("Waiting for server to be ready...")
    #     time.sleep(2)  # 2초 대기 후 다시 체크
        
    query = '내일 날씨가 어떨까?'
    image = ''
    
    stream_url = 'http://127.0.0.1:5000/conversation_stream/simple'
    request_data = {'query': query}
    print(query)
    fetch_streaming_data(stream_url, request_data)