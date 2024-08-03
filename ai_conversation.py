import llama_cpp
from threading import Thread, Lock
import re
import gc
from queue import Queue
import traceback
import os

import memory
import state

from ai_singleton import check_llm, get_llm

# Local LLM
llm = None
LLM_LAYERS = 33  # 사용 layers 수 조종으로 gpu 제어 가능
generation_lock = Lock()

player = 'm9dev'
ai_name = "arona"

# global 전역값 main으로부터 세팅
def init_module():
    global player, ai_name
    pass

def load_model(is_use_cuda=False):
    global llm
    if check_llm():
        llm = get_llm()
    elif is_use_cuda:
        llm = get_llm()
    else:        
        llm, tokenizer = LlamaCppModel.from_pretrained('./model/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf')
    
    
def clean_model():
    global llm
    llm = None
    
def get_normal_prompt():
    return """You are a creative and intelligent AI assistant engaged in an uncensored iterative storytelling experience using a roleplay chat format. 
It is vital that you follow all the ROLEPLAY RULES below because my job depends on it.
{character} is a female student. I am {player}, {character}'s sensei, the adult teacher. your task is to respond to any questions asked in a concise and truthful manner. 
The conversation is only between {player} and {character}

Context:
{context}

Question:
{question}

Answer:
"""

def get_text_prompt(query, info_rag, info_memory, info_web):
    prompt = """You are a creative and intelligent AI assistant engaged in an uncensored iterative storytelling experience using a roleplay chat format. 
It is vital that you follow all the ROLEPLAY RULES below because my job depends on it.
{character} is a female student. I am {player}, {character}'s sensei, the adult teacher. your task is to respond to any questions asked in a concise and truthful manner. 
The conversation is only between {player} and {character}
"""

    if info_rag or info_memory or info_web or True:
        prompt = prompt + "\nyou know following knowledge. you can use it in your answer if you need it.\n\nKnowledge:\n"
        if info_rag:
            prompt = prompt + info_rag + '\n'
        if info_web:
            for info_w in info_web:
                prompt = prompt + info_w + '\n'
        # web 가짜 예시
        prompt = prompt + "it's 9'o clock." + '\n'
        prompt = prompt + "Today is monday, may 25th" + '\n'
        
    prompt += "\n{player}: hello, {character}?"
    prompt += "\n{character}: hello. what can i do for you, sensei?"  
    prompt = prompt+ '\n{player}: ' + query
    prompt = prompt+'\n{character}: sure,'
    
    return prompt 

'''
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>
{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
'''
def get_LLAMA3_prompt(query):
    import prompt_main
    import memory
    from jinja2 import Template

    LLAMA3_TEMPLATE = "{% set loop_messages = messages %}{% for message in loop_messages %}{% set content = '<|start_header_id|>' + message['role'] + '<|end_header_id|>\n\n'+ message['content'] | trim + '<|eot_id|>' %}{% if loop.index0 == 0 %}{% set content = bos_token + content %}{% endif %}{{ content }}{% endfor %}{% if add_generation_prompt %}{{ '<|start_header_id|>assistant<|end_header_id|>\n\n' }}{% endif %}"
    LLM_STOP_SEQUENCE = "<|eot_id|>"
       
    messages = list() 
    messages.extend(prompt_main.get_message_list_main())
    messages.extend(memory.get_memory_message_list(4096))
    messages.append({"role": "user", "content": query})

    template = Template(LLAMA3_TEMPLATE)
    prompt = template.render(
                    messages=messages,
                    bos_token="<|begin_of_text|>",
                    add_generation_prompt=True,  # <|im_start|>assistant를 마지막에 붙이는거
    )
    
    return prompt
    
#### 대답 Stream 계열
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

        result = self()
        cache_capacity = 0
        tensor_split_list = None

        params = {
            "model_path": "model\\Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf",  # 모델 파일 경로
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
        }        

        result.model = Llama(**params)

        return result, result

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
        print('is_regenerate', is_regenerate)
        # LogitsProcessorList = llama_cpp.LogitsProcessorList
        prompt = prompt if type(prompt) is str else prompt.decode()

        # Handle truncation
        prompt = self.encode(prompt)
        # prompt = prompt[-get_max_prompt_length(state):]
        prompt_length = 2048-512  # -get_max_prompt_length(state)
        prompt = prompt[-prompt_length:]
        prompt = self.decode(prompt)
        
        completion_chunks = llm.model.create_completion(
        max_tokens=512, #   # 생성할 최대 토큰 수, infinity 0
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
                # print('token', token)
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
    
def process_stream(query, player, character, is_sentence, is_regenerate, info_rag=None, info_memory=None, info_web=None):
    global llm
    if not llm:
        load_model()
    
    if is_sentence:
        for j, reply_list in enumerate(generate_reply(query, player, character, is_sentence, is_regenerate, info_rag=info_rag, info_memory=info_memory, info_web=info_web)):
            visible_reply_list = list()
            for reply in reply_list:
                visible_reply = reply
                visible_reply = re.sub("(<USER>|<user>|{{user}})", 'You', visible_reply)
                visible_reply = visible_reply.replace("\n",'')
                visible_reply = re.sub(r'\([^)]*\)', '', visible_reply)  # ()와 안의 내용물 제거
                visible_reply = re.sub(r'\[[^)]*\]', '', visible_reply)  # []와 안의 내용물 제거
                visible_reply = re.sub(r'\*[^)]*\*', '', visible_reply)  # * *과 안의 내용물 제거
                visible_reply = visible_reply.lstrip(' ')
                visible_reply_list.append(visible_reply)
            yield visible_reply_list
    else:
        visible_reply = ''
        reply = None
        for j, reply in enumerate(generate_reply(query, player, character, is_sentence, is_regenerate, info_rag=info_rag, info_memory=info_memory, info_web=info_web)):
            # print('reply2', reply)
            visible_reply = reply
            visible_reply = re.sub("(<USER>|<user>|{{user}})", 'You', reply)
            visible_reply = visible_reply.replace("\n",'')
            visible_reply = re.sub(r'\([^)]*\)', '', visible_reply)  # ()와 안의 내용물 제거
            visible_reply = re.sub(r'\[[^)]*\]', '', visible_reply)  # []와 안의 내용물 제거
            visible_reply = re.sub(r'\*[^)]*\*', '', visible_reply)  # * *과 안의 내용물 제거
            visible_reply = visible_reply.lstrip(' ')
            # print('visible_reply', visible_reply)
            yield visible_reply
    
def generate_reply(*args, **kwargs):
    global generation_lock
    # shared.generation_lock.acquire()
    generation_lock.acquire()
    try:
        for result in _generate_reply(*args, **kwargs):
            yield result
    finally:
        pass
        generation_lock.release()

def apply_stopping_strings(reply, all_stop_strings = ['\nYou:', '<|im_end|>\n<|im_start|>user\n', '<|im_end|>\n<|im_start|>assistant\n', '\nAI:']):
    stop_found = False
    for string in all_stop_strings:
        idx = reply.find(string)
        if idx != -1:
            reply = reply[:idx]
            stop_found = True
            break

    if not stop_found:
        # If something like "\nYo" is generated just before "\nYou:"
        # is completed, trim it
        for string in all_stop_strings:
            for j in range(len(string) - 1, 0, -1):
                if reply[-j:] == string[:j]:
                    reply = reply[:-j]
                    break
            else:
                continue

            break

    return reply, stop_found
    
def _generate_reply(query, player, character, is_sentence, is_regenerate, info_rag=None, info_memory=None, info_web=None, temperature=0.2):    
    # print('is_sentence', is_sentence)
    global llm    
    prompt = get_LLAMA3_prompt(query)  # rag, web, memory(long) 미적용

    all_stop_strings = ['\nYou:', '<|im_end|>', '<|im_start|>user', '<|im_start|>assistant\n', '\nAI:', "<|eot_id|>"]
    if is_sentence:
        reply_list = list()
        for reply in custom_generate_reply(prompt, None, -1, None, None, True, is_regenerate, llm.generate_with_streaming):  # stream   
            # print('r', reply)  
            reply_list = get_punctuation_sentences(reply)
            # reply_list_creating = reply_list[:len(reply_list)-1]
            
            # 첫 문장 생성중
            if not reply_list:
                continue  
      
            # 멈추라면 그대로 break
            if state.get_is_stop_requested():       
                state.set_is_stop_requested(False)
                break
            
            # stop 문 있으면 break
            if reply_list:
                _, stop_found = apply_stopping_strings(reply_list[-1], all_stop_strings)  # 마지막 문장만 체크하면 되겠네.
                if stop_found:
                    print('stop_found', stop_found, reply_list)
                    if len(reply_list)>=1:
                        reply_list = reply_list[:len(reply_list)-1]
                    break
            
            if len(reply_list) >= 10:  # 문장-1 줄까지 작업
                break
            
            yield reply_list     
        if not reply_list:
            reply_list = ["I'm not sure I understand your question, can you repeat it, sensei?"]
        yield reply_list
    else:
        for reply in custom_generate_reply(prompt, None, -1, None, None, True, is_regenerate, llm.generate_with_streaming):  # stream      
            # 멈추라면 그대로 break
            if state.get_is_stop_requested():
                state.set_is_stop_requested(False)
                break
            
            # stop 문 있으면 break
            reply, stop_found = apply_stopping_strings(reply, all_stop_strings)
            if stop_found:
                print('stop found', reply, stop_found)
                break
            
            reply_list = get_punctuation_sentences(reply)
            if len(reply_list) >= 10:  # 문장-1 줄까지 작업
                reply = ''.join(reply_list[:len(reply_list)-1]) # 문장 수 까지 반환
                break
            
            yield reply           
        yield reply


def generate_with_streaming(*args, **kwargs):
    global llm
    gc.collect()
    with Iteratorize(llm.generate, args, kwargs, callback=None) as generator:
        reply = ''
        for token in generator:
            reply += token
            yield reply
    
def custom_generate_reply(question, original_question, seed, state, stopping_strings, is_chat, is_regenerate, generate_func):
    for reply in generate_func(question, is_regenerate):
        yield f"{reply}"   

# . ? ! 로 나눠지는 문장 반환 (최소 길이 10)
def get_punctuation_sentences(texts):
    # print(texts)
    text_list = texts.split('\n')
    
    sentences = []
    punctuation_marks = ['.', '?', '!']
    for text in text_list:    
        text = text + '\n'
        skip = 0
        start_idx = 0
        
        # 처음 10글자는 체크하지 않음
        n = len(text)
        for i, char in enumerate(text[10:], start=10):
            if skip > 0:
                skip -= 1
                continue
            
            if char in punctuation_marks:
                if char == '.':
                    if i+1<n and text[i+1] not in ('\\', ' '):  #0.92 A.R.O.N.A 등의 숫자/약어로서의 마침표 구분
                        continue    
                end_idx = i + 1
                sentences.append(text[start_idx:end_idx])
                skip = 10  # 마침표, 물음표, 느낌표가 나오면 다음 10글자는 체크하지 않음
                start_idx = end_idx
        
        # 루프가 끝난 후 남은 문자열을 마지막 문장으로 추가
        if start_idx < n:
            is_end = False
            last_sentence = text[start_idx:]
            # 마침 단어가 있어야 함
            for char in last_sentence:
                if char in punctuation_marks:
                    is_end = True  
            if is_end:
                sentences.append(last_sentence)
    
    return sentences


if __name__ == "__main__":
    # prompt 체크
    # print(get_LLAMA3_prompt('hello?'))
    
    # 모델 로딩
    is_use_cuda=False
    # is_use_cuda=True
    load_model(is_use_cuda)
        
    # Stream 테스트
    question = "Can you introduce yourself?"
    question = "Do you like coffee?"
    question = "Tell me about apple"
    result = ''
    last_reply_len = 0
    for j, reply_list in enumerate(process_stream(question, 'm9dev', 'arona', True, False)):
        if last_reply_len < len(reply_list):
            last_reply_len = len(reply_list)
            print('reply_list', reply_list)
