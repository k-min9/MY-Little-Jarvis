import json
import state
import pygame

# Local
import ai_conversation
import inference_ko

# Server-Flask
from flask import Flask, Response, request, jsonify, send_file
app = Flask(__name__)

# Translator (TODO : interface에서 로직 분리)
from proper_nouns import change_to_jp, change_to_ko  # 고유명사 번역
translator_google = None
try:
    import googletrans # 번역 관련
    translator_google = googletrans.Translator()
except:
    pass

# 번역없이 답변
@app.route('/conversation_stream/simple', methods=['POST'])
def main_stream_simple():  # main logic
    query = request.json.get('query')
    # image = ''  # TODO
    def generate():
        reply_len = 0
        for j, reply_list in enumerate(ai_conversation.process_stream(query, 'm9dev', 'arona', True, False)):
            if reply_len < len(reply_list):
                reply_len = len(reply_list)
                yield json.dumps({"reply_list": reply_list}) + '\n'
        # print(reply_list)
    return Response(generate(), content_type='application/json')

# 번역포함 답변
@app.route('/conversation_stream', methods=['POST'])
def main_stream():  # main logic
    query = request.json.get('query')
    player_name = request.json.get('player', 'sensei')  # player key가 없을대의 초기값 sensei
    char_name = request.json.get('char', 'arona')  # player key가 없을대의 초기값 m9dev
    ai_language = request.json.get('ai_language', 'en')  #  추론 언어 : 영입영출, 한입한출, 일입일출 등등
    # image = ''  # TODO
    def generate():
        answer_list = list()
        reply_len = 0
        for j, reply_list in enumerate(ai_conversation.process_stream(query, player_name, char_name, True, False)):
            if reply_len < len(reply_list):
                reply_len = len(reply_list)
                
                reply_new = reply_list[-1]
                result_ko = reply_new
                result_jp = reply_new
                try:
                    result_ko = translator_google.translate(reply_new, dest='ko').text
                    result_ko = change_to_ko(result_ko)
                    result_jp = translator_google.translate(reply_new, dest='ja').text    
                    result_jp = change_to_jp(result_jp)
                except:
                    pass
                answer = dict()
                answer['answer_en'] = reply_new                
                answer['answer_ko'] = result_ko
                answer['answer_jp'] = result_jp            
                answer_list.append(answer)
                
                print(reply_list)
                yield json.dumps({"reply_list": answer_list}) + '\n'
        # print(reply_list)
    return Response(generate(), content_type='application/json')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

# 한국어 텍스트를 입력받아 변환
@app.route('/getSound/ko', methods=['POST'])
def synthesize_ko():
    text = request.json.get('text', '안녕하십니까.')

    inference_ko.get_audio_file('korean', text)  # 동기적으로 ./output.wav 생성
    return send_file('./output.wav', mimetype="audio/wav")

# 한국어 텍스트를 입력받아 변환 (Test용 GET, 문장중에 '/'가 있을 경우 고장)
@app.route('/getSound/ko_test/')
@app.route('/getSound/ko_test/<text>')
def synthesize_ko_get(text=None):
    if text is None:
        text = '안녕하세요!'
    inference_ko.get_audio_file('korean', text)  # 동기적으로 ./output.wav 생성
    return send_file('./output.wav', mimetype="audio/wav")

if __name__ == '__main__':
    pygame.mixer.init()
    # llm = load_model()
    # vision_model = get_vision_model()
    # vision_processor = get_vision_processor()
    
    state.set_use_gpu_percent(8)  # GPU 100% 발동
    
    # preloading
    inference_ko.get_audio_file('korean', '안녕하세요!')
    for j, reply_list in enumerate(ai_conversation.process_stream('안녕?', 'sensei', 'arona', True, False)):
        pass
    
    app.run(host='0.0.0.0', port=5000)
