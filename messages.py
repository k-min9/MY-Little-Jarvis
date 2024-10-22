'''
message를 관리하고 반환
'''
from collections import defaultdict
messages = defaultdict(defaultdict)
messages['Setting']['ko'] = '설정'
messages['Setting']['ja'] = '設定'
messages['Language']['ko'] = '언어'
messages['Language']['ja'] = '言語'
messages['Speech Recognition']['ko'] = '음성인식'
messages['Speech Recognition']['ja'] = '音声認識'
messages['Speech R.']['ko'] = '음성인식'
messages['Speech R.']['ja'] = '音声認識'
messages['Preloading']['ko'] = '사전로딩'
messages['Preloading']['ja'] = '先読み'
messages['Extra']['ko'] = '기타'
messages['Extra']['ja'] = 'その他'
messages['small, fast (X16)']['ko'] = '작고 빠른(X16)'
messages['small, fast (X16)']['ja'] = '小さくて速い(X16)'
messages['basic (X8)']['ko'] = '기본(X8)'
messages['basic (X8)']['ja'] = '基本(X8)'
messages['large, accurate (X3)']['ko'] = '크고 정확한(X3)'
messages['large, accurate (X3)']['ja'] = '大きくて正確(X3)'
messages['larger, accurater (X1)']['ko'] = '더 크고 정확한(X1)'
messages['larger, accurater (X1)']['ja'] = 'より大きく、より正確(X1)'
messages['Download']['ko'] = '다운로드'
messages['Download']['ja'] = 'ダウンロード'
messages['Test']['ko'] = '테스트'
messages['Test']['ja'] = 'テスト'
messages['Download modules for speech recognition']['ko'] = '음성 인식용 모듈 다운로드'
messages['Download modules for speech recognition']['ja'] = '音声認識用モジュールダウンロード'
messages['Voice']['ko'] = '음성'
messages['Voice']['ja'] = '音声'
messages["Preloads modules when the program is run,\nspeeding up first-time behavior."]['ko'] = '프로그램 구동시 모듈을 미리 읽어서,\n최초 동작을 빠르게 합니다.'
messages["Preloads modules when the program is run,\nspeeding up first-time behavior."]['ja'] = 'プログラム駆動時モジュールを先読みして、\n初期動作を高速化します。'
messages["Preload main character's voice module."]['ko'] = '메인 캐릭터의 음성 모듈을 미리 읽어옵니다.'
messages["Preload main character's voice module."]['ja'] = 'メインキャラクターの音声モジュールを先読みます。'
messages["Preload set speech recoginition module."]['ko'] = '설정된 음성 인식 모듈을 미리 읽어옵니다.'
messages["Preload set speech recoginition module."]['ja'] = '設定された音声認識モジュールを先読みます。'
messages['Downloaded']['ko'] = '다운로드'
messages['Downloaded']['ja'] = 'ダウンロード'
messages['Confirm']['ko'] = '확인'
messages['Confirm']['ja'] = '確認'
messages['Task Success']['ko'] = '작업 성공'
messages['Task Success']['ja'] = '作業成功'
messages['Do you want to download?']['ko'] = '다운로드 받으시겠습니까?'
messages['Do you want to download?']['ja'] = 'ダウンロードしますか？'
messages['of space is required.\n']['ko'] = '의 용량이 필요합니다.\n'
messages['of space is required.\n']['ja'] = 'の容量が必要です。\n'
messages['] have been successfully added to Workspace.\nDo you want to reflect to your [Inworld Name]?']['ko'] = ']이 Workspace에 무사히 추가되었습니다.\nInworld Name에 반영하시겠습니까?'
messages['] have been successfully added to Workspace.\nDo you want to reflect to your [Inworld Name]?']['ja'] = ']がWorkspaceに無事追加されました.\nInworld Nameに反映しますか？'
messages['Do you want to save your current voice settings?']['ko'] = '현재 목소리 설정을 저장하시겠습니까?'
messages['Do you want to save your current voice settings?']['ja'] = '現在の音声設定を保存しますか？'
messages['Do you really want to delete it?']['ko'] = '정말 삭제하시겠습니까?'
messages['Do you really want to delete it?']['ja'] = '本当に削除しますか？'
messages['Want to enable GPU acceleration to voice generation right now?']['ko'] = '음성생성에 GPU 가속을 지금 바로 적용하시겠습니까?'
messages['Want to enable GPU acceleration to voice generation right now?']['ja'] = '音声生成にGPU加速を今すぐ適用してみますか？'
messages['Want to enable voice recognition right now?']['ko'] = '음성인식을 바로 활성화 하시겠습니까?'
messages['Want to enable voice recognition right now?']['ja'] = '音声認識を今すぐ適用してみますか？'
messages['Cancel']['ko'] = '취소'
messages['Cancel']['ja'] = 'キャンセル'
messages['Finish']['ko'] = '완료'
messages['Finish']['ja'] = '完了'
messages['Error']['ko'] = '에러'
messages['Error']['ja'] = 'エラー'
messages['Guidance']['ko'] = '안내'
messages['Guidance']['ja'] = '案内'
messages['The task was canceled.']['ko'] = '작업이 취소되었습니다.'
messages['The task was canceled.']['ja'] = '作業は中止されました。'
messages['The task is completed.']['ko'] = '작업이 완료되었습니다.'
messages['The task is completed.']['ja'] = '作業が完了しました。'
messages['You already have a downloading file.']['ko'] = '이미 다운로드 중인 파일이 있습니다.'
messages['You already have a downloading file.']['ja'] = 'すでにダウンロード中のファイルがあります。'
messages['There is already a character with that name.']['ko'] = '이미 해당 이름을 갖는 캐릭터가 있습니다.'
messages['There is already a character with that name.']['ja'] = 'すでにその名前を持つキャラクターがあります。'
messages['It will be applied at closing the window.']['ko'] = '창을 닫을 때 적용됩니다.'
messages['It will be applied at closing the window.']['ja'] = 'ウィンドウ終了時に適用されます。'
messages['Current version only offers Inworld and Local.']['ko'] = '현재 버전은 Inworld와 Local만 제공합니다.'
messages['Current version only offers Inworld and Local.']['ja'] = '現在のバージョンは[Inworld, Local]のみ提供しています。'
messages['Current version only offers Local.']['ko'] = '현재 버전은 Local만 제공합니다.'
messages['Current version only offers Local.']['ja'] = '現在のバージョンは[Local]のみ提供しています。'
messages['One of the following values is incorrect\n[Workspace]\n[API Key(for workspace)]\n[Inworld Name]']['ko'] = '다음 중 하나의 값이 정확하지 않습니다.\n[Workspace 이름]\n[inworld api key(Workspace용)]\n[Inworld Name]'
messages['One of the following values is incorrect\n[Workspace]\n[API Key(for workspace)]\n[Inworld Name]']['ja'] = '次のいずれかのデータが正しくありません。\n[Workspace名]\n[inworld api key(Workspace用)]\n[Inworld Name]'
messages['Enter your Studio API KEY first.']['ko'] = '우선 Studio API KEY를 입력해주세요.'
messages['Enter your Studio API KEY first.']['ja'] = 'まず、Studio API KEYを入力してください。'
messages[' : save location']['ko'] = '에 저장하였습니다.'
messages[' : save location']['ja'] = 'に保存しました。'
messages['You can only save to a sublocation of the inworld folder.']['ko'] = 'inworld 폴더의 하위 위치에만 저장할 수 있습니다.'
messages['You can only save to a sublocation of the inworld folder.']['ja'] = 'inworldフォルダのサブロケーションにのみ保存できます。'
messages['One of the following values is incorrect.\n[Workspace]\n[Inworld Name]\n[Studio API KEY]']['ko'] = '다음 중 하나의 값이 정확하지 않습니다.\n[Workspace]\n[Inworld Name]\n[Studio API KEY]'
messages['One of the following values is incorrect.\n[Workspace]\n[Inworld Name]\n[Studio API KEY]']['ja'] = '次のいずれかのデータが正しくありません。\n[Workspace]\n[Inworld Name]\n[Studio API KEY]'
messages['Please enter a name.']['ko'] = '이름을 입력해주세요.'
messages['Please enter a name.']['ja'] = '名前を入力してください。'
messages['The JSON file is not valid.']['ko'] = 'json 파일이 정상적이지 않습니다.'
messages['The JSON file is not valid.']['ja'] = 'jsonファイルが正常ではありません。'
messages['Select a JSON file.']['ko'] = 'json 파일을 선택해주세요.'
messages['Select a JSON file.']['ja'] = 'jsonファイルを選択してください。'
messages['You can only store them in the main.exe subfolder.']['ko'] = 'main.exe 하위 폴더에만 저장할 수 있습니다.'
messages['You can only store them in the main.exe subfolder.']['ja'] = 'main.exeサブフォルダにのみ保存できます。'
messages['] : Change Character']['ko'] = ']으로 캐릭터를 변경하시겠습니까?'
messages['] : Change Character']['ja'] = ']にキャラクターを変更しますか？'
messages["\nNo 'AI' is set up."]['ko'] = "\n'AI'가 설정되지 않았습니다."
messages["\nNo 'AI' is set up."]['ja'] = "\n'AI'が設定されていません。"
messages["\nNo 'Animation assets' is set up."]['ko'] = "\n'Animation assets'가 설정되지 않았습니다."
messages["\nNo 'Animation assets' is set up."]['ja'] = "\n'Animation assets'が設定されていません。"
messages["\nNo 'Voice' is set up."]['ko'] = "\n'Voice'가 설정되지 않았습니다."
messages["\nNo 'Voice' is set up."]['ja'] = "\n'Voice'が設定されていません。"
messages['] : Change Main Character']['ko'] = ']으로 메인 캐릭터를 변경하였습니다.'
messages['] : Change Main Character']['ja'] = ']にメインキャラクターを変更しました。'
messages['You cannot delete [arona].']['ko'] = '[arona]는 삭제할 수 없습니다.'
messages['You cannot delete [arona].']['ja'] = '[arona]は削除できません。'
messages['You cannot delete the main character.']['ko'] = '메인 캐릭터는 삭제할 수 없습니다.'
messages['You cannot delete the main character.']['ja'] = 'メインキャラクターは削除できません。'
messages['The key is not valid, or the connection is poor.']['ko'] = '유효한 키가 아니거나, 통신 상태가 좋지 않습니다.'
messages['The key is not valid, or the connection is poor.']['ja'] = '有効なキーでないか、通信状態が悪いです。'
messages['Set Voice to [GPU] in [Settings].']['ko'] = '[설정]에서 Voice를 [GPU]로 설정해주세요.'
messages['Set Voice to [GPU] in [Settings].']['ja'] = '[設定]でVoiceを[GPU]に設定してください。'
messages['The computer is not capable of GPU acceleration.']['ko'] = 'GPU 가속을 사용할 수 없는 컴퓨터입니다.'
messages['The computer is not capable of GPU acceleration.']['ja'] = 'GPU加速を使用できないコンピュータです。'
messages['GPU acceleration is enabled.']['ko'] = 'GPU 가속을 활성화하였습니다.'
messages['GPU acceleration is enabled.']['ja'] = 'GPU加速を起動しました。'
messages['Set up Talk in [Settings].']['ko'] = '[설정]에서 Talk을 설정해주세요.'
messages['Set up Talk in [Settings].']['ja'] = '[設定]でTalkを設定してください。'
messages['Speech recognition is already enabled.']['ko'] = '이미 음성인식이 활성화 되어있습니다.'
messages['Speech recognition is already enabled.']['ja'] = 'すでに音声認識が起動しています。'
messages['The microphone is not detected.']['ko'] = '마이크가 감지되지 않습니다.'
messages['The microphone is not detected.']['ja'] = 'マイクが検知されません。'
messages['Speech recognition is enabled.']['ko'] = '음성 인식을 활성화하였습니다.'
messages['Speech recognition is enabled.']['ja'] = '音声認識を起動しました。'
messages['Speech recognition is not enabled.']['ko'] = '음성 인식이 활성화되지 않았습니다.'
messages['Speech recognition is not enabled.']['ja'] = '音声認識が起動されません。'
messages['Speech recognition is disabled.']['ko'] = '음성인식을 비활성화하였습니다.'
messages['Speech recognition is disabled.']['ja'] = '音声認識を非アクティブ化しました。'
messages['key [ENTER] is not allowed.']['ko'] = '[enter]는 사용하실 수 없습니다.'
messages['key [ENTER] is not allowed.']['ja'] = '[enter]は使用できません。'
messages['Please set [Talk] Option to OFF to avoid conflicts.']['ko'] = '충돌 방지를 위해 [대화] 옵션을 OFF로 설정하세요.'
messages['Please set [Talk] Option to OFF to avoid conflicts.']['ja'] = '衝突を防ぐため、[会話]オプションをOFFにしてください。'
messages['Do you want to start a new conversation?']['ko'] = '새로운 대화를 시작하겠습니까?'
messages['Do you want to start a new conversation?']['ja'] = '新しい会話を始めますか？'
messages['Yes']['ko'] = '네'
messages['Yes']['ja'] = 'はい'
messages['No']['ko'] = '아니오'
messages['No']['ja'] = 'いいえ'
messages['Name']['ko'] = '이름'
messages['Name']['ja'] = '名前'
messages['Input']['ko'] = '입력'
messages['Input']['ja'] = '入力'
messages['Change']['ko'] = '변경'
messages['Change']['ja'] = '変更'
messages['Initialize']['ko'] = '초기화'
messages['Initialize']['ja'] = '初期化'
messages['Free']['ko'] = '무료'
messages['Free']['ja'] = '無料'
messages['Exist']['ko'] = '있음'
messages['Exist']['ja'] = 'あり'
messages['Select']['ko'] = '선택'
messages['Select']['ja'] = '選択'
messages['Catalog']['ko'] = '카탈로그'
messages['Catalog']['ja'] = 'カタログ'
messages["Select the Inworld Workspace that contains the characters you want to use."]['ko'] = "Inworld에서 사용할 캐릭터가 포함된 Workspace를 골라주세요."
messages["Select the Inworld Workspace that contains the characters you want to use."]['ja'] = "Inworldで使用するキャラクターが含まれているWorkspaceを選択してください。"
messages["Choose an API Key that matches your Workspace.\n(Each Workspace has a different API Key)"]['ko'] = "Workspace에 맞는 API Key를 골라주세요.\n(Workspace마다 API Key가 다릅니다.)"
messages["Choose an API Key that matches your Workspace.\n(Each Workspace has a different API Key)"]['ja'] = "Workspaceに合ったAPI Keyを選択してください。\n(WorkspaceごとにAPI Keyが異なります)"
messages["Name of the character registered in Inworld."]['ko'] = "사용할 캐릭터가 Inworld에 등록된 이름"
messages["Name of the character registered in Inworld."]['ja'] = "使用するキャラクターがInworldに登録されている名前"
messages["Select the animation you want the character to use from the animation folder."]['ko'] = "animation 폴더에서 캐릭터가 사용할 애니메이션을 골라주세요."
messages["Select the animation you want the character to use from the animation folder."]['ja'] = "animationフォルダからキャラクターが使用するアニメーションを選択してください。"
messages["idle: idle\nsit: sitting\npick: picking up\nfall: falling (pick)\nthink: chat typing\ntalk: chat answer\nsmile: setting (think)\nwalk: walk\n\n(If there is no corresponding action animation, the animation in parentheses is used. \nIf there is still no animation to use, the idle animation is used.)"]['ko'] = "idle : 평소\nsit : 앉기\npick : 집기\nfall : 낙하 (pick)\nthink : 채팅 입력\ntalk : 채팅 답변\nsmile : 설정(think)\nwalk : 걷기\n\n(해당 동작 애니메이션이 없을 경우, 괄호 속 애니메이션이 사용됩니다. \n그래도 사용할 애니메이션이 없으면 idle 애니메이션이 사용됩니다.)"
messages["idle: idle\nsit: sitting\npick: picking up\nfall: falling (pick)\nthink: chat typing\ntalk: chat answer\nsmile: setting (think)\nwalk: walk\n\n(If there is no corresponding action animation, the animation in parentheses is used. \nIf there is still no animation to use, the idle animation is used.)"]['ja'] = "idle : 通常\nsit : 座る\npick : つまみ\nfall : 落下(pick)\nthink : チャット入力\ntalk : チャット発言\nsmile : 設定(think)\nwalk : 歩く\n\n(該当する動作アニメーションがない場合、括弧内のアニメーションが使用されます。\nそれでも使用するアニメーションがない場合は、idleアニメーションが使用されます。)"
messages["Whether the current animation is enabled or disabled.\n(idle cannot be turned off)"]['ko'] = "현재 애니메이션 사용 여부\n(idle은 해제할 수 없습니다.)"
messages["Whether the current animation is enabled or disabled.\n(idle cannot be turned off)"]['ja'] = "現在のアニメーションの使用有無\n(idleは解除できません。)"
messages["Current animation play length\n(1000 = 1s)"]['ko'] = "현재 애니메이션 재생 길이\n(1000 = 1s)"
messages["Current animation play length\n(1000 = 1s)"]['ja'] = "現在のアニメーションの再生時間\n(1000 = 1s)"
messages["Current animation width"]['ko'] = "현재 애니메이션 넓이"
messages["Current animation width"]['ja'] = "現在のアニメーションの幅"
messages["Current animation height"]['ko'] = "현재 애니메이션 높이"
messages["Current animation height"]['ja'] = "現在のアニメーションの高さ"
messages["Current animation size rate"]['ko'] = "현재 애니메이션 크기 비율"
messages["Current animation size rate"]['ja'] = "現在のアニメーションサイズ比率"
messages["Current animation bottom position\n(see red line on the right canvas)"]['ko'] = "현재 애니메이션 바닥위치\n(우측 캔버스의 붉은 선 참조)"
messages["Current animation bottom position\n(see red line on the right canvas)"]['ja'] = "現在のアニメーションの底位置\n(右側キャンバスの赤線参照)"
messages["Write Name for character"]['ko'] = "캐릭터 이름을 적어주세요."
messages["Write Name for character"]['ja'] = "キャラクター名を書いてください"
messages["The program is free to use and is supported by many generous donors."]['ko'] = "이 프로그램은 무료로 사용할 수 있으며 많은 기부자들의 후원으로 제작되고 있습니다."
messages["The program is free to use and is supported by many generous donors."]['ja'] = "このプログラムは無料で利用することができ、多くのパトロンの後援で制作されています。"
messages["Click Reaction"]['ko'] = "클릭 반응속도"
messages["Click Reaction"]['ja'] = "クリック反応速度 "
messages["Latest"]['ko'] = "최신"
messages["Latest"]['ja'] = "最新"
messages["Updateable"]['ko'] = "갱신가능"
messages["Updateable"]['ja'] = "更新可能"
messages["Run install.exe for the update."]['ko'] = "업데이트를 위해 install.exe를 실행해주세요."
messages["Run install.exe for the update."]['ja'] = "アップデートのためにinstall.exeを実行してください。"
messages["Set to the width of 'idle'"]['ko'] = "'idle'의 넓이로 설정합니다."
messages["Set to the width of 'idle'"]['ja'] = "'idle'の幅に設定します。"
messages["Set to the width of the original"]['ko'] = "원본의 넓이로 설정합니다."
messages["Set to the width of the original"]['ja'] = "元の幅に設定します。"
messages["Multiply the height by the rate of 'idle'"]['ko'] = "높이에 'idle'의 비율을 곱합니다."
messages["Multiply the height by the rate of 'idle'"]['ja'] = "高さに'idle'の比率を掛けます。"
messages["Set to the height of 'idle'"]['ko'] = "'idle'의 높이로 설정합니다."
messages["Set to the height of 'idle'"]['ja'] = "'idle'の高さに設定します。"
messages["Set to the height of the original"]['ko'] = "원본의 높이로 설정합니다."
messages["Set to the height of the original"]['ja'] = "元の高さに設定します。"
messages["Multiply the width by the rate of 'idle'"]['ko'] = "넓이에 'idle'의 비율을 곱합니다."
messages["Multiply the width by the rate of 'idle'"]['ja'] = "幅に'idle'の比率を掛けます。"
messages["Add"]['ko'] = "추가"
messages["Add"]['ja'] = "追加"
messages["Del"]['ko'] = "삭제"
messages["Del"]['ja'] = "削除"
messages["Edit"]['ko'] = "수정"
messages["Edit"]['ja'] = "修正"
messages["Under updating..."]['ko'] = "업데이트 중입니다..."
messages["Under updating..."]['ja'] = "アップデート中です..."
messages["User name"]['ko'] = "유저 이름"
messages["User name"]['ja'] = "ユーザー名"
messages["Languages to use in UI/Settings"]['ko'] = "UI/Setting에서 쓸 언어"
messages["Languages to use in UI/Settings"]['ja'] = "UI/Settingで使う言語"
messages["Volume"]['ko'] = "음량"
messages["Volume"]['ja'] = "音量"
messages["Mute"]['ko'] = "음소거"
messages["Mute"]['ja'] = "ミュート"
messages["Chat response language\n(Questions can be asked in any language)"]['ko'] = "채팅 응답 언어\n(질문은 아무 언어나 OK)"
messages["Chat response language\n(Questions can be asked in any language)"]['ja'] = "チャット応答言語\n(質問はどの言語でもOK)"
messages["Use Web search for chatting"]['ko'] = "채팅에 웹 검색 사용"
messages["Use Web search for chatting"]['ja'] = "チャットにWeb検索を使用"
messages["Start chat with a single left click"]['ko'] = "좌클릭 1회로 채팅시작"
messages["Start chat with a single left click"]['ja'] = "左クリック1回でチャット開始"
messages["keyboard key to start chat\n(click also applies)"]['ko'] = "키보드 키를 눌러서 채팅시작\n(클릭도 적용)"
messages["keyboard key to start chat\n(click also applies)"]['ja'] = "キーボードキーを押してチャット開始\n(Clickも適用)"
messages["Default conversations"]['ko'] = "기본 대화"
messages["Default conversations"]['ja'] = "基本会話"
messages["Web search results are reflected in the answer"]['ko'] = "Web검색 결과를 대답에 반영"
messages["Web search results are reflected in the answer"]['ja'] = "Web検索結果を回答に反映"
messages["Enables conversations about Story elements."]['ko'] = "Story 요소에 대한 대화가 가능"
messages["Enables conversations about Story elements."]['ja'] = "Story要素についての会話が可能"
messages["Translation with AI. Resourcefully not recommended."]['ko'] = "AI를 이용한 번역. 리소스적으로 비추천"
messages["Translation with AI. Resourcefully not recommended."]['ja'] = "AIを使った翻訳。リソース的に非推奨。"
messages["Short-term memory. Reflects recent conversations in the conversation."]['ko'] = "단기기억력. 최근 대화를 대화에 반영"
messages["Short-term memory. Reflects recent conversations in the conversation."]['ja'] = "短期記憶力。最近の会話を会話に反映。"
messages["Long-term memory. It remembers user characteristics and reflects them in conversations."]['ko'] = "장기기억력. 대화를 통해 유저의 특성을 기억하고 대화에 반영"
messages["Long-term memory. It remembers user characteristics and reflects them in conversations."]['ja'] = "長期記憶力。会話を通じてユーザーの特性を記憶し、会話に反映。"
messages["Image recognition. Enables conversations about images\nwithin a specified range or dragged and dropped images."]['ko'] = "이미지 인식기능. 지정된 범위 내의 이미지나\n드래그 앤 드롭 된 이미지에 대한 대화가 가능"
messages["Image recognition. Enables conversations about images\nwithin a specified range or dragged and dropped images."]['ja'] = "画像認識機能。指定された範囲内の画像や\nドラッグ＆ドロップされた画像に対する会話が可能。"
messages["Speech recognition. Enables direct conversation with AI via microphone"]['ko'] = "음성 인식기능. AI와 마이크를 통해 직접 대화 가능"
messages["Speech recognition. Enables direct conversation with AI via microphone"]['ja'] = "音声認識機能。AIとマイクで直接会話が可能"
messages["Fast loading with minimal settings"]['ko'] = "최소설정을 통한 빠른 로딩"
messages["Fast loading with minimal settings"]['ja'] = "最小設定による高速ローディング"
messages["Default. Enable all options"]['ko'] = "기본값. 모든 설정을 활성화"
messages["Default. Enable all options"]['ja'] = "初期設定。すべてのオプションを起動"
messages["Custom. Proceed with the selected option"]['ko'] = "커스텀. 선택된 옵션대로 진행"
messages["Custom. Proceed with the selected option"]['ja'] = "カスタム。選択されたオプション通りに進行"
messages["I'm ready to talk, sensei."]['ko'] = "선생님, 이야기할 준비가 되었습니다."
messages["I'm ready to talk, sensei."]['ja'] = "先生、話す準備はできています。"
messages["Sensei? I can't start a conversation. Could you please check your microphone settings or something?"]['ko'] = "선생님? 대화를 시작할 수 없어요. 마이크 설정 등을 확인해주실 수 있으실까요?"
messages["Sensei? I can't start a conversation. Could you please check your microphone settings or something?"]['ja'] = "先生？ 会話を始めることができません。マイクの設定などをご確認いただけますか？"
messages["Use CPU for Normal response."]['ko'] = "응답에 CPU를 사용"
messages["Use CPU for Normal response."]['ja'] = "応答にはCPUを使用。"
messages["Use Nvidia GPU for fast response.\n(VRAM about 8~10GB needed)"]['ko'] = "빠른응답을 위해 Nvidia GPU 사용.\n(VRAM 약 8~10GB 필요)"
messages["Use Nvidia GPU for fast response.\n(VRAM about 8~10GB needed)"]['ja'] = "高速応答のためにNvidia GPUを使用。\n(VRAM 約8～10GB必要)"
messages["It's already running. Do you want to restart it?"]['ko'] = "이미 구동중입니다. 재기동하시겠습니까?"
messages["It's already running. Do you want to restart it?"]['ja'] = "すでに稼働中です。再起動しますか？"
messages["Restart failed, please try again later."]['ko'] = "재기동에 실패했습니다. 잠시 후 시도해주세요."
messages["Restart failed, please try again later."]['ja'] = "再起動に失敗しました。 しばらくしてから再試行してください。"
messages["Cleaned Preloaded Models"]['ko'] = "사전 로드된 모델 청소"
messages["Cleaned Preloaded Models"]['ja'] = "Cleaned Preloaded Models"
messages["Input Image"]['ko'] = "이미지 입력"
messages["Input Image"]['ja'] = "画像追加"
messages["Web Search"]['ko'] = "웹 검색"
messages["Web Search"]['ja'] = "WEB検索"
messages["Send"]['ko'] = "보내기"
messages["Send"]['ja'] = "転送"
messages["Selecting screenshot area..."]['ko'] = "Screenshot area 선택중..."
messages["Selecting screenshot area..."]['ja'] = "Screenshot area 選択中..."
messages["Focus mode activated"]['ko'] = "Focus Mode 작동"
messages["Focus mode activated"]['ja'] = "Focus Mode 作動"
messages["Focus mode Deactivated"]['ko'] = "Focus Mode 해제"
messages["Focus mode Deactivated"]['ja'] = "Focus Mode 解除"
messages["I'll focus on the focus area, sensei!"]['ko'] = "집중해서 볼게요, 선생님!"
messages["I'll focus on the focus area, sensei!"]['ja'] = "集中して見ますよ、先生！"
messages["I'll turn off focus mode, sensei!"]['ko'] = "집중모드를 해제할게요, 선생님!"
messages["I'll turn off focus mode, sensei!"]['ja'] = "集中モードを解除します、先生！"
messages["Delete"]['ko'] = "삭제"
messages["Delete"]['ja'] = "削除"
messages["Modify"]['ko'] = "수정"
messages["Modify"]['ja'] = "修正"  # 編集, 更新, 変更
messages["Detail"]['ko'] = "상세"
messages["Detail"]['ja'] = "詳細"
messages["AI learning"]['ko'] = "AI 학습"
messages["AI learning"]['ja'] = "AI学習 "
messages["Current Chat"]['ko'] = "현재 채팅"
messages["Current Chat"]['ja'] = "現在チャット"
messages["New Chat"]['ko'] = "새 채팅"
messages["New Chat"]['ja'] = "新規チャット"
messages["Analyze the information to learn from the conversation history."]['ko'] = "대화 내역에서 학습할 정보를 분석합니다."
messages["Analyze the information to learn from the conversation history."]['ja'] = "会話履歴から学習する情報を分析します。"
messages["Suggest title suggestions from conversation history."]['ko'] = "대화 내역에서 제목 후보를 추천합니다."
messages["Suggest title suggestions from conversation history."]['ja'] = "会話履歴からタイトル候補を推薦します。"
# messages["Download"]['ko'] = "다운로드"
# messages["Download"]['ja'] = "ダウンロード"
# messages["Download"]['ko'] = "다운로드"
# messages["Download"]['ja'] = "ダウンロード"
# messages["Download"]['ko'] = "다운로드"
# messages["Download"]['ja'] = "ダウンロード"
# messages["Download"]['ko'] = "다운로드"
# messages["Download"]['ja'] = "ダウンロード"
# messages["Download"]['ko'] = "다운로드"
# messages["Download"]['ja'] = "ダウンロード"
# messages["Download"]['ko'] = "다운로드"
# messages["Download"]['ja'] = "ダウンロード"



messagesSpecial = defaultdict(str)
messagesSpecial['sound option title'] = 'Download modules for speech recognition'
messagesSpecial['sound option tiny'] = 'small, fast (X16)'
messagesSpecial['sound option base'] = 'basic (X8)'
messagesSpecial['sound option small'] = 'large, accurate (X3)'
messagesSpecial['sound option medium'] = 'larger, accurater (X1)'
messagesSpecial['loading option title'] = "Preloads modules when the program is run,\nspeeding up first-time behavior."

def getSpecialMessage(message):
    if message in messagesSpecial:
        return messagesSpecial[message]
    else:
        print("### MesseagesSpecial dict don't have keyword : " + message)        
        return message


def getMessage(message, lang="en", is_special=False):
    # 하드코딩 메뉴들
    if is_special:
        message = getSpecialMessage(message)
    
    # 언어 변수 변환
    if lang == '日本語':
        lang = 'ja'
    if lang == 'English':
        lang = 'en'
    if lang == '한국어':
        lang = 'ko'
    
    # 영어면 그대로 반환
    if lang == 'en':
        return message

    # messages dict에 없으면 원형 반환
    try:
        return messages[message][lang]
    except:
        print("### Messeages dict don't have keyword : " + message)
        return message