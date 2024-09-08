'''
pygame으로 발언중에도 음성인식이 가능해지는 Class 별도 제작
'''
import threading
import time
import queue
import requests
import re
import json
import os

import numpy as np
import sounddevice as sd
import pygame
from faster_whisper import WhisperModel
import googletrans
translator_Google = googletrans.Translator()
loaded_settings = list()

# local module
import vad
import ai_conversation
from inference_ko import synthesize_char
from main import play_wav_queue_add, clear_wav_queue, stop_wav, AnswerBalloon
import memory

PAUSE_TIME = 0.05
PAUSE_LIMIT = 400  # Milliseconds of pause allowed before processing
VAD_SIZE = 50
VAD_THRESHOLD = 0.9  # Threshold for VAD detection

# 음악 재생 함수
def play_music():
    pygame.mixer.music.play(-1)  # 음악을 무한 반복으로 재생

class FasterWhisperListener:
    def __init__(self, lang='en', root=None, program_type='CPU'):
        AnswerBalloon.set_images()
        self.status = None
        self.program_type = program_type
        self.use_cuda = False
        if not self.program_type == 'CPU':
            self.use_cuda = True
        
        # self.model = WhisperModel("base", device="cpu", download_root='./model_whisper')
        self.model = WhisperModel("small", device="cpu", download_root='./model')
        # self.model = WhisperModel("large-v3", device="cuda", download_root='./model')
        self._vad_model = vad.VAD(model_path="./model/silero_vad.onnx")
        
        self.root = root
        self.language = lang  # ja, en, ko
        self.player = "sensei"
        self.character = "Arona"
        
        self.answer_balloon = None
    
        self.completion_url = ""
        self._samples = []
        self._sample_queue = queue.Queue()
        BUFFER_SIZE = 600 # Milliseconds of buffer before VAD detection
        VAD_SIZE = 50  # Milliseconds of sample for Voice Activity Detection (VAD)
        self._buffer = queue.Queue(
            maxsize=BUFFER_SIZE // VAD_SIZE
        )
        self._recording_started = False
        self.currently_speaking = False
        self.interruptible = True  # 도중에 말 끊을 수 있음
        self.shutdown_event = threading.Event()
        self._gap_counter = 0
        
        self.llm_queue = queue.Queue()
        self.processing = False
        self.currently_speaking = False
   
        llm_thread = threading.Thread(target=self.process_LLM)
        llm_thread.start()
        
        def audio_callback_for_sdInputStream( indata, frames, time, status):
            data = indata.copy().squeeze()  # Reduce to single channel if necessary
            vad_confidence = self._vad_model.process_chunk(data) > VAD_THRESHOLD
            if vad_confidence:
                # 질문다운 문장왔으면 기존의 음성 재생 멈춤 + 새로이 시작
                self.status = 'think'
                stop_wav()
                clear_wav_queue()
            self._sample_queue.put((data, vad_confidence))

        SAMPLE_RATE = 16000  # Sample rate for input stream
        self.input_stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            callback=audio_callback_for_sdInputStream,
            blocksize=int(SAMPLE_RATE * VAD_SIZE / 1000),
        )  

    def process_LLM(self):
        while not self.shutdown_event.is_set():
            try:
                detected_text = self.llm_queue.get(timeout=0.1)
                
                prompt = ai_conversation.get_LLAMA3_prompt(detected_text)
                
                # prompt = prompt.replace("{player}", self.player)
                # prompt = prompt.replace("{char}", self.character)

                data = {
                    "stream": True,
                    "prompt": prompt,
                }
                print(f"starting request on '{detected_text}'")
                print("Performing request to LLM server...")

                if self.answer_balloon:
                    self.answer_balloon.kill_balloon()    
                    self.answer_balloon = None           
                
                answer = dict()
                answer['answer_en'] = ''                 
                answer['answer_ko'] = ''
                answer['answer_jp'] = ''
                answer['setting_lang'] = self.language

                with requests.post(
                    self.completion_url,
                    json=data,
                    stream=True,
                ) as response:
                    # 새로운 답장왔으면 기존의 음성 재생 멈춤 + 새로이 시작
                    # self.status = 'talk'
                    stop_wav()
                    clear_wav_queue()
                    
                    # iter stream
                    sentence = []
                    for line in response.iter_lines():
                        if self.processing is False:
                            break  # If the stop flag is set from new voice input, halt processing
                        if line:  # Filter out empty keep-alive new lines
                            line = self._clean_raw_bytes(line)
                            next_token = self._process_line(line)
                            if next_token:
                                sentence.append(next_token)
                                # If there is a pause token, send the sentence to the TTS queue
                                if next_token in [
                                    ".",
                                    "!",
                                    "?",
                                    ":",
                                    ";",
                                    "?!",
                                    "\n",
                                    "\n\n",
                                ]:
                                    processed_sentence = self._process_sentence(sentence)
                                    print('answer', processed_sentence)
                                    if '<|im' in processed_sentence:
                                        processed_sentence = processed_sentence.split('<|im')[0]
                                        self.processing = False
                                        
                                    result_jp = translator_Google.translate(processed_sentence, dest='ja').text
                                    result_ko = translator_Google.translate(processed_sentence, dest='ko').text
                                    
                                    if answer['answer_en']:
                                        answer['answer_en'] = answer['answer_en'] + ' ' + processed_sentence.lstrip()
                                    else:
                                        answer['answer_en'] = processed_sentence.lstrip()
                                    if answer['answer_ko']:
                                        answer['answer_ko'] = answer['answer_ko'] + ' ' + result_ko.lstrip()
                                    else:
                                        answer['answer_ko'] = result_ko.lstrip()
                                    answer['answer_jp'] = answer['answer_jp'] + result_jp.lstrip()  
                                    
                                    if self.answer_balloon:
                                        # 말풍선 갱신                                                           
                                        self.answer_balloon.modify_text_from_answer(answer)
                                        # tkinter 창 업데이트
                                        self.answer_balloon.update_idletasks()
                                        self.answer_balloon.update()
                                    else:
                                        self.answer_balloon = AnswerBalloon(answer, detected_text, root_called=self.root)
                
                                    audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_ko, use_cuda=self.use_cuda, type='single', sid=0)
                                    play_wav_queue_add(audio) 
                                    sentence = []                            
                    if self.processing:
                        if sentence:
                            processed_sentence = self._process_sentence(sentence)
                            print('answer', processed_sentence)
                            if '<|im' in processed_sentence:
                                processed_sentence = processed_sentence.split('<|im')[0]
                                self.processing = False
                                
                            result_jp = translator_Google.translate(processed_sentence, dest='ja').text
                            result_ko = translator_Google.translate(processed_sentence, dest='ko').text

                            if answer['answer_en']:
                                answer['answer_en'] = answer['answer_en'] + ' ' + processed_sentence.lstrip()
                            else:
                                answer['answer_en'] = processed_sentence.lstrip()
                            if answer['answer_ko']:
                                answer['answer_ko'] = answer['answer_ko'] + ' ' + result_ko.lstrip()
                            else:
                                answer['answer_ko'] = result_ko.lstrip()
                            answer['answer_jp'] = answer['answer_jp'] + result_jp.lstrip()  
                            
                            if self.answer_balloon:
                                # 말풍선 갱신                                                           
                                self.answer_balloon.modify_text_from_answer(answer)
                                # tkinter 창 업데이트
                                self.answer_balloon.update_idletasks()
                                self.answer_balloon.update()
                            else:
                                self.answer_balloon = AnswerBalloon(answer, detected_text, root_called=self.root)                                     
                            
                            audio = os.path.abspath('.').replace('\\','/') +'/' + synthesize_char('korean', result_ko, use_cuda=self.use_cuda, type='single', sid=0)
                            play_wav_queue_add(audio)  
                            self.status = 'talk'
                    
                    memory.save_conversation_memory('player', detected_text)
                    memory.save_conversation_memory('character', answer['answer_en'])                  
                    # self.tts_queue.put("<EOS>")  # Add end of stream token to the queue
            except queue.Empty:
                time.sleep(PAUSE_TIME)

    def process_single_LLM(self, text=""):        
        prompt = ai_conversation.get_chatLM_prompt(text)

        data = {
            "stream": True,
            "prompt": prompt,
        }
        print(f"starting request on '{text}'")
        print("Performing request to LLM server...")
        # print('prompt', prompt)

        # Perform the request and process the stream
        with requests.post(
            self.completion_url,
            # headers=self.prompt_headers,
            json=data,
            stream=True,
        ) as response:
            sentence = []
            for line in response.iter_lines():
                # if self.processing is False:
                #     break  # If the stop flag is set from new voice input, halt processing
                if line:  # Filter out empty keep-alive new lines
                    line = self._clean_raw_bytes(line)
                    next_token = self._process_line(line)
                    if next_token:
                        sentence.append(next_token)
                        # If there is a pause token, send the sentence to the TTS queue
                        if next_token in [
                            ".",
                            "!",
                            "?",
                            ":",
                            ";",
                            "?!",
                            "\n",
                            "\n\n",
                        ]:
                            self._process_sentence(sentence)
                            sentence = []

    def _process_sentence(self, current_sentence):
        sentence = "".join(current_sentence)
        sentence = re.sub(r"\*.*?\*|\(.*?\)", "", sentence)
        sentence = (
            sentence.replace("\n\n", ". ")
            .replace("\n", ". ")
            .replace("  ", " ")
            .replace(":", " ")
        )
        if sentence:
            # print('sentence', sentence)
            # self.tts_queue.put(sentence)
            return sentence
            

    def _process_line(self, line):
        if not line["stop"]:
            token = line["content"]
            return token
        return None

    def _clean_raw_bytes(self, line):
        line = line.decode("utf-8")
        line = line.removeprefix("data: ")
        line = json.loads(line)
        return line

    def start_listen_event_loop(self):
        self.input_stream.start()
        print("Audio Modules Operational")
        print("Listening...")
        # Loop forever, but is 'paused' when new samples are not available
        try:
            while not self.shutdown_event.is_set():
                sample, vad_confidence = self._sample_queue.get()
                self._handle_audio_sample(sample, vad_confidence)
            return
        except KeyboardInterrupt:
            self.shutdown_event.set()
            self.input_stream.stop()

    def set_shutdown_event(self):
        self.shutdown_event.set()
        self.input_stream.stop()           
            
    def _handle_audio_sample(self, sample, vad_confidence):
        if not self._recording_started:
            self._manage_pre_activation_buffer(sample, vad_confidence)
        else:
            self._process_activated_audio(sample, vad_confidence)        
      
    def _manage_pre_activation_buffer(self, sample, vad_confidence):
        if self._buffer.full():
            self._buffer.get()  # Discard the oldest sample to make room for new ones
        self._buffer.put(sample)

        if vad_confidence:  # Voice activity detected
            sd.stop()  # Stop the audio stream to prevent overlap
            self.processing = (
                False  # Turns off processing on threads for the LLM and TTS!!!
            )
            self._samples = list(self._buffer.queue)
            self._recording_started = True      
        
    def _process_activated_audio(self, sample, vad_confidence):
        self._samples.append(sample)

        if not vad_confidence:
            self._gap_counter += 1
            if self._gap_counter >= PAUSE_LIMIT // VAD_SIZE:
                self._process_detected_audio()
        else:
            self._gap_counter = 0

    def transcribe_audio(self, samples):
        audio = np.concatenate(samples)
        audio_array = audio.astype(np.float32)
        segments, info = self.model.transcribe(audio_array, beam_size=5, language=self.language)
        text =""
        for segment in segments:
            text = text + segment.text # + " "
        return text.lower()

    def _process_detected_audio(self):
        print("Detected pause after speech. Processing...")
        self.input_stream.stop()

        detected_text = self.transcribe_audio(self._samples)

        if detected_text:
            print(f"ASR text: '{detected_text}'")

            # if self.wake_word and not self._wakeword_detected(detected_text):
            #     print(f"Required wake word {self.wake_word=} not detected.")
            
            self.llm_queue.put(detected_text)
            self.processing = True
            self.currently_speaking = True

        if not self.interruptible:
            while self.currently_speaking:
                time.sleep(PAUSE_TIME)

        self.reset()
        self.input_stream.start()
        
    def reset(self):
        self._recording_started = False
        self._samples.clear()
        self._gap_counter = 0
        with self._buffer.mutex:
            self._buffer.queue.clear()

if __name__ == "__main__":
    # 초기화 for test
    pygame.mixer.init()
    
    # pygame 공존 테스트
    # pygame.mixer.music.load('./output/output1.wav')
    # play_music()
    
    from llama_server import LlamaServer    
    llama_server = LlamaServer(use_gpu=True)
    llama_server.start()

    fasterWhisperListener = FasterWhisperListener()
    fasterWhisperListener.completion_url = llama_server.completion_url
    fasterWhisperListener.start_listen_event_loop()

