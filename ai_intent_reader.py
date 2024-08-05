from threading import Lock

from ai_singleton import check_llm, get_llm

llm = None

generation_lock = Lock()

def load_model(is_use_cuda=False):
    global llm
    if check_llm():
        llm = get_llm()
    elif is_use_cuda:
        llm = get_llm()
    else:
        from ai_llama_cpp_model import LlamaCppModel 
        llm, tokenizer = LlamaCppModel.from_pretrained('./model/llama-3-neural-chat-v1-8b-Q4_K_M.gguf')

def process(question):
    from jinja2 import Template
    global llm
    if not llm:
        load_model()
        
    LLAMA3_TEMPLATE = "{% set loop_messages = messages %}{% for message in loop_messages %}{% set content = '<|start_header_id|>' + message['role'] + '<|end_header_id|>\n\n'+ message['content'] | trim + '<|eot_id|>' %}{% if loop.index0 == 0 %}{% set content = bos_token + content %}{% endif %}{{ content }}{% endfor %}{% if add_generation_prompt %}{{ '<|start_header_id|>assistant<|end_header_id|>\n\n' }}{% endif %}"
    LLM_STOP_SEQUENCE = "<|eot_id|>"
    
    messages =list()
    content = """Determine if the user is asking about past events in a novel and if a web search is needed to answer the question. 
response the result ONLY in the following format.  Do not add any additional comments:
rag: True/False
web: True/False"""
    messages.append({"role": "system", "content": content})
    content = """Example:
Question: "What happened to Mika when she visited the store?"
Result:
rag: True
web: False

Question: "What date is today?"
Result:
rag: False
web: True

Question: "What did you do today?"
Result:
rag: False
web: False"""
    messages.append({"role": "system", "content": content})

    template = Template(LLAMA3_TEMPLATE)
    prompt = template.render(
                    messages=messages,
                    bos_token="<|begin_of_text|>",
                    add_generation_prompt=False,  # <|im_start|>assistant를 마지막에 붙이는거
    )
    prompt = prompt + f"""<|start_header_id|>assistant<|end_header_id|>

Question: "{question}"
Result:"""

    output = llm.create_completion(
        # max_tokens=128,  
        max_tokens=4096, # infinity
        # stop=["Q:", "\n"],
        # stop=[f"sensei:",f"sensei(","<|im_","user:", "#", ":"],
        stop=["<|eot_id|>", "question:", "Question:"],
        prompt=prompt,
        temperature=0
    )
    result = output['choices'][0]['text']
    
    # 문장체크
    
    # 감정체크
    
    # 정제 [음성용으로 따로 뱉던가.]
    # import re
    # result = result.replace("\n",'')
    # result = re.sub(r'\([^)]*\)', '', result)  # ()와 안의 내용물 제거
    # result = re.sub(r'\[[^)]*\]', '', result)  # []와 안의 내용물 제거
    # result = re.sub(r'\*[^)]*\*', '', result)  # * *과 안의 내용물 제거
    
    # print('prompt', prompt)

    return result


if __name__ == "__main__":
    load_model()
    
    question = "do you like coffee?"
    response = process(question)
    print('===============')
    print('question : ', question)
    print('response\n', response)
    
    question = "what did you do yesterday?"
    response = process(question)
    print('===============')
    print('question : ', question)
    print('response\n', response)
    
    question = "where is capital of france?"
    response = process(question)
    print('===============')
    print('question : ', question)
    print('response\n', response)
    
    question = "do you no hoshino?"
    response = process(question)
    print('===============')
    print('question : ', question)
    print('response\n', response)
    
    question = "what time is now?"
    response = process(question)
    print('===============')
    print('question : ', question)
    print('response\n', response)
    