'''
메뉴 등의 UI 용
'''
import state
ui_lang = state.get_g_language_init()

from collections import defaultdict
messages_ui = defaultdict(defaultdict)

messages_ui['Setting']['ko'] = '설정'
messages_ui['Setting']['ja'] = '設定'
messages_ui['AI Setting']['ko'] = 'AI 설정'
messages_ui['AI Setting']['ja'] = 'AI 設定'
messages_ui['Idle']['ko'] = '제자리 대기'
messages_ui['Idle']['ja'] = 'その場で待機'
messages_ui['Idle Talk']['ko'] = '말 걸어줘'
messages_ui['Idle Talk']['ja'] = '声かけて'
messages_ui['Go Left']['ko'] = '왼쪽으로'
messages_ui['Go Left']['ja'] = '左へ'
messages_ui['Go Right']['ko'] = '오른쪽으로'
messages_ui['Go Right']['ja'] = '右へ'
messages_ui['Sit']['ko'] = '앉아줘'
messages_ui['Sit']['ja'] = '座って'
messages_ui['Deactivate Speech Recognition']['ko'] = '음성인식 비활성화'
messages_ui['Deactivate Speech Recognition']['ja'] = '音声認識無効化'
messages_ui['Activate Speech Recognition']['ko'] = '음성인식 활성화'
messages_ui['Activate Speech Recognition']['ja'] = '音声認識有効化'
messages_ui['Activate TikiTaka']['ko'] = '티키타카 활성화'
messages_ui['Activate TikiTaka']['ja'] = 'TikiTaka 起動'
messages_ui['Activate Focus']['ko'] = '집중모드 활성화'
messages_ui['Activate Focus']['ja'] = '集中モード 起動'
messages_ui['Deactivate Focus']['ko'] = '집중모드 비활성화'
messages_ui['Deactivate Focus']['ja'] = '集中モード 無効化'
messages_ui['Load models']['ko'] = '모델 로딩'
messages_ui['Load models']['ja'] = 'モデル読み込み'
messages_ui['Clean models']['ko'] = '모델 로딩 해제'
messages_ui['Clean models']['ja'] = 'モデル読み込み解除'
messages_ui['History']['ko'] = '대화이력'
messages_ui['History']['ja'] = '会話履歴'
messages_ui['Clear Conversation']['ko'] = '현재 대화 초기화'
messages_ui['Clear Conversation']['ja'] = '現在会話 初期化'
messages_ui['Version']['ko'] = 'Version'
messages_ui['Version']['ja'] = 'Version'
messages_ui['Exit']['ko'] = '종료'
messages_ui['Exit']['ja'] = '終了'
messages_ui["Please set the screenshot area first."]['ko'] = "우선 스크린샷 영역을 선택해주세요."
messages_ui["Please set the screenshot area first."]['ja'] = "まずスクリーンショット領域を設定してください。"
messages_ui['Info']['ko'] = '안내'
messages_ui['Info']['ja'] = 'ご案内'
messages_ui['Show Focus Area']['ko'] = '집중범위 표시'
messages_ui['Show Focus Area']['ja'] = '集中範囲表示'
messages_ui['Char Change']['ko'] = '캐릭변경'
messages_ui['Char Change']['ja'] = 'キャラクター変更'
# messages_ui['Setting']['ko'] = '설정'
# messages_ui['Setting']['ja'] = '設定'
# messages_ui['Setting']['ko'] = '설정'
# messages_ui['Setting']['ja'] = '設定'




def get_message_ui(message):
    global ui_lang    
    # 영어면 그대로 반환
    if ui_lang == 'en':
        return message

    # messages_ui dict에 없으면 원형 반환
    try:
        return messages_ui[message][ui_lang]
    except:
        print("### Messeages dict don't have keyword : " + message)
        return message