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