# Week 11 실습

## 오늘 한 것

- PyInstaller 설치 및 빌드
- resource_path() 함수 추가
- --add-data 옵션으로 에셋 포함
- .exe 실행 확인

## resource_path() 를 써야 하는 이유

- .py를 .exe를 빌드하는 과정에서 pyinstaller가 리소스 파일을 임시 파일에 압축 해제하기 위함
- resource_path가 없을 때는 임시 폴더를 찾지 못하여 오류가 발생함
- resource_path가 있을 때는 올바른 경로로 자동 변환함
- .py로 개발할 때는 문제가 없지만, .exe로 빌드할 때 파일을 찾지 못 하는 것을 방지하기 위함

## 빌드 명령어

- pyinstaller --onefile --windowed --add-data "assets;assets" --name=태웅겜 dodger.py

- dodger.py를 태웅겜.exe로 빌드, 에셋 폴더를 추가

## AI 활용 내역

- "강의의 참고 예시에 나와있는 코드와 내 코드의 파일 로드 방식이 달라,
내 코드에 리소스 패스를 적용한 코드를 보내줘"