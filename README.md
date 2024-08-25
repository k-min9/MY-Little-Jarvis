# 👩‍💻 MY Little JARVIS - 나만의 작은 AI 비서

![title](docs_image/title.png)

## 개요

- 나만을 위한 그냥 좀 많이 똑똑한 시스템(Just A Rather Very Intelligent System)

## 환경

- Python 3.9.6
- Cuda 11.6

## 세팅

``` bash
py -3.9 -m venv venv

# 일반 library
pip install pyinstaller
pip install googletrans==3.1.0a0
pip install tkinterdnd2 # tkinter 보조로 drag and drop 등의 외부 입력 받음
pip install pyaudio
pip install keyboard
pip install pygame
pip install Unidecode
pip install Flask

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
pip install llama-cpp-python --prefer-binary --extra-index-url=https://jllllll.github.io/llama-cpp-python-cuBLAS-wheels/AVX2/cu116
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

```

- 외부 파일
  - kss_korean_ISTFT.pth
  - Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf

## 배포

- 패키징

``` bash
pyinstaller --onedir main.py -n jarvis --noconsole --contents-directory=files --noconfirm --icon=./assets/ico/icon_arona.ico
```

- 업로드

- 다운로드
https://huggingface.co/mingu4969/my-little-jarvis-dist/resolve/main/Install.exe
