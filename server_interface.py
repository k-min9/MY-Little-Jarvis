import json
import state

# Local
# from ai_singleton import check_llm, get_llm  # main
# from ai_singleton import get_vision_model, get_vision_processor  # image
import ai_conversation

# Server-Flask
from flask import Flask, Response, request, jsonify
app = Flask(__name__)

# llm = None
# vision_processor = None
# vision_model = None

# def load_model(is_use_cuda=True):
#     global llm
#     if not check_llm():
#         llm = get_llm()

@app.route('/conversation_stream', methods=['POST'])
def main_stream():  # main logic
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

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy"}), 200

if __name__ == '__main__':
    # llm = load_model()
    # vision_model = get_vision_model()
    # vision_processor = get_vision_processor()
    
    state.set_use_gpu_percent(8)  # GPU 100% 발동
    
    app.run(host='0.0.0.0', port=5000)
