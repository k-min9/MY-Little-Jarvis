# 👩‍💻 MY Little JARVIS - 私だけの小さなAIアシスタント

![title](../docs_image/title.png)

## Installer Download : release or <https://shorturl.at/QrFmp>

[Quick installation guide](../docs/installation_guide.md)

## Language

[한국어](../README.md)|日本語|English

## 概要

- 私だけのためのちょっと賢いシステム(Just A Rather Very Intelligent System)
- オープンソースAI(ローカルLLM)で作った自分だけの小さなAIアシスタント

## 背景

現在、Cloud-based AIサービスは、開発者にとって不便でコストがかかるという問題により、AIの収益化が難しくなっており、企業中心のサービスへの移行が加速しています。

[My little Jarvis]プロジェクトは、ローカルLLMを活用し、開発者が費用なしで直接AIシステムを構築・制御できるようにすることで、このような制約を克服することを目指しています。

これにより、個人ユーザーも高価なCloudサービスに依存することなく、実生活に役立つ商業的価値のあるAIアシスタントを活用できるようになります。

## 主な機能

- 対話可能なインターフェース: 慣れ親しんだWindows環境で、AI合成技術で作ったアニメーションを含む画像を持つ秘書と実際に会話するようなインターフェースを提供します。
- オープンソースAIによる回答の推論と生成： LLAMA3.1の量子化AIモデルに基づいて、個人PC環境で自然で迅速な会話を生成します。
- グローバルな言語提供及び詳細設定機能：質問と回答に韓/英/日の言語を選択することができ、キャラクターのインタラクション頻度及びサイズなどを設定することができます。
- メタ認識によるキャラクターの解釈とAI側での会話：AIがキャラクターを解釈し、ユーザーではなくAIが先に話しかける機能を提供し、会話の参入障壁を下げます。
- 意図把握機能：ユーザーの入力を分析して特定のフォーマットで返すことで、会話の文脈を把握し、他の機能と連携することができます。
- メモリ機能：会話内容自体を記憶して次の会話に反映し、会話からユーザーとAIの性格を把握します。
- 画像認識機能：画面の一部または入力された画像をAIアシスタントの入力値として活用することができます。
- Web検索機能：Web検索結果を反映して、最新の情報や必要な情報を会話に活用することができます。
- 音声認識機能：音声認識により会話が可能で、VAD機能で音声と雑音を区別します。
- Easy Installer：ワンクリックでインストールが可能なInstallerを提供し、インストール位置と言語を設定することができます。
- 最適化されたリソースの使用：状況に合わせてCPU/GPUの使用可否を選択することができ、GPU使用時に最適化されたVRAM使用量を推薦してくれます。
- サーバー機能 : Flaskを通じてAPIで出力できるようにし、サーバーとして活用してマルチプラットフォームを構築することができます。

## こんなあなたに必要なプロジェクト

- キャラクターとインタラクションをしたい方
  - 高い拡張性でジャンルを問わず対応できます。
  - 他のプログラム利用中でも会話が可能です。
- 感情的な交流が必要な方
  - 拡大する介護者市場
  - 励ましとフィードバックによるモチベーションの向上
- AIへの高いアクセス障壁が怖い開発者/ユーザー
  - 開発者は小さくはPythonのバージョンから大きくはdllのインストールまで極悪な環境設定が必要ですが、wheelで最も難しい部分のインストールを調整し、開発だけに集中することができます。
  - ユーザーも複雑なrepo cloneやインストールなしでワンクリックで可能なインストール環境を提供します。

## 差別点 : Why JARVIS?

Closed AIが高い利便性と性能を持ち、それに見合った環境とコストが必要であれば、MY-Little-JARVISは高い拡張性とエコシステムを基盤に最適化されたリソースだけで運用可能です。

| **違い**           | **Closed AI(GPT, Claude...)**                  | **Open Source(My Little Jarvis)**          |
|----------------------|-----------------------------------------------|-----------------------------------------------|
| **生態系**           | 大企業中心                                    | オープンソース                                     |
| **技術共有**         | 大企業中心の管理                               | 開発者・ユーザー中心の大規模なグローバルコミュニティ   |
| **費用**             | クラウドベース、従量制料金制使用。高価。           | ローカルベース(+クラウド対応)、無料。              |
| **セキュリティ**             | データがサーバーに送信される可能性がある    | データが外部に送信されない                   |
| **コントロール自由度**    |  設定されたパラメータ内で利用                      | 開発者がパラメータを設定                 |
| **インターネット接続**      | インターネット必須、サーバーに依存             | インターネットなしでもオフラインで動作可能              |
| **サーバーの効率性**           | 必要な機能数だけAPIを呼び出して組み立て      | モジュール組み立てにより、1回の呼び出しで複数の機能を同時に実行  |
| **モデル**             | 固定されたクラウドモデルを使用し、与えられた選択肢から選択   | 様々なモデルを直接所有することができ、軽量化または改造することができる   |
| **ハードウェア**         | 高レベルのハードウェアが必要(個人PC不可)       | レベルに合ったハードウェアで駆動可能(個人PC可能)  |

## Get Started

- [インストールガイド](../docs/installation_guide.md)
- [使用ガイド](../docs/how_to_use_guide.md)

### 追加資料

- [発表資料](../docs/presentation.pptx)

## 主なサービス画面

### インターフェース

- 使用Tool : Stable-Diffusion, ComfyUI
- 使用技術 : Text-to-Image, ControlNet, (+Inpainting), toonCrafter
- 画面で[直観的にインタラクション]するインターフェースをローカルで完成

![interaction](../docs_image/interaction.gif)

### 意図の把握

- [質問にWeb検索が必要か]をAIに考えさせる。

![ai_intent](../docs_image/ai_intent.png)

### Web検索

- Web検索結果を反映した回答機能

![ai_web](../docs_image/ai_web.png)

### 画像認識

- 入力された画像や設定された背景に関する会話機能

![ai_florence](../docs_image/ai_florence.png)

### Tikitaka(高速音声認識会話)

- リアルタイム音声認識による質問と回答

![tikitaka](../docs_image/tikitaka.png)

### 会話履歴管理

- 会話の保存/変更/修正/削除および要約を通じたタイトル推薦機能

![history](../docs_image/history.png)

## 사용 AI 기술

- MY-Little-JARVISは以下のAI技術を使用しました。
  - AI回答生成及び意図把握、翻訳、サーバーなど主要AIモジュール
    - 使用主な技術 : LLama.cpp, langchain, transformers
    - 使用モデル : Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
  - AIキャラクター生成
    - 使用ツール : Stable Diffusion
    - 使用主モデル : Animagine3.1
  - AIキャラクターアニメーション生成
    - 使用ツール : Stable Diffusion, ComfyUI
    - 使用主技術 : AnimateDiff, ToonCrafter
  - Web検索用単語短縮
    - 使用主技術 : sentence-transformers, duckduckgo_search
    - 使用モデル : all-MiniLM-L6-v2
  - AI音声合成
    - 使用技術 : VITS (ISTFTで高速推論)
    - 使用データ : KSSオープンデータ
  - AI音声認識
    - 使用技術 : faster-whisper + sound, VAD
    - 使用モデル：Systran-faster-whisper-small, sillero_vad
  - AI画像認識
    - 使用技術 : Florence2
    - 使用モデル : Microsoft-Florence-2-base
- 外部AIモデル
  - kss_korean_ISTFT.pth
  - Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf
  - Microsoft-Florence
  - Sentence Transformers-all-MiniLM-L6-v2
  - Faster-whisper(small)
  - sillero_vad.onnx

## Special Thanks

- 今回のプロジェクトで使用した[Nexon]の[BlueArchive]IPについて、何度も連絡と問い合わせの結果、[問題があれば対応する]という形でIPの使用を受け入れていただきました。 ([証跡](../docs/special_thanks_nexon.md))
- このプロジェクトはオリジナルリソース、音声、Assetなどの資産を活用せず、[NexonゲームIP使用ガイド](https://member.nexon.com/policy/gameipguide.aspx)を遵守しました。
- この場を借りて感謝の意を表します。
