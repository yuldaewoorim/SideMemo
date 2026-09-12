# SideMemo

> `dist\\SideMemo\\SideMemo.exe`를 직접 배포할 때는 `_internal` 폴더도 반드시 같은 위치에 함께 복사해야 합니다. 설치 파일(`installer\\SideMemo-Setup.exe`)은 두 항목을 자동으로 함께 설치합니다.

Windows 화면 가장자리에서 열고 닫는 상단 고정 메모 앱입니다.

## 실행 파일 만들기

1. `build_exe.bat`를 실행합니다.
2. `dist\SideMemo\SideMemo.exe`가 생성됩니다.
3. Inno Setup 6에서 `SideMemo.iss`를 열어 Compile하면 `installer\SideMemo-Setup.exe` 설치 파일이 생성됩니다.

## 기본 사용법

- `Ctrl + Alt + M`: 창 표시 및 앞으로 가져오기
- 메모에서 마우스를 떼면 설정된 시간 후 세로 탭 상태로 접힙니다.
- 탭을 클릭하면 메모를 열고, ⚙에서 전체·탭별 설정을 변경합니다.
- 창을 닫으면 종료되지 않고 트레이로 숨습니다.
- 백업 내보내기는 메모와 첨부 이미지를 하나의 `.zip` 파일로 저장합니다.
