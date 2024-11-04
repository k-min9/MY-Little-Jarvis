# 👩‍💻 MY Little JARVIS - My own little AI assistant

![title](../docs_image/title.png)

## Installer Download : release or <https://shorturl.at/QrFmp>

[Quick installation guide](../docs/installation_guide.md)

## Language

[한국어](../README.md)|[日本語](../docs/README_jp.md)|**English**

## Overview

- Just A Rather Very Intelligent System
- My own little AI assistant made with open source AI (local LLM)

## Background

Cloud-based AI services are currently experiencing an accelerating shift towards enterprise-centric services as AI monetization is becoming more difficult due to its inconvenience and cost for developers.

The [My little Jarvis] project aims to overcome these limitations by leveraging local LLMs to allow developers to build and control AI systems directly at no cost.

This will also allow individual users to take advantage of commercially valuable AI assistants for real-life use without having to rely on expensive Cloud services.

## Key Features

- Interactive interface: Provides an interface that is like having a real conversation with a secretary in a familiar Windows environment, with images containing animations created with AI synthesis technology.
- Open source AI for answer inference and generation: Generates natural and quick conversations in a personal PC environment based on the LLAMA 3.1 quantized AI model.
- Global language provision and advanced configuration functions: Allows users to select Korean/English/Japanese languages for questions and answers, and to configure character interaction frequency and size, etc.
- Meta-recognition of character interpretation and conversation from the AI side: Provides the ability for the AI to interpret the character and talk to user first, lowering the barrier to entry into the conversation.
- Intention understanding function: Analyzes user input and returns it in a specific format to understand the context of the conversation and link it to other functions.
- Memory function: Memorize the content of the conversation itself and reflect it in the next conversation to understand the personality of the user and AI from the conversation.
- Image recognition function: A portion of the screen or an input image can be used as an input value for the AI assistant.
- Web search function: Reflects web search results to utilize the latest and necessary information in conversation.
- Voice Recognition Function: Conversation is possible through voice recognition, and the VAD function distinguishes between voice and noise.
- Easy Installer: Provides a one-click Installer and allows the user to set the installation location and language.
- Optimized Resource Usage : Allows the user to choose CPU/GPU availability depending on the situation and recommends optimized VRAM usage when using GPU.
- Server functionality : Allows output via API through Flask, and can be utilized as a server to build multi-platforms.

## Who needs this project

- Those who want to interact with characters
  - Highly scalable and can be used in any genre.
  - Conversation is possible even while using other programs.
- People who need emotional interaction
  - Expanding market of caregivers
  - Motivation through encouragement and feedback
- Developers/users afraid of high access barriers to AI
  - Developers need to set up nefarious environments, from small Python versions to large dll installations, but with wheel they can coordinate the most difficult part of the installation and focus solely on development.
  - Users are also provided with a one-click installation environment without complicated repo clone or installation.

## Differences : Why JARVIS?

Whereas closed AI requires a high level of convenience and performance with a corresponding environment and cost, MY-Little-JARVIS is highly scalable and can be operated with optimized resources based on the ecosystem.

| **Differences**           | **Closed AI(GPT, Claude...)**                  | **Open Source(My Little Jarvis)**          |
|----------------------|-----------------------------------------------|-----------------------------------------------|
| **System**           | Large Company                                    | Open Source                                     |
| **technology sharing**         | large company-centric management        | large global community of developers and users   |
| **Cost**             | Cloud-based, pay-as-you-go usage. Expensive.           | Local-based (+cloud support), free.                |
| **Security**             |  Data may be sent to servers    | Data is not sent externally              |
| **Control Freedom**    |  Use within configured parameters                     | Developer sets parameters            |
| **Internet Connection**      | Internet required, server dependent             | Can work offline without Internet              |
| **Server Efficiency**   |  Call and assemble APIs for as many functions as needed     | Modular assembly allows multiple functions to be performed simultaneously with a single call  |
| **Models**             | Use a fixed cloud model and choose from a given set of options | Directly own a variety of models, which can be lightweight or modified |
| **Hardware**         | Requires high level hardware (not for personal PC) | Can be driven by level appropriate hardware (can be driven by personal PC)  |

## Get Started

- [Installation Guide](../docs/installation_guide.md)
- [Usage Guide](../docs/how_to_use_guide.md)

### Additional Materials

- [Presentation](../docs/presentation.pptx)

## Main service

### Interface

- Tools used : Stable-Diffusion, ComfyUI
- Techniques used : Text-to-Image, ControlNet, (+Inpainting), toonCrafter
- Completed the [intuitively interactive] interface locally.

![interaction](../docs_image/interaction.gif)

### Intent guessing

- Let the AI think about [whether the question requires a web search].

![ai_intent](../docs_image/ai_intent.png)

### Web search

- Can answer reflecting the result of web search.

![ai_web](../docs_image/ai_web.png)

### Image Recognition

- Conversation function about input image or figured background

![ai_florence](../docs_image/ai_florence.png)

### Tikitaka(High-speed speech recognition conversation)

- Question and answer by real-time speech recognition

![tikitaka](../docs_image/tikitaka.png)

### Conversation history management

- Conversation saving/modification/revision/deletion and title recommendation through summary

![history](../docs_image/history.png)

## used AI technologies

- MY-Little-JARVIS used the following AI technologies
  - Main AI modules such as AI answer generation and intent recognition, translation, server, etc.
    - Main technologies used : LLama.cpp, langchain, transformers
    - Model used : Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
  - AI character generation
    - Tool used: Stable Diffusion
    - Main model used: Animagine3.1
  - AI Character Animation Generation
    - Tools used: Stable Diffusion, ComfyUI
    - Main technology used : AnimateDiff, ToonCrafter
  - Word shortening for Web search
    - Main technologies used : sentence-transformers, duckduckgo_search
    - Model used: all-MiniLM-L6-v2
  - AI Speech Synthesis
    - Technology used: VITS (fast inference with ISTFT)
    - Data used : KSS open data
  - AI Speech Recognition
    - Technology used : faster-whisper + sound, VAD
    - Model used : Systran-faster-whisper-small, sillero_vad
  - AI Image Recognition
    - Technology used : Florence2
    - Model used : Microsoft-Florence-2-base
- External AI Model
  - kss_korean_ISTFT.pth
  - Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
  - Microsoft-Florence
  - Sentence Transformers-all-MiniLM-L6-v2
  - Faster-whisper(small)
  - sillero_vad.onnx

## Special Thanks

- Regarding [Nexon]'s [BlueArchive] IP used in this project, after several contacts and inquiries, this project received permission to use the IP in the form of [we will take action if there are any problems] after several contacts and inquiries. ([Proof](../docs/special_thanks_nexon.md))
- This project did not utilize any original resources, voice, assets, etc. and complied with the [Nexon Game IP Usage Guide](https://member.nexon.com/policy/gameipguide.aspx).
- I would like to take this opportunity to express our gratitude.
