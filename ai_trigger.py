import re
from threading import Lock
import random

from ai_singleton import check_llm, get_llm
from ai_trigger_topics import topics

import state

llm = None

generation_lock = Lock()

def load_model(is_use_cuda=False):
    global llm
    if state.get_use_gpu_percent() != 0:  # gpu 사용여부 확인 (0이 아님)
        llm = get_llm()
    elif not check_llm() or is_use_cuda:  # 초기화 여부
        llm = get_llm()
    else:
        from ai_llama_cpp_model import LlamaCppModel 
        llm, tokenizer = LlamaCppModel.from_pretrained('./model/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf')

def process_stream(query, player, character, is_sentence, is_regenerate, info_rag=None, info_memory=None, info_web=None):
    global llm
    if not llm:
        load_model()
    
    if is_sentence:
        for j, reply_list in enumerate(generate_reply(query, player, character, is_sentence, is_regenerate)):
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
        for j, reply in enumerate(generate_reply(query, player, character, is_sentence, is_regenerate)):
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

'''
<|begin_of_text|><|start_header_id|>system<|end_header_id|>
{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>
{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>
'''
def get_LLAMA3_prompt(topic, player_name=None, char_name=None):
    import prompt_main
    import memory
    from jinja2 import Template
    LLAMA3_TEMPLATE = "{% set loop_messages = messages %}{% for message in loop_messages %}{% set content = '<|start_header_id|>' + message['role'] + '<|end_header_id|>\n\n'+ message['content'] | trim + '<|eot_id|>' %}{% if loop.index0 == 0 %}{% set content = bos_token + content %}{% endif %}{{ content }}{% endfor %}{% if add_generation_prompt %}{{ '<|start_header_id|>assistant<|end_header_id|>\n\n' }}{% endif %}"
    LLM_STOP_SEQUENCE = "<|eot_id|>"
       
    messages = list() 
    content = """You are {{char}}, a cute little assistant AI girl, chatting with {{user}}, a teacher. You need to bring up a topic before you start chatting. You're given a theme. Use the theme to start a conversation by creating a concise topic to talk about with the user.
Return the result in the following format:
Result : <|Topic|>

Example:
Topic: "Weekend plans"
Result: What will you going to do this weekend, sensei?

Topic: "Lunch Menu"
Result: Teacher? What will you going to do this weekend?

Topic: "Last night"
Result: I had an amazing dream last night!"""
    messages.append({"role": "system", "content": content})
    messages.extend(prompt_main.get_message_list_main(char_name))
    # messages.extend(memory.get_memory_message_list(4096))  #  메모리 배제

    template = Template(LLAMA3_TEMPLATE)
    prompt = template.render(
                    messages=messages,
                    bos_token="<|begin_of_text|>",
                    add_generation_prompt=False,  # <|im_start|>assistant를 마지막에 붙이는거
    )
    prompt = prompt + f"""<|start_header_id|>assistant<|end_header_id|>

Topic: "{topic}"
Result: """
    
    return prompt

def get_random_topic(topics):
    random_index = random.randint(0, len(topics) - 1)
    return topics[random_index]["eng"]

def _generate_reply(query, player, character, is_sentence, is_regenerate, info_rag=None, info_memory=None, info_web=None, temperature=0.2):    
    # print('is_sentence', is_sentence)
    global llm
    
    topic = get_random_topic(topics)
    prompt = get_LLAMA3_prompt(topic, character)  # rag, web, memory(long) 미적용

    all_stop_strings = ['\nYou:', '<|im_end|>', '<|im_start|>user', '<|im_start|>assistant\n', '\nAI:', "<|eot_id|>"]
    if is_sentence:
        reply_list = list()
        for reply in custom_generate_reply(prompt, None, -1, None, None, True, is_regenerate, llm.generate_with_streaming):  # stream     
            reply_list = get_punctuation_sentences(reply)
            reply_list_creating = reply_list[:len(reply_list)-1]
            
            # 첫 문장 생성중
            if not reply_list_creating:
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
            
            # 3문장 넘으면 break
            if len(reply_list) >= 4:  # 4-1 줄까지 작업
                break
            
            yield reply_list_creating           
        yield reply_list # 맞...나?
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
            
            # 3문장 넘으면 break
            reply_list = get_punctuation_sentences(reply)
            if len(reply_list) >= 6:  # 문장-1 줄까지 작업
                reply = ''.join(reply_list[:len(reply_list)-1]) # 문장 수 까지 반환
                break
            
            yield reply           
        yield reply

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
    # print(get_chatLM_prompt('hello?'))
    
    # 제대로 된 모델 로딩
    # load_model(is_use_cuda=True)
    load_model(is_use_cuda=False)

    # Stream 테스트 (문장)
    # 딕셔너리를 반복문으로 조회하는 코드
    for topic in topics:
        print(f"Index: {topic['index']}, Korean: {topic['kor']}, English: {topic['eng']}")

        result = ''
        last_reply_len = 0
        for j, reply_list in enumerate(process_stream(topic['eng'], 'm9dev', 'arona', True, False)):
            if last_reply_len < len(reply_list):
                last_reply_len = len(reply_list)
        print(f'topic{j} :', topic['kor'], '/', topic['eng'])
        print('question :', ' '.join(reply_list))
    