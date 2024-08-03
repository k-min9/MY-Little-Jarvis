# model_manager.py
import llama_cpp
import gc
from queue import Queue
from threading import Thread
import traceback


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

    def release_instance(cls):
        if cls in cls._instances:
            del cls._instances[cls]

################################################################ LLM
LLM_LAYERS = 33
class LlamaCppModel(metaclass=SingletonMeta):
    def __init__(self):
        self.model = None
        self.initialized = False

    def __del__(self):
        self.release()

    def from_pretrained(self, path, gpu_percent=100):
        Llama = llama_cpp.Llama
        LlamaCache = llama_cpp.LlamaCache

        n_gpu_layers = int(LLM_LAYERS * gpu_percent / 100)

        params = {
            "model_path": path,  # 모델 파일 경로
            "n_ctx": 8192,  # 컨텍스트 길이 (최대 토큰 수)
            "n_threads": None,  # 모델 로딩 및 실행 시 사용할 스레드 수 (None이면 기본값 사용)
            "n_threads_batch": None,  # 배치 처리 시 사용할 스레드 수 (None이면 기본값 사용)
            "n_batch": 512,  # 배치 크기 (한 번에 처리할 토큰 수)
            "use_mmap": True,  # 메모리 맵핑 사용 여부 (모델을 디스크에서 직접 읽기)
            "use_mlock": False,  # 메모리 고정 사용 여부 (메모리를 swap 방지)
            "mul_mat_q": True,  # 양자화된 행렬 곱셈 사용 여부
            "numa": False,  # NUMA 아키텍처 지원 여부
            "n_gpu_layers": n_gpu_layers,  # GPU에서 실행할 레이어 수
            "rope_freq_base": 500000,  # RoPE(회전 위치 임베딩) 주파수 기본값
            "tensor_split": None,  # 텐서 분할 설정 (None이면 기본값 사용)
            "rope_freq_scale": 1.0,  # RoPE 주파수 스케일
            "offload_kqv": True,  # KQV 텐서를 GPU로 오프로드 할지 여부
            "split_mode": 1,  # 텐서 분할 모드
            "flash_attn": False,  # Flash Attention 사용 여부
        }  

        self.model = Llama(**params)
        self.initialized = True

    def release(self):
        if self.model:
            del self.model
            self.model = None
            self.initialized = False
            gc.collect()

    def encode(self, string):
        if type(string) is str:
            string = string.encode()
        return self.model.tokenize(string)

    def decode(self, ids, **kwargs):
        return self.model.detokenize(ids).decode('utf-8')

    def create_completion(self, *args, **kwargs):
        gc.collect()
        prompt = kwargs.get('prompt')
        temperature = kwargs.get('temperature', 0)  # 기본값은 0
        
        prompt = prompt if type(prompt) is str else prompt.decode()
        prompt = self.encode(prompt)
        prompt_length = 8192 - 1024
        prompt = prompt[-prompt_length:]
        prompt = self.decode(prompt)
        
        
        output = self.model.create_completion(
            max_tokens=1024,
            prompt=prompt,
            temperature=temperature,
        )
        return output

    def generate(self, prompt, is_regenerate, state=None, callback=None):
        temperature = 0.2
        if is_regenerate:
            temperature = 0.7

        prompt = prompt if type(prompt) is str else prompt.decode()
        prompt = self.encode(prompt)
        prompt_length = 8192 - 1024
        prompt = prompt[-prompt_length:]
        prompt = self.decode(prompt)
        
        completion_chunks = self.model.create_completion(
            max_tokens=1024,
            prompt=prompt,
            temperature=temperature,
            stream=True
        )

        output = ""
        for completion_chunk in completion_chunks:
            text = completion_chunk['choices'][0]['text']
            output += text
            if callback:
                callback(text)
        return output

    def generate_with_streaming(self, *args, **kwargs):
        gc.collect()
        with Iteratorize(self.generate, args, kwargs, callback=None) as generator:
            reply = ''
            for token in generator:
                reply += token
                yield reply
                
    def generate_web(self, prompt, state=None, callback=None):
        # LogitsProcessorList = llama_cpp.LogitsProcessorList
        prompt = prompt if type(prompt) is str else prompt.decode()

        # Handle truncation
        prompt = self.encode(prompt)
        # prompt = prompt[-get_max_prompt_length(state):]
        prompt_length = 2048-512  # -get_max_prompt_length(state)
        prompt = prompt[-prompt_length:]
        prompt = self.decode(prompt)
        
        # print('prompt', prompt)

        # self.load_grammar(state['grammar_string'])  # 일단 빈값인것 같아 생략
        # logit_processors = LogitsProcessorList()
        # if state['ban_eos_token']:  # False
        #     logit_processors.append(partial(ban_eos_logits_processor, self.model.token_eos()))

        # if state['custom_token_bans']:  # ''
        #     to_ban = [int(x) for x in state['custom_token_bans'].split(',')]
        #     if len(to_ban) > 0:
        #         logit_processors.append(partial(custom_token_ban_logits_processor, to_ban))

        state = {
            "max_new_tokens": 512,
            "auto_max_new_tokens": False,
            "max_tokens_second": 0,
            "max_updates_second": 0,
            "prompt_lookup_num_tokens": 0,
            "seed": -1,
            "temperature": 1,
            "temperature_last": False,
            "dynamic_temperature": False,
            "dynatemp_low": 1,
            "dynatemp_high": 1,
            "dynatemp_exponent": 1,
            "smoothing_factor": 0,
            "smoothing_curve": 1,
            "top_p": 1,
            "min_p": 0.05,
            "top_k": 0,
            "typical_p": 1,
            "epsilon_cutoff": 0,
            "eta_cutoff": 0,
            "repetition_penalty": 1,
            "presence_penalty": 0,
            "frequency_penalty": 0,
            "repetition_penalty_range": 1024,
            "encoder_repetition_penalty": 1,
            "no_repeat_ngram_size": 0,
            "do_sample": True,
            "penalty_alpha": 0,
            "mirostat_mode": 0,
            "mirostat_tau": 5,
            "mirostat_eta": 0.1,
            "grammar_string": "",
            "negative_prompt": "",
            "guidance_scale": 1,
            "add_bos_token": True,
            "ban_eos_token": False,
            "custom_token_bans": "",
            "sampler_priority": "temperature\ndynamic_temperature\nquadratic_sampling\ntop_k\ntop_p\ntypical_p\nepsilon_cutoff\neta_cutoff\ntfs\ntop_a\nmin_p\nmirostat",
            "truncation_length": 2048,
            "custom_stopping_strings": "",
            "skip_special_tokens": True,
            "stream": True,
            "tfs": 1,
            "top_a": 0,
            "textbox": "안녕?",
            "start_with": "",
            "character_menu": "Assistant",
            "history": {
                "visible": [
                    ["gogog", "*Is typing*"],
                    [
                        "sleepy",
                        "Alright, let&#x27;s take a moment to calm down and help you relax. I have a few guided meditations and sleep stories that can help you unwind. \n&#x27;Guided Meditation: Relaxation and Breathing&#x27; is a simple yet effective guided meditation that helps you to relax your body and calm your mind. It also teaches you breathing techniques to reduce stress and anxiety. \n&#x27;Bedtime Story: The Forest of Dreams&#x27; is a sleep story that takes you on a journey through a magical forest. It helps you to fall asleep and relax with a soothing, gentle story. \n&#x27;Guided Meditation: Sleep and Serenity&#x27; is another guided meditation that is designed to help you fall asleep and improve the quality of your sleep. It guides you through a relaxation process to ease your mind and body into a deep, peaceful sleep.\nWhich one would you like to try?",
                    ],
                ],
                "internal": [
                    ["gogog", ""],
                    [
                        "sleepy",
                        "Alright, let's take a moment to calm down and help you relax. I have a few guided meditations and sleep stories that can help you unwind. \n'Guided Meditation: Relaxation and Breathing' is a simple yet effective guided meditation that helps you to relax your body and calm your mind. It also teaches you breathing techniques to reduce stress and anxiety. \n'Bedtime Story: The Forest of Dreams' is a sleep story that takes you on a journey through a magical forest. It helps you to fall asleep and relax with a soothing, gentle story. \n'Guided Meditation: Sleep and Serenity' is another guided meditation that is designed to help you fall asleep and improve the quality of your sleep. It guides you through a relaxation process to ease your mind and body into a deep, peaceful sleep.\nWhich one would you like to try?",
                    ],
                ],
            },
            "name1": "You",
            "user_bio": "",
            "name2": "AI",
            "greeting": "How can I help you today?",
            "context": "The following is a conversation with an AI Large Language Model. The AI has been trained to answer questions, provide recommendations, and help with decision making. The AI follows user requests. The AI thinks outside the box.",
            "mode": "chat",
            "custom_system_message": "",
            "instruction_template_str": "{%- set ns = namespace(found=false) -%}{%- for message in messages -%}{%- if message['role'] == 'system' -%}{%- set ns.found = true -%}{%- endif -%}{%- endfor -%}{%- for message in messages %}{%- if message['role'] == 'system' -%}{{- '<|im_start|>system\n' + message['content'].rstrip() + '<|im_end|>\n' -}}{%- else -%}{%- if message['role'] == 'user' -%}{{-'<|im_start|>user\n' + message['content'].rstrip() + '<|im_end|>\n'-}}{%- else -%}{{-'<|im_start|>assistant\n' + message['content'] + '<|im_end|>\n' -}}{%- endif -%}{%- endif -%}{%- endfor -%}{%- if add_generation_prompt -%}{{-'<|im_start|>assistant\n'-}}{%- endif -%}",
            "chat_template_str": "{%- for message in messages %}\n    {%- if message['role'] == 'system' -%}\n        {%- if message['content'] -%}\n            {{- message['content'] + '\\n\\n' -}}\n        {%- endif -%}\n        {%- if user_bio -%}\n            {{- user_bio + '\\n\\n' -}}\n        {%- endif -%}\n    {%- else -%}\n        {%- if message['role'] == 'user' -%}\n            {{- name1 + ': ' + message['content'] + '\\n'-}}\n        {%- else -%}\n            {{- name2 + ': ' + message['content'] + '\\n' -}}\n        {%- endif -%}\n    {%- endif -%}\n{%- endfor -%}",
            "chat_style": "cai-chat",
            "chat-instruct_command": 'Continue the chat dialogue below. Write a single reply for the character "<|character|>".\n\n<|prompt|>',
            "textbox-notebook": "Common sense questions and answers\n\nQuestion: \nFactual answer:",
            "textbox-default": "Common sense questions and answers\n\nQuestion: \nFactual answer:",
            "output_textbox": "",
            "prompt_menu-default": "QA",
            "prompt_menu-notebook": "QA",
            "loader": "llama.cpp",
            "filter_by_loader": "llama.cpp",
            "cpu_memory": 0,
            "auto_devices": False,
            "disk": False,
            "cpu": True,
            "bf16": False,
            "load_in_8bit": False,
            "trust_remote_code": False,
            "no_use_fast": False,
            "use_flash_attention_2": False,
            "load_in_4bit": False,
            "compute_dtype": "float16",
            "quant_type": "nf4",
            "use_double_quant": False,
            "wbits": "None",
            "groupsize": "None",
            "model_type": "llama",
            "pre_layer": 0,
            "triton": False,
            "desc_act": False,
            "no_inject_fused_attention": False,
            "no_inject_fused_mlp": False,
            "no_use_cuda_fp16": False,
            "disable_exllama": False,
            "disable_exllamav2": False,
            "cfg_cache": False,
            "no_flash_attn": False,
            "num_experts_per_token": 2,
            "cache_8bit": False,
            "cache_4bit": False,
            "autosplit": False,
            "threads": 0,
            "threads_batch": 0,
            "n_batch": 512,
            "no_mmap": False,
            "mlock": False,
            "no_mul_mat_q": False,
            "n_gpu_layers": 33,
            "tensor_split": "",
            "n_ctx": 8192,
            "gpu_split": "",
            "max_seq_len": 2048,
            "compress_pos_emb": 1,
            "alpha_value": 1,
            "rope_freq_base": 500000,
            "numa": False,
            "logits_all": False,
            "no_offload_kqv": False,
            "row_split": False,
            "tensorcores": False,
            "flash-attn": False,
            "streaming_llm": False,
            "attention_sink_size": 5,
            "hqq_backend": "PYTORCH_COMPILE",
        }

        completion_chunks = self.model.create_completion(
            prompt=prompt,  # 입력 프롬프트 텍스트
            max_tokens=state['max_new_tokens'],  # 생성할 최대 토큰 수
            temperature=state['temperature'],  # 출력의 다양성을 제어하는 온도 설정
            # temperature=0,  # 고정된 온도를 사용하려면 주석을 해제하고 사용
            top_p=state['top_p'],  # 누적 확률에 기반한 샘플링 임계값
            min_p=state['min_p'],  # 샘플링할 최소 확률
            typical_p=state['typical_p'],  # 전형적 확률 샘플링 임계값
            frequency_penalty=state['frequency_penalty'],  # 빈도 페널티 (자주 등장하는 단어에 페널티 부여)
            presence_penalty=state['presence_penalty'],  # 존재 페널티 (이미 등장한 단어에 페널티 부여)
            repeat_penalty=state['repetition_penalty'],  # 반복 페널티 (반복 단어에 페널티 부여)
            top_k=state['top_k'],  # 상위 k개의 토큰만 고려하는 샘플링
            stream=True,  # 스트리밍 모드 사용 여부 (생성된 텍스트를 실시간으로 반환)
            seed=int(state['seed']) if state['seed'] != -1 else None,  # 시드 값 (재현성을 위해 사용, -1이면 무작위 시드)
            tfs_z=state['tfs'],  # 토큰 필터링 스케일
            mirostat_mode=int(state['mirostat_mode']),  # Mirostat 모드 설정
            mirostat_tau=state['mirostat_tau'],  # Mirostat 타우 값 (생성된 텍스트의 엔트로피 조절)
            mirostat_eta=state['mirostat_eta'],  # Mirostat 에타 값 (학습률 조절)
            # logits_processor=logit_processors  # 로그잇 프로세서 사용 시 주석 해제
            # grammar=self.grammar  # 문법 적용 시 주석 해제
        )
        
        output = ""
        for completion_chunk in completion_chunks:
            # if shared.stop_everything:
            #     break

            text = completion_chunk['choices'][0]['text']
            output += text
            if callback:
                callback(text)

        return output

    def generate_with_streaming_web(self, *args, **kwargs):
        gc.collect()
        with Iteratorize(self.generate_web, args, kwargs, callback=None) as generator:
            reply = ''
            for token in generator:
                reply += token
                yield reply

class Iteratorize:
    """
    Transforms a function that takes a callback
    into a lazy iterator (generator).

    Adapted from: https://stackoverflow.com/a/9969000
    """

    def __init__(self, func, args=None, kwargs=None, callback=None):
        self.mfunc = func
        self.c_callback = callback
        self.q = Queue()
        self.sentinel = object()
        self.args = args or []
        self.kwargs = kwargs or {}
        self.stop_now = False

        def _callback(val):
            if self.stop_now: # or shared.stop_everything:
                raise StopNowException
            self.q.put(val)

        def gentask():
            try:
                ret = self.mfunc(callback=_callback, *args, **self.kwargs)
            except StopNowException:
                pass
            except:
                traceback.print_exc()
                pass

            # clear_torch_cache()
            self.q.put(self.sentinel)
            if self.c_callback:
                self.c_callback(ret)

        self.thread = Thread(target=gentask)
        self.thread.start()

    def __iter__(self):
        return self

    def __next__(self):
        obj = self.q.get(True, None)
        if obj is self.sentinel:
            raise StopIteration
        else:
            return obj

    def __del__(self):
        pass
        # clear_torch_cache()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop_now = True
        # clear_torch_cache()

class StopNowException(Exception):
    pass

def check_llm():
    try:
        llm = LlamaCppModel()
        return llm.initialized
    except:
        return False

def get_llm():
    llm = LlamaCppModel()
    if not llm.initialized:
        llm.from_pretrained('./model/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf')
    return llm

def release():
    llm = LlamaCppModel()
    if llm.initialized:
        llm.release()

################################################################ Vision
import os
from PIL import Image
from transformers import AutoProcessor, AutoModelForCausalLM 

from unittest.mock import patch
from transformers.dynamic_module_utils import get_imports

# VisionModel 싱글톤 클래스
class VisionModel(metaclass=SingletonMeta):
    def __init__(self):
        self.model = None
        self.initialized = False

    def __del__(self):
        del self.model

    def from_pretrained(self, model_name):
        with patch("transformers.dynamic_module_utils.get_imports", self.fixed_get_imports):  # Workaround for unnecessary flash_attn requirement
            self.model = AutoModelForCausalLM.from_pretrained(model_name, trust_remote_code=True, cache_dir='./model/', local_files_only=True)
        self.initialized = True

    @staticmethod
    def fixed_get_imports(filename):
        if not str(filename).endswith("modeling_florence2.py"):
            return get_imports(filename)
        imports = get_imports(filename)
        imports.remove("flash_attn")
        return imports

    def release(self):
        self.model = None
        self.initialized = False

# VisionProcessor 싱글톤 클래스
class VisionProcessor(metaclass=SingletonMeta):
    def __init__(self):
        self.processor = None
        self.initialized = False

    def __del__(self):
        del self.processor

    def from_pretrained(self, processor_name):
        self.processor = AutoProcessor.from_pretrained(processor_name, trust_remote_code=True, cache_dir='./model/', local_files_only=True)
        self.initialized = True

    def release(self):
        self.processor = None
        self.initialized = False

# getter 함수
def get_vision_model():
    vision_model = VisionModel()
    if not vision_model.initialized:
        vision_model.from_pretrained("microsoft/Florence-2-base")
    return vision_model

def get_vision_processor():
    vision_processor = VisionProcessor()
    if not vision_processor.initialized:
        vision_processor.from_pretrained("microsoft/Florence-2-base")
    return vision_processor

# 리소스 해제 함수
def release_vision_resources():
    vision_model = VisionModel()
    if vision_model.initialized:
        vision_model.release()
        VisionModel.release_instance()

    vision_processor = VisionProcessor()
    if vision_processor.initialized:
        vision_processor.release()
        VisionProcessor.release_instance()