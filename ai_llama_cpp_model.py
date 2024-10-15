### CPU용 공용 모델로더
from queue import Queue
import llama_cpp
from threading import Thread
import traceback
import gc

class LlamaCppModel:
    def __init__(self):
        self.initialized = False
        self.grammar_string = ''
        self.grammar = None

    def __del__(self):
        del self.model

    @classmethod
    def from_pretrained(self, path):

        Llama = llama_cpp.Llama
        LlamaCache = llama_cpp.LlamaCache

        cache_capacity = 0
        tensor_split_list = None

        params = {
            "model_path": "./model/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",  # 모델 파일 경로
            "n_ctx": 8192,  # 컨텍스트 길이 (최대 토큰 수)
            "n_threads": None,  # 모델 로딩 및 실행 시 사용할 스레드 수 (None이면 기본값 사용)
            "n_threads_batch": None,  # 배치 처리 시 사용할 스레드 수 (None이면 기본값 사용)
            "n_batch": 512,  # 배치 크기 (한 번에 처리할 토큰 수)
            "use_mmap": True,  # 메모리 맵핑 사용 여부 (모델을 디스크에서 직접 읽기)
            "use_mlock": False,  # 메모리 고정 사용 여부 (메모리를 swap 방지)
            "mul_mat_q": True,  # 양자화된 행렬 곱셈 사용 여부
            "numa": False,  # NUMA 아키텍처 지원 여부
            "n_gpu_layers": 0,  # GPU에서 실행할 레이어 수
            "rope_freq_base": 500000,  # RoPE(회전 위치 임베딩) 주파수 기본값
            "tensor_split": None,  # 텐서 분할 설정 (None이면 기본값 사용)
            "rope_freq_scale": 1.0,  # RoPE 주파수 스케일
            "offload_kqv": True,  # KQV 텐서를 GPU로 오프로드 할지 여부
            "split_mode": 1,  # 텐서 분할 모드
            "flash_attn": False,  # Flash Attention 사용 여부
            "return_direct": True
        }        

        self.model = Llama(**params)

        return self, self

    def encode(self, string):
        if type(string) is str:
            string = string.encode()

        return self.model.tokenize(string)

    def decode(self, ids, **kwargs):
        return self.model.detokenize(ids).decode('utf-8')

    def generate(self, prompt, is_regenerate, state=None, callback=None):
        temperature = 0.2
        if is_regenerate:
            temperature = 0.7
        # LogitsProcessorList = llama_cpp.LogitsProcessorList
        prompt = prompt if type(prompt) is str else prompt.decode()

        # Handle truncation
        prompt = self.encode(prompt)
        # prompt = prompt[-get_max_prompt_length(state):]
        prompt_length = 2048-512  # -get_max_prompt_length(state)
        prompt = prompt[-prompt_length:]
        prompt = self.decode(prompt)
        
        completion_chunks = self.model.create_completion(
        max_tokens=2048, #   # 생성할 최대 토큰 수, infinity 0
        prompt=prompt,
        temperature=temperature,
        stream=True
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

    def generate_with_streaming(self, *args, **kwargs):
        gc.collect()
        with Iteratorize(self.generate, args, kwargs, callback=None) as generator:
            reply = ''
            for token in generator:
                reply += token
                yield reply

   
class StopNowException(Exception):
    pass 
    
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
    