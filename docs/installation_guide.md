# 설치 가이드

## 사용자 가이드

MY-Little-JARVIS는 exe 형태의 Product 상태로 배포되어 바로 사용하실 수 있습니다.

- 정식 다운로드 링크 : [https://huggingface.co/mingu4969/my-little-jarvis-dist/resolve/main/Install.exe]
- Installer 명세
  - 개요 : python 설치, version, venv, gmake, gpu 설정 등 복잡한 설정 없이 원클릭 Install 파일 지원
  ![installer](../docs_image/installer1.png)
  - 설치방법
    1. 위에서 Download하신 Installer.exe를 실행해주세요.
       - 실행한 프로그램 우측 하단의 Install을 클릭하시면 Installer.exe 위치에 바로 설치됩니다. (설치할 위치나 언어를 변경할 수 있습니다.)
    2. 설치가 완료되었다는 안내메시지가 뜨면 확인을 눌러 종료해주세요.
    3. Done! 설치된 폴더에 있는 jarvis.exe를 실행해주세요.
- 프로그램 명세
  - 구동환경 : Windows
  - 용량 : 13.2GB
  - 지원언어 : 한국어/English/日本語

## 개발자 가이드

개발자분들을 위한 설치가이드입니다. 직접 개발환경을 구축하고 패키징하실 수 있습니다.

- 프로젝트 환경 설정
  - Python 3.9.6
  - Cuda 11.6
  - Git
- 프로젝트 깃허브를 클론

    ``` bash
    git clone https://github.com/k-min9/MY-Little-Jarvis.git
    ```

- 필요 라이브러리 설치
  - 가장 복잡한 설정이 필요한 llama-cpp-python을 wheel로 설치하기 때문에 requirements.txt는 추천되지 않습니다.

    ``` bash
    py -3.9 -m venv venv

    # 일반 library
    pip install pyinstaller
    pip install googletrans==4.0.0-rc1
    pip install tkinterdnd2 # tkinter 보조로 drag and drop 등의 외부 입력 받음
    pip install pyaudio
    pip install keyboard
    pip install pygame
    pip install Unidecode
    pip install Flask
    pip install screeninfo

    # websearch 관련
    pip install sentence-transformers
    pip install beautifulsoup4
    pip install optimum
    pip install duckduckgo_search==6.1.0
    pip install lxml
    pip install faiss-cpu==1.8.0
    pip install rank_bm25==0.2.2

    # AI 관련 library
    ## 기본
    pip install langchain
    pip install langchain-community
    pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu116
    pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121 --upgrade --force-reinstall --no-cache-dir
    pip install pynvml  # GPU 
    pip install transformers==4.41.0
    ## 음성인식
    pip install sounddevice
    pip install faster-whisper
    pip install SpeechRecognition  # init에 faster-whisper을 위한 함수 개조 있음
    ## 음성합성(VITS)
    pip install jamo g2pk2 
    pip install ko-pron
    pip install Cython
    pip install scipy==1.12.0
    pip install librosa
    # pip install pyopenjtalk==0.2.0 # 일본어음성합성시 필요
    ## 화상인식
    pip install einops timm  # florence

    ## conflict된 버전 정합성용 재설치
    pip install numpy==1.22.4
    pip install httpx==0.13.3

    ### Legacy (Not using)
    pip install llama-cpp-python --prefer-binary --extra-index-url=https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/AVX2/cu116

    ```

- pyinstaller로 프로젝트를 패키징할 수 있습니다.

    ``` bash
    pyinstaller --onedir main.py -n jarvis --noconsole --contents-directory=files --noconfirm --icon=./assets/ico/icon_arona.ico # 메인 프로그램
    pyinstaller --onedir server_interface.py -n jarvis_server --noconsole --contents-directory=files_server --noconfirm --icon=./assets/ico/icon_arona.ico # 서버 프로그램1
    pyinstaller --onedir server_interface_jp.py -n jarvis_server_jp --contents-directory=files_server --noconfirm --icon=./assets/ico/icon_arona.ico --noconsole # 서버 프로그램2ㄴ
    ```

## NEXT STEP : [사용 가이드](docs/how_to_use_guide.md)
