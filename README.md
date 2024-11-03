# 👩‍💻 MY Little JARVIS - 나만의 작은 AI 비서

![title](docs_image/title.png)

## Installer Download : release or <https://shorturl.at/QrFmp>

[빠른 설치 가이드](docs/installation_guide.md)

## 개요

- 나만을 위한 그냥 좀 많이 똑똑한 시스템(Just A Rather Very Intelligent System)
- 오픈소스 AI(로컬 LLM)으로 만든 나만의 작은 AI 비서

## 배경

현재 클라우드 기반 AI 서비스는 개발자에게 불편하고 비용이 많이 든다는 문제로 인해, AI 수익화가 어려워지고 있으며, 기업 중심의 서비스로 전환이 가속화되고 있습니다.

[My little Jarvis] 프로젝트는 로컬 LLM을 활용해 개발자가 비용 없이 직접 AI 시스템을 구축하고 제어할 수 있도록 함으로써 이러한 제약을 극복하고자 합니다.

이를 통해 개인 사용자들도 비싼 클라우드 서비스에 의존하지 않고, 실생활에서 유용하게 사용할 수 있는 상업적 가치가 있는 AI 비서를 활용할 수 있게 될 것입니다.

## 주요기능

- 상호작용 가능한 인터페이스: 친숙한 윈도우 환경에서 AI 합성기술로 만든 애니메이션 포함 이미지를 가진 비서와 실제로 대화하는 듯한 인터페이스를 제공합니다.
- 오픈소스 AI를 통한 대답 추론 및 생성: LLAMA3.1의 양자화 AI 모델을 기반으로 개인 PC 환경에서 자연스럽고 빠른 대화를 생성합니다.
- 글로벌한 언어 제공 및 세부 설정 기능: 질문과 답변에 한/영/일 언어를 선택할 수 있으며, 캐릭터 상호작용 빈도 및 크기 등을 설정할 수 있습니다.
- 메타 인지를 통한 캐릭터 해석 및 AI 쪽에서 대화: AI가 캐릭터를 해석하고, 유저가 아닌 AI가 먼저 말을 거는 기능을 제공하여 대화 진입장벽을 낮춥니다.
- 의도 파악 기능: 유저의 입력을 분석해 특정 포맷으로 반환하여, 대화의 맥락을 파악하고 다른 기능과 연계할 수 있습니다.
- 메모리 기능: 대화 내용 자체를 기억하고 다음 대화에 반영하고, 대화에서 유저와 AI의 성격을 파악합니다.
- 화상 인식 기능: 화면 일부 또는 입력된 이미지를 AI 비서의 입력값으로 활용할 수 있습니다.
- Web 검색 기능: 웹 검색 결과를 반영해 최신 정보나 필요한 정보를 대화에 활용할 수 있습니다.
- 음성 인식 기능: 음성인식을 통해 대화가 가능하며, VAD 기능으로 음성과 소음을 구분합니다.
- Easy Installer: 클릭 한 번으로 설치가 가능한 Installer를 제공하며, 설치 위치와 언어를 설정할 수 있습니다.
- 최적화된 리소스 사용 : 상황에 맞춰 CPU/GPU 사용여부를 선택할 수 있고, GPU 사용시 최적화된 VRAM 사용량을 추천해줍니다.
- 서버 기능 : Flask를 통해 API로 출력할 수 있게 하여 서버로서 활용하여 멀티플랫폼을 구축할 수 있습니다.

## 이런 당신에게 필요한 프로젝트

- 캐릭터와 상호작용하고 싶으신 분
  - 높은 확장성으로 장르를 가리지 않고 대응할 수 있습니다.
  - 타 프로그램 이용중에도 대화가 가능합니다.
- 정서적 교감이 필요하신 분
  - 넓어가는 간병인시장
  - 격려와 피드백을 통한 의욕고취
- 높은 AI 접근 장벽이 무서운 개발자/사용자
  - 개발자는 작게는 파이썬 버전부터 크게는 dll설치까지 극악인 환경설정이 필요하지만, wheel로 가장 어려운 부분의 설치를 조율하여 개발에만 집중할 수 있습니다.
  - 사용자도 복잡한 repo clone이나 설치 없이 원 클릭으로 가능한 설치환경 제공합니다.

## 차별점 : Why JARVIS?

Closed AI가 높은 편의성과 성능을 가지고 그에 맞는 환경과 비용이 필요하다면, MY-Little-JARVIS는 높은 확장성과 생태계를 바탕으로 최적화된 리소스 만으로 운용 가능합니다.

| **차이점**           | **Closed AI(GPT, Claude...)**                  | **Open Source(My Little Jarvis)**          |
|----------------------|-----------------------------------------------|-----------------------------------------------|
| **생태계**           | 대기업 위주                                    | 오픈소스.                                     |
| **기술 공유**         | 대기업 중심의 관리                               | 개발자 및 사용자 중심의 대규모 글로벌 커뮤니티   |
| **비용**             | 클라우드 기반, 종량제 요금제 사용.비쌈.            | 로컬 기반(+클라우드 지원), 무료.            |
| **보안**             | 데이터가 서버로 전송될 수 있음                 | 데이터가 외부로 전송되지 않음                   |
| **컨트롤 자유도**    | 설정된 파라미터 내에서 이용                      | 개발자가 파라미터 설정 가능                   |
| **인터넷 연결**      | 인터넷 필수, 서버에 의존                          | 인터넷 없이 오프라인으로 작동 가능               |
| **서버 효율**           | 필요 기능 수 만큼 API를 호출하여 조립             | 모듈 조립을 통해 한 번의 호출로 여러 기능을 동시에 실행  |
| **모델**             | 고정된 클라우드 모델 사용, 주어진 선택지에서 선택   | 다양한 모델을 직접 소유할 수 있고 경량화하거나 개조할 수 있음   |
| **하드웨어**         | 높은 수준의 하드웨어 필요. (개인PC 불가)       | 수준에 맞는 하드웨어로 구동 가능. (개인PC 가능)   |

## Get Started

- [설치 가이드](docs/installation_guide.md)
- [사용 가이드](docs/how_to_use_guide.md)

### 산출물

- [발표 자료](docs/presentation.pptx)

## 주요 서비스 화면

### 인터페이스

- 사용 Tool : Stable-Diffusion, ComfyUI
- 사용 기술 : Text-to-Image, ControlNet, (+인페인팅), toonCrafter
- 화면에서 [직관적으로 상호작용]하는 인터페이스를 로컬에서 완성

![interaction](docs_image/interaction.gif)

### 의도파악

- [질문에 Web 검색이 필요할까?] 를 AI가 생각하게 함

![ai_intent](docs_image/ai_intent.png)

### Web검색

- 입력된 이미지나 설정된 배경에 관한 대화 기능

![ai_web](docs_image/ai_web.png)

### 화상인식

- 입력된 이미지나 설정된 배경에 관한 대화 기능

![ai_florence](docs_image/ai_florence.png)

### 티키타카(고속-음성인식대화)

- 실시간 음성 인식을 통한 질문 및 답변

![tikitaka](docs_image/tikitaka.png)

### 대화 이력 관리

- 대화 저장/변경/수정/삭제 및 요약을 통한 제목 추천 기능

![history](docs_image/history.png)

## 사용 AI 기술

- MY-Little-JARVIS는 아래와 같은 AI 기술을 사용했습니다.
  - AI 대답 생성 및 의도 파악, 번역, 서버 등 주요 AI 모듈
    - 사용 주 기술 : LLama.cpp, langchain, transformers
    - 사용 모델 : Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
  - AI 캐릭터 생성
    - 사용 도구 : Stable Diffusion
    - 사용 주 모델 : Animagine3.1
  - AI 캐릭터 애니메이션 생성
    - 사용 도구 : Stable Diffusion, ComfyUI
    - 사용 주 기술 : AnimateDiff, ToonCrafter
  - Web 검색용 단어 단축
    - 사용 주 기술 : sentence-transformers, duckduckgo_search
    - 사용 모델 : all-MiniLM-L6-v2
  - AI 음성 합성
    - 사용 기술 : VITS (ISTFT로 고속 추론)
    - 사용 데이터 : KSS 오픈 데이터
  - AI 음성 인식
    - 사용 기술 : faster-whisper + sound, VAD
    - 사용 모델 : Systran-faster-whisper-small, sillero_vad
  - AI 화상 인식
    - 사용 기술 : Florence2
    - 사용 모델 : Microsoft-Florence-2-base
- 외부 AI 모델
  - kss_korean_ISTFT.pth
  - Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
  - Microsoft-Florence
  - Sentence Transformers-all-MiniLM-L6-v2
  - Faster-whisper(small)
  - sillero_vad.onnx

## Special Thanks

- 이번 프로젝트에서 사용한 [Nexon]의 [블루아카이브] IP에 관하여, 여러번에 걸친 연락과 문의 끝에 [문제가 있으면 조치한다]는 형태로 IP 사용을 수락 받았습니다. ([증적](docs/special_thanks_nexon.md))
- 이 프로젝트는 원본 리소스, 음성, Asset등의 자산을 활용하지 않았고, [Nexon게임IP사용가이드](https://member.nexon.com/policy/gameipguide.aspx)를 준수하였습니다.
- 이 자리를 빌어 감사의 말씀을 전합니다.
