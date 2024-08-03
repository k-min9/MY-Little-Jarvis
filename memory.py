import json
import os
import prompt_main

def save_conversation_memory(speaker, message, message_trans=''):
    if not message_trans:
        message_trans = message
    conversation_memory_file = './memory/conversation_memory.json'
    try:
        with open(conversation_memory_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []
    
    data.append({'speaker': speaker, 'message': message, 'message_trans': message_trans})
    
    os.makedirs('./memory', exist_ok=True) 
    with open(conversation_memory_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def get_all_conversation_memory():
    conversation_memory_file = './memory/conversation_memory.json'
    if not os.path.exists(conversation_memory_file):
        return []
    try:
        with open(conversation_memory_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return []

def get_latest_conversation_memory(conversation_memory_number):
    conversation_memory_file = './memory/conversation_memory.json'
    if not os.path.exists(conversation_memory_file):
        return []
    try:
        with open(conversation_memory_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return data[-conversation_memory_number:]
    except FileNotFoundError:
        return []

def reset_conversation_memory():
    conversation_memory_file = './memory/conversation_memory.json'
    os.makedirs('./memory', exist_ok=True)
    with open(conversation_memory_file, 'w', encoding='utf-8') as file:
        json.dump([], file)

# count까지의 길이 텍스트 (순서는 허용)
def get_truncated_conversation_memory(max_len=2048):
    # 기본 대화
    result_list, greeting_len = get_greeting_dialogue()
    max_len = max_len - greeting_len
    
    # 메모리 최대까지 대화 추가
    conversation_memory = get_all_conversation_memory()
    
    memory_len = 0
    memory_cnt = 0
    truncated_meomory = list()
    for memory in reversed(conversation_memory):
        if len(memory['message_trans']) + memory_len >= max_len:
            break
        memory_len += len(memory['message_trans'])
        memory_cnt += 1
        truncated_meomory.append(memory)
    
    # 합치기
    result_list.extend(truncated_meomory[::-1])
        
    return result_list, greeting_len + memory_len, memory_cnt

def get_greeting_dialogue():
    greeting_list = list()
    greeting_list.append({'speaker': 'player', 'message': 'hello, {character}?', 'message_trans': 'hello, {character}?'})
    greeting_list.append({'speaker': 'character', 'message': 'hello. what can i do for you, sensei?', 'message_trans': 'hello. what can i do for you, sensei?'})
    
    greeting_len = 0
    for greeting in greeting_list:
        greeting_len += len(greeting['message'])

    return greeting_list, greeting_len

# 마지막 대화 지우기
def delete_recent_dialogue():
    conversation_memory_file = './memory/conversation_memory.json'
    if not os.path.exists(conversation_memory_file):
        return
    try:
        with open(conversation_memory_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = []
    
    if data:
        data.pop()
    
    with open(conversation_memory_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# 평범한 문장
def get_text_prompt():
    local_memory_len = 2048  # 글자 수로 변경
    # memory를 포함한 대화 내역 생성
    prompt = ''
    if local_memory_len <=0:
        prompt += "\n{player}:hello, {character}?"
        prompt += "\n{character}:hello. what can i do for you, sensei?" 
    else:
        conversation_memory, memory_len, memory_cnt = get_truncated_conversation_memory(2048)
        for memory in conversation_memory:
            if memory['speaker'] == 'player':
                prompt += "\n{player}:"+memory['message_trans']
            elif memory['speaker'] == 'character':
                prompt += "\n{character}:"+memory['message_trans']
    return prompt


def get_chatLM_prompt():
    def add_chatLM_prompt(speaker_type, speaker_name, text):  # [user, assistant], [You, AI]
        prompt = """\n<|im_start|>"""+speaker_type+"""
"""+speaker_name+""": """ + text + """<|im_end|>"""
        return prompt
    local_memory_len = 2048  # 글자 수로 변경
    # memory를 포함한 대화 내역 생성
    prompt = ''
    conversation_memory, memory_len, memory_cnt = get_truncated_conversation_memory(2048)
    for memory in conversation_memory:
        if memory['speaker'] == 'player':
            prompt += add_chatLM_prompt('user', '{player}', memory['message_trans'])
        elif memory['speaker'] == 'character':
            prompt += add_chatLM_prompt('assistant', '{character}', memory['message_trans'])
    return prompt
    
# 2048 글자(token보다 낮을 수 밖에 없음)
def get_memory_message_list(local_memory_len = 2048):
    conversation_memory, memory_len, memory_cnt = get_truncated_conversation_memory(local_memory_len)    
    messages = list()
    for memory in conversation_memory:
        if memory['speaker'] == 'player':
            messages.append({"role": "user", "content": memory['message_trans']})
        elif memory['speaker'] == 'character':
            messages.append({"role": "assistant", "content": memory['message_trans']})    
    return messages
        
if __name__ == "__main__":
    # sample conversation
    pass

    # test
    # print(get_truncated_conversation_memory())
    # print(get_text_prompt())
    
    # print(get_chatLM_prompt())
    print(prompt_main.get_message_list_main())
    print(get_memory_message_list(4096))