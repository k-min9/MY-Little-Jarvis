import llama_cpp
import os
from ai_web_search_module import LangchainCompressor, langchain_search_duckduckgo, Generator, get_webpage_content
import html
import re
import gc
from datetime import datetime
from queue import Queue
import traceback
from threading import Thread, Lock
import state as st

from ai_singleton import check_llm, get_llm

llm = None
langchain_compressor = None
generation_lock = Lock()

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

    def generate(self, prompt, state=None, callback=None):
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
        with Iteratorize(self.generate, args, kwargs, callback=None) as generator:
            reply = ''
            for token in generator:
                reply += token
                yield reply

def load_model(is_use_cuda=False):
    global langchain_compressor, llm
    start_compressor()
    
    global llm
    if check_llm():
        llm = get_llm()
    elif is_use_cuda:
        llm = get_llm()
    else:
        llm, tokenizer = LlamaCppModel.from_pretrained('./model/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf')

# stream 밖에 없기 때문에 그대로 is_sentence 적용
def process(query):    
    global llm 
    if not llm:
        load_model()
    for j, reply_list in enumerate(generate_reply(query)):
        visible_reply_list = list()
        for reply in reply_list:
            visible_reply = reply
            visible_reply = re.sub("(<USER>|<user>|{{user}})", 'You', visible_reply)
            # visible_reply = visible_reply.replace("\n",'')  # 음성쪽은 제거해야함 (그쪽에 추가)
            visible_reply = re.sub(r'\([^)]*\)', '', visible_reply)  # ()와 안의 내용물 제거
            visible_reply = re.sub(r'\[[^)]*\]', '', visible_reply)  # []와 안의 내용물 제거
            visible_reply = re.sub(r'\*[^)]*\*', '', visible_reply)  # * *과 안의 내용물 제거
            visible_reply = visible_reply.lstrip(' ')
            visible_reply_list.append(visible_reply)
        print('visible_reply_list', visible_reply_list)
        yield visible_reply_list

# Loading시 시작해야함, 원본 seach LLM extension script.py의 toggle_extension
def start_compressor():
    global langchain_compressor#, custom_system_message_filename
    extension_path = os.path.dirname(os.path.abspath(__file__))
    langchain_compressor = LangchainCompressor(device="cpu",
                                                keyword_retriever="bm25", #  params["keyword retriever"],
                                                model_cache_dir=os.path.join(extension_path, "model"))
    compressor_model = langchain_compressor.embeddings.client
    compressor_model.to(compressor_model._target_device)
    
    print('os.path.join(extension_path, "model")', os.path.join(extension_path, "model"))


# From LLM websearch  
# generate_func 추가
def custom_generate_reply(question, original_question, seed, state, stopping_strings, is_chat, generate_func):
    """
    Overrides the main text generation function.
    :return:
    """
    params = {
    "display_name": "LLM Web Search",
    "is_tab": True,
    "enable": True,
    "search results per query": 5,
    "langchain similarity score threshold": 0.5,
    "instant answers": True,
    "regular search results": True,
    "search command regex": "",
    "default search command regex": r"Search_web\(\"(.*)\"\)",
    "open url command regex": "",
    "default open url command regex": r"Open_url\(\"(.*)\"\)",
    "display search results in chat": True,
    "display extracted URL content in chat": True,
    "searxng url": "",
    "cpu only": True,
    "chunk size": 500,
    "duckduckgo results per query": 10,
    "append current datetime": False,
    "default system prompt filename": None,
    "force search prefix": "Search_web",
    "ensemble weighting": 0.5,
    "keyword retriever": "bm25",
    "splade batch size": 2,
    "chunking method": "character-based",
    "chunker breakpoint_threshold_amount": 30
    }
    
    global langchain_compressor
    # if shared.model.__class__.__name__ in ['LlamaCppModel', 'RWKVModel', 'ExllamaModel', 'Exllamav2Model',
    #                                        'CtransformersModel']:
    #     generate_func = generate_reply_custom 
    #     print('generate_func', 'generate_reply_custom')  ### 이거
    # else:
    #     generate_func = generate_reply_HF
    #     print('generate_func', 'generate_reply_HF')

    # if not params['enable']:  # 당근 enable이니까 여길 왔지
    #     for reply in generate_func(question, original_question, seed, state, stopping_strings, is_chat=is_chat):
    #         yield reply
    #     return
    
    generate_func = generate_func

    web_search = False
    read_webpage = False
    # max_search_results = int(params["search results per query"])
    max_search_results = 4
    # instant_answers = params["instant answers"]
    instant_answers = True
    # regular_search_results = params["regular search results"]  # 일단 True인데 처음부터 비활성화

    # langchain_compressor.num_results = int(params["duckduckgo results per query"])
    langchain_compressor.num_results = 10
    langchain_compressor.similarity_threshold = params["langchain similarity score threshold"]
    langchain_compressor.chunk_size = params["chunk size"]
    langchain_compressor.ensemble_weighting = params["ensemble weighting"]
    langchain_compressor.splade_batch_size = params["splade batch size"]
    langchain_compressor.chunking_method = params["chunking method"]
    langchain_compressor.chunker_breakpoint_threshold_amount = params["chunker breakpoint_threshold_amount"]

    search_command_regex = params["search command regex"]
    open_url_command_regex = params["open url command regex"]
    searxng_url = params["searxng url"]  # ""
    display_search_results = params["display search results in chat"]
    display_webpage_content = params["display extracted URL content in chat"]

    if search_command_regex == "":
        search_command_regex = params["default search command regex"]
    if open_url_command_regex == "":
        open_url_command_regex = params["default open url command regex"]

    import re
    compiled_search_command_regex = re.compile(search_command_regex)
    compiled_open_url_command_regex = re.compile(open_url_command_regex)

    # print('force_search', force_search)
    print('compiled_search_command_regex', compiled_search_command_regex)
    print('compiled_open_url_command_regex', compiled_open_url_command_regex)
    # force_search = True
    # if force_search:
    #     question += f" {params['force search prefix']}"
    question += " Search_web"

    reply = None
    # for reply in generate_func(question, original_question, seed, state, stopping_strings, is_chat=is_chat):
    for reply in generate_func(question):

        # if force_search:
        #     print('reply + force', reply)
        #     reply = params["force search prefix"] + reply
        reply = params["force search prefix"] + reply
        # print(reply)  # Search_web("Disney's history and publishing

        search_re_match = compiled_search_command_regex.search(reply)
        # print('search_re_match', reply)
        if search_re_match is not None:
            yield reply
            original_model_reply = reply
            web_search = True
            search_term = search_re_match.group(1)
            print(f"LLM_Web_search | Searching for {search_term}")
            reply += "\n```plaintext"
            reply += "\nSearch tool:\n"
            # print('searxng_url', searxng_url)  # 비어있음 여기 안탐
            # if searxng_url == "":                
            #     search_generator = Generator(langchain_search_duckduckgo(search_term,
            #                                                              langchain_compressor,
            #                                                              max_search_results,
            #                                                              instant_answers))
            #     print('search_generator', search_generator)
            # else:
            #     search_generator = Generator(langchain_search_searxng(search_term,
            #                                                           searxng_url,
            #                                                           langchain_compressor,
            #                                                           max_search_results))
            print('search_term', search_term)
            search_generator = Generator(langchain_search_duckduckgo(search_term,
                                                                        langchain_compressor,
                                                                        max_search_results,
                                                                        instant_answers)) 
            print('gen')
            try:
                for status_message in search_generator:
                    print('status_message', status_message)
                    yield original_model_reply + f"\n*{status_message}*"
                search_results = search_generator.value
                print('search_results', search_results)
            except Exception as exc:
                exception_message = str(exc)
                reply += f"The search tool encountered an error: {exception_message}"
                print(f'LLM_Web_search | {search_term} generated an exception: {exception_message}')
            else:
                if search_results != "":
                    reply += search_results
                    print('search_results_reply', search_results)
                else:
                    reply += f"\nThe search tool did not return any results."
            reply += "```"
            if display_search_results:
                yield reply
            break

        # print('web search fin')
        
        open_url_re_match = compiled_open_url_command_regex.search(reply)
        if open_url_re_match is not None:
            yield reply
            original_model_reply = reply
            read_webpage = True
            url = open_url_re_match.group(1)
            print(f"LLM_Web_search | Reading {url}")
            reply += "\n```plaintext"
            reply += "\nURL opener tool:\n"
            try:
                webpage_content = get_webpage_content(url)
            except Exception as exc:
                reply += f"Couldn't open {url}. Error message: {str(exc)}"
                print(f'LLM_Web_search | {url} generated an exception: {str(exc)}')
            else:
                reply += f"\nText content of {url}:\n"
                reply += webpage_content
            reply += "```\n"
            if display_webpage_content:
                yield reply
            break
        yield reply

    print('web_search', web_search)
    print('read_webpage', read_webpage)
    if web_search or read_webpage:
    #     display_results = web_search and display_search_results or read_webpage and display_webpage_content
        display_results = False
        # Add results to context and continue model output
        print('before chat.generate_chat_prompt', f"{question}{reply}", state)
        # new_question = chat.generate_chat_prompt(f"{question}{reply}", state)
        
        # ChatLM Style
#         new_question = question + reply + """<|im_end|>
# <|im_start|>assistant
# AI:
#         """


        # LLAMA3 Style
        new_question = question + reply + """<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""     

        print('new_question!!!!', new_question)
        print('new_question####')
        
        # print('new_question', new_question)
        new_reply = ""
        # for new_reply in generate_func(new_question, new_question, seed, state, stopping_strings, is_chat=is_chat):
        print('new_question start')
        for new_reply in generate_func(new_question):
            if display_results:
                yield f"{reply}\n{new_reply}"
            else:# 여기임
                # yield f"{original_model_reply}\n{new_reply}"
                yield f"{new_reply}"
        
        # print('new_reply', new_reply)

        # if not display_results:
        #     update_history = [state["textbox"], f"{reply}\n{new_reply}"]

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


def get_ChatLM_question(question):
    question = """<|im_start|>system
A chat between a curious user and artificial intelligence assistant. The assistant is never confident about facts. The assistant always searches the web for facts. The assistant uses the available tools to retrieve relevant information and give helpful, detailed, and polite answers to the user's questions. The assistant simply answers the question succinctly and makes no reference to the source or rationale.

Search tool command format: Search_web("<|query|>")

Date and time of conversation: """+ str(datetime.now().strftime('%A %d %B %Y %H:%M'))+"""<|im_end|>
<|im_start|>user
Continue the chat dialogue below. Write a single reply for the character "AI".

The following is a conversation with an AI Large Language Model. The AI has been trained to answer questions, provide recommendations, and help with decision making.

AI: How can I help you today?
You: """ + question + """<|im_end|>
<|im_start|>assistant
AI:"""

'''
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>
{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
'''
def get_LLAMA3_question(question):
    question = """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

A chat between a curious user and artificial intelligence assistant. The assistant is never confident about facts. The assistant always searches the web for facts. The assistant uses the available tools to retrieve relevant information and give helpful, detailed, and polite answers to the user's questions. The assistant simply answers the question succinctly and makes no reference to the source or rationale.

Search tool command format: Search_web("<|query|>")

Date and time of conversation: """+str(datetime.now().strftime('%A %d %B %Y %H:%M'))+"""<|eot_id|><|start_header_id|>system<|end_header_id|>

Continue the chat dialogue below. Write a single reply for the character "AI".

The following is a conversation with an AI Large Language Model. The AI has been trained to answer questions, provide recommendations, and help with decision making.<|eot_id|><|start_header_id|>assistant<|end_header_id|>

How can I help you today?<|eot_id|><|start_header_id|>user<|end_header_id|>

"""+question+"""<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
    return question


def _generate_reply(question, state=None, stopping_strings=None, is_chat=False, escape_html=False, for_ui=False):
    # custom_generate_reply(question, None, seed, state, stopping_strings, is_chat, model.generate)
    # question = get_ChatLM_question(question)
    question = get_LLAMA3_question(question)
    
    
    print('question', question)
    global llm
    all_stop_strings = ['\nYou:', '<|im_end|>\n<|im_start|>user\n', '<|im_end|>\n<|im_start|>assistant\n', '\nAI:', "<|eot_id|>"]
    # for reply in custom_generate_reply(question, None, -1, None, None, True, model.generate):  # no stream
    reply_list = list()
    for reply in custom_generate_reply(question, None, -1, None, None, True, llm.generate_with_streaming_web):  # stream
        # 아직 검색 키워드 체킹
        if "Search_web(" in reply:
            continue
        
        reply_list = get_punctuation_sentences(reply)
        reply_list_creating = reply_list[:len(reply_list)-1]

        # 첫 문장 생성중
        if not reply_list_creating:
            continue  

        # 멈추라면 그대로 break
        if st.get_is_stop_requested():       
            st.set_is_stop_requested(False)
            break
            

        # stop 문 있으면 break
        if reply_list:
            _, stop_found = apply_stopping_strings(reply_list[-1], all_stop_strings)  # 마지막 문장만 체크하면 되겠네.
            if stop_found:
                print('stop_found', stop_found, reply_list)
                if len(reply_list)>=1:
                    reply_list = reply_list[:len(reply_list)-1]
                break
        
        # 3문장 넘으면 break
        if len(reply_list) >= 10:  # 4-1 줄까지 작업
            break
        
        yield reply_list_creating           
    yield reply_list

# 줄바꿈 감지하지 않음 / 예시 : "Here's a simple recipe that you can try:\n\nIngredients:\n\n Vegetable oil or cooking spray for greasing the pan\n\nInstructions:\n\n1.", 'In a large bowl, whisk together the flour, sugar, baking powder, and salt.\n2.', 'In a separate bowl, whisk together the milk, egg, and melted butter.\n3.'
def get_punctuation_sentences(texts):
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
    is_use_cuda = False
    is_use_cuda = True
    load_model(is_use_cuda)  # compressor때문이라도 해야함
    
    # question = "What are the top trending news stories in the Korea right now?"
    # question = "What is the current stock price of Apple Inc. (AAPL)?"
    question = "What is the current exchange rate between USD and EUR?"
    # question = "What date is today?"
    # question = "Tell me the weather of tokyo today."
    # question = "tell me how to make pancake!"
    last_reply_len = 0
    for j, reply_list in enumerate(process(question)):
        if last_reply_len < len(reply_list):
            last_reply_len = len(reply_list)
            # print('reply_list', reply_list)
    # print('reply_list', reply_list)
