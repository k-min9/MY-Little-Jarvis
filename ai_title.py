'''
대화로그 내용을 보고 적절한 이름을 지어줌
'''
import json
import re
from threading import Lock

import state

from ai_singleton import check_llm, get_llm

llm = None

generation_lock = Lock()

def load_model(is_use_cuda=True):  # 현재 CPU 오류 + history 등 외부 호출 고려
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
    
    for j, reply_list in enumerate(generate_reply(query, player, character, is_sentence, is_regenerate)):
        # visible_reply_list = list()
        # for reply in reply_list:
        #     visible_reply = reply
        #     visible_reply = re.sub("(<USER>|<user>|{{user}})", 'You', visible_reply)
        #     visible_reply = visible_reply.replace("\n",'')
        #     visible_reply = re.sub(r'\([^)]*\)', '', visible_reply)  # ()와 안의 내용물 제거
        #     visible_reply = re.sub(r'\[[^)]*\]', '', visible_reply)  # []와 안의 내용물 제거
        #     visible_reply = re.sub(r'\*[^)]*\*', '', visible_reply)  # * *과 안의 내용물 제거
        #     visible_reply = visible_reply.lstrip(' ')
        #     visible_reply_list.append(visible_reply)
        yield reply_list

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
def get_LLAMA3_prompt():
    import prompt_main
    import memory
    from jinja2 import Template
    LLAMA3_TEMPLATE = "{% set loop_messages = messages %}{% for message in loop_messages %}{% set content = '<|start_header_id|>' + message['role'] + '<|end_header_id|>\n\n'+ message['content'] | trim + '<|eot_id|>' %}{% if loop.index0 == 0 %}{% set content = bos_token + content %}{% endif %}{{ content }}{% endfor %}{% if add_generation_prompt %}{{ '<|start_header_id|>assistant<|end_header_id|>\n\n' }}{% endif %}"
    LLM_STOP_SEQUENCE = "<|eot_id|>"
       
    messages = list() 
    content = """You're an expert at looking at conversations and creating titles based on the content of those conversations. given dialog is a conversation between two people, {char} and {user}.

please respond in the order of the titles you think are best suited with a JSON consisting of the formats {"title": Title you created, "reason": optional, reason or sentence that make you to think that.}.

Example:
{[
    {
        "title": "Tomorrow's schedule",
        "reason" : "Tomorrow's schedule was the main topic of discussion."
    },
    {
        "title": "Sensei's hobby",
        "reason" : "{char} asks about {user}'s hobby and gets an answer"
    },
    {
        "title" : "simple conversation"
    }
]}

"""
    messages.append({"role": "system", "content": content})
    # messages.extend(prompt_main.get_message_list_main())
    conversations = memory.get_memory_message_list(99999)  # 최대 128K
    dialog = ""
    for conversation in conversations:
        role = conversation['role']
        content = conversation['content']
        
        dialog_role = '{user}'
        if role == "assistant":
            dialog_role = '{char}'
        dialog = dialog + dialog_role + " : " + content + "\n"
    dialog = f"""Given dialog
```
{dialog}
```

"""
    dialog = dialog + "Recommend up to 5 titles that you think would be a good match based on the given dialog\n"

    messages.append({"role": "user", "content": dialog})
    # messages.append({"role": "user", "content": "Tell me all the traits of the {user} as best you can."})

    template = Template(LLAMA3_TEMPLATE)
    prompt = template.render(
                    messages=messages,
                    bos_token="<|begin_of_text|>",
                    add_generation_prompt=True,  # <|im_start|>assistant를 마지막에 붙이는거
    )
    
    return prompt

def _generate_reply(query, player, character, is_sentence, is_regenerate, info_rag=None, info_memory=None, info_web=None, temperature=0):    
    global llm
    
    prompt = get_LLAMA3_prompt()

    # all_stop_strings = ['\nYou:', '<|im_end|>', '<|im_start|>user', '<|im_start|>assistant\n', '\nAI:', "<|eot_id|>"]
    # reply_list = list()
    for reply in custom_generate_reply(prompt, None, -1, None, None, True, is_regenerate, llm.generate_with_streaming):  # stream     
        # reply_list = get_punctuation_sentences(reply)
        # reply_list_creating = reply_list[:len(reply_list)-1]
        
        # # 첫 문장 생성중
        # if not reply_list_creating:
        #     continue  
    
        # # 멈추라면 그대로 break
        # if state.get_is_stop_requested():       
        #     state.set_is_stop_requested(False)
        #     break
        
        # # stop 문 있으면 break
        # if reply_list:
        #     _, stop_found = apply_stopping_strings(reply_list[-1], all_stop_strings)  # 마지막 문장만 체크하면 되겠네.
        #     if stop_found:
        #         if len(reply_list)>=1:
        #             reply_list = reply_list[:len(reply_list)-1]
        #         break
        
        # # # 3문장 넘으면 break
        # # if len(reply_list) >= 4:  # 4-1 줄까지 작업
        # #     break
        
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
# 여기서는 안쓰임
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

# title 정보 text에서 list로
def get_title_infos(text):
    # 1단계: 텍스트에 대괄호([])로 감싸진 JSON 배열이 있는지 확인
    match = re.search(r'\[(.*?)\]', text, re.DOTALL)
    
    if not match:
        return []  # JSON 배열이 없으면 빈 리스트 반환

    # 2단계: JSON 문자열을 추출하고, 이를 딕셔너리의 리스트로 변환
    json_str = match.group(0)  # 매치된 문자열
    data_list = json.loads(json_str)
    
    # 3단계: 리스트를 반복하며 'title'이 포함된 딕셔너리만 필터링
    result = []
    for item in data_list:
        if "title" in item:
            result.append(item)
    
    return result

if __name__ == "__main__":
    import gc
    gc.collect()
    
    # prompt 체크
    # print(get_chatLM_prompt('hello?'))
    
    # 제대로 된 모델 로딩
    load_model(is_use_cuda=True)
    load_model(is_use_cuda=False)

    # Stream 테스트 (문장) > (일반) : tkinter 등의 동기화를 위해 pass도 의미가 있음.
    reply = ''
    for j, reply in enumerate(process_stream(None, 'm9dev', 'arona', True, False)):
        pass
    print(reply)
    
    title_infos = get_title_infos(reply)
    
    for title_info in title_infos:
        title = title_info['title']
        title_reason = ''
        if 'reason' in title_info:
            title_reason = title_info['reason']
        
        print('------------')
        print("title : " + title + "\nreason : " + title_reason)
        
        # TODO title은 UI에 맞게 변경해야 함
    
    