import requests
import os, shutil
from time import time

from PIL import Image
from ai_singleton import get_vision_model, get_vision_processor

vision_processor = None
vision_model = None

def load_model():
    global vision_model, vision_processor
    vision_model = get_vision_model()
    vision_processor = get_vision_processor()

def get_image_from_url(url):
    # url = "https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/transformers/tasks/car.jpg?download=true"
    image = Image.open(requests.get(url, stream=True).raw)
    return image

def get_image_from_file(file_path):
    # Test용 코드
    if not file_path:
        file_path = './image/external.png'
    
    # temp 파일 생성
    directory, filename = os.path.split(file_path)
    tmp_filename = f'tmp_{filename}'
    tmp_file_path = os.path.join(directory, tmp_filename)
    shutil.copy(file_path, tmp_file_path)
    
    i = 0 
    while True:
        try:
            image = Image.open(tmp_file_path).convert("RGB")
            break
        except:
            time.sleep(0.2)
            i+=1
        if i > 15:  # 15*0.2=최대 3초 리트라이
            return None
    return image

def get_image_info(file_path):
    global vision_model, vision_processor
    if not vision_model:
        load_model()
    prompt = "<MORE_DETAILED_CAPTION>"
    image = get_image_from_file(file_path)
    if image:
        inputs = vision_processor.processor(text=prompt, images=image, return_tensors="pt")

        generated_ids = vision_model.model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            num_beams=3,
            do_sample=False
        )
        generated_text = vision_processor.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        parsed_answer = vision_processor.processor.post_process_generation(generated_text, task=prompt, image_size=(image.width, image.height))
        return parsed_answer[prompt]
    else:
        return 'The image recognition programme is not working properly, it needs to be re-requested.'
    
    
