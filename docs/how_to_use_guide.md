# 사용 가이드

## 최초 구동

- 개요 : 최초 구동시 옵션 설정

![use_guide_start_cpu](../docs_image/use_guide_start_cpu.png)
![use_guide_start_gpu](../docs_image/use_guide_start_gpu.png)

1. CPU : GPU 가속없이 사용
2. GPU : 빠른응답을 위해 Nvidia GPU를 사용. (VRAM 최대 8GB까지 분배 가능)
3. CPU 옵션 - Fast : 최소한의 모듈만 캐싱
4. CPU 옵션 - Normal : 사용가능한 모든 모듈을 캐싱
5. CPU 옵션 - Custom : 원하는 모듈을 선택하여 사용
6. Custom 상세 화면 : (5)를 선택시 팝업. 원하는 모듈을 선택
7. 사용 VRAM : 최대 8GB까지 입력 가능. (현재 사용가능한 VRAM - 2GB가 선입력되어 있음)
8. 호버 팁 : 특정 UI위에 마우스를 올려두면(hover) 나오는 Tip메시지풍선
9. 확인 : 현재 옵션 설정대로 프로그램을 시작

## 로딩 화면

- 개요 : 옵션 설정 후 확인 버튼을 누르면 모듈 로딩이 시작되고 진행상황을 로딩 화면으로 표시합니다.

![use_guide_start_gpu](../docs_image/use_guide_loading_screen.png)

1. 현재 로딩중인 모듈 및 전체 모듈 중 진행상태

## 기본 조작

- 개요 : 캐릭터 상호작용에 관한 기본 조작입니다.

![interaction](../docs_image/interaction.gif)

좌클릭 : 채팅 시작(채팅 말풍선 보이기)  
좌클릭 드래그 & 드롭 : 캐릭터를 원하는 위치로 이동  
우클릭 : 메뉴  

## UI 설명

- 채팅 말풍선

    ![chatBalloon](../docs_image/use_guide_ui_chatballoon.png)

1. 입력공간 (입력 공간 내에서 엔터 입력시 [4.질문]가 동작합니다.)
2. 대화에 사용할 이미지 추가
3. 웹 검색을 강제한 질문
4. 질문
5. 닫기

- 답변 말풍선 (답변 생성중)

    ![answerBalloon1](../docs_image/use_guide_ui_answerballoon1.png)

1. 답변 중 답변(밝은 하늘색 배경)
2. 중지
3. 음성 다시 재생
4. 표시 언어 변경(한->영->일->한)
5. 재생성
6. 답변 삭제(해당 답변과 질문이 메모리에 저장되지 않음)

- 답변 말풍선 (답변 완료)

    ![answerBalloon2](../docs_image/use_guide_ui_answerballoon2.png)

1. 답변 완료 답변(파란색 배경)
2. 중지
3. 음성 다시 재생
4. 표시 언어 변경(한->영->일->한)
5. 재생성
6. 답변 삭제(해당 답변과 질문이 메모리에 저장되지 않음)
