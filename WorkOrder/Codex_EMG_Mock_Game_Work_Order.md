# Codex 작업 지시서
## Flask 기반 Mock EMG Exercise Game 구현

---

# 1. 프로젝트 목표

Python + Flask 기반의 웹 애플리케이션을 구현한다.

이 프로그램은 향후 실제 EMG 센서 데이터를 이용한 운동 보조/게임 시스템으로 확장하기 위한 **Mock Prototype**이다.

현재 단계에서는 실제 EMG 장비를 연결하지 않는다.

대신 다음 입력 방법을 제공한다.

1. 키보드 입력
2. 웹 UI 슬라이더
3. 자동 생성 Mock EMG 신호

Mock EMG 신호를 이용하여 사용자의 근활성도를 추정하고, 화면의 게임 오브젝트를 움직인다.

최종적으로 실제 EMG 데이터나 ESP32 입력을 연결할 때 게임 로직을 거의 수정하지 않고 `EMG Input Provider`만 교체할 수 있는 구조로 설계한다.

---

# 2. 개발 환경

## Backend

- Python 3.10+
- Flask
- NumPy
- 표준 Python 모듈 우선 사용

필요하다면 다음 라이브러리는 사용할 수 있다.

```txt
Flask
numpy
```

가능하면 초기 Mock 버전에서는 의존성을 최소화한다.

## Frontend

- HTML5
- CSS3
- Vanilla JavaScript

React, Vue 등의 프레임워크는 사용하지 않는다.

---

# 3. 프로젝트 핵심 개념

프로젝트에서 사용할 EMG는 우선 다음 2채널을 기준으로 한다.

```txt
Channel 1 : Biceps EMG
Channel 2 : Triceps EMG
```

Mock 환경에서도 반드시 2개의 채널을 독립적으로 관리한다.

예:

```txt
Biceps
0.00 ────────────── 1.00

Triceps
0.00 ────────────── 1.00
```

실제 시스템에서는 이 값이 다음 흐름으로 들어올 예정이다.

```txt
EMG Sensor
   ↓
ESP32 / DAQ
   ↓
Signal Processing
   ↓
Feature Extraction
   ↓
Muscle Activation
   ↓
Game Control
```

현재 Mock 버전에서는 다음 구조를 사용한다.

```txt
Keyboard / Slider / Mock Generator
              ↓
        Mock EMG Provider
              ↓
        EMG Processor
              ↓
       Game Controller
              ↓
          Web Game
```

---

# 4. 아키텍처 요구사항

입력, EMG 처리, 게임 로직을 서로 분리한다.

권장 구조:

```txt
emg_mock_game/
│
├── app.py
├── requirements.txt
├── README.md
├── config.py
│
├── emg/
│   ├── __init__.py
│   ├── provider.py
│   ├── mock_provider.py
│   └── processor.py
│
├── game/
│   ├── __init__.py
│   └── controller.py
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── game.js
│
└── tests/
    ├── test_processor.py
    └── test_game_controller.py
```

역할은 다음과 같이 분리한다.

### `provider.py`

EMG 입력 인터페이스를 정의한다.

향후 다음 Provider를 추가할 수 있어야 한다.

```txt
MockEMGProvider
ESP32EMGProvider
SerialEMGProvider
FileEMGProvider
```

게임에서는 입력 데이터가 Mock인지 실제 센서 데이터인지 몰라도 되게 한다.

---

# 5. Mock EMG 입력

세 가지 입력 모드를 구현한다.

## MODE 1 — Slider

사용자가 직접 웹에서 다음 값을 조절한다.

```txt
Biceps : 0 ~ 100 %
Triceps : 0 ~ 100 %
```

표시는 다음 두 가지 모두 제공한다.

```txt
Raw activation
Normalized activation
```

현재 Mock에서는 둘이 동일해도 된다.

---

# 6. 키보드 입력

게임을 키보드만으로 테스트할 수 있어야 한다.

다음 키를 사용한다.

```txt
W 또는 ↑
Biceps activation 증가

S 또는 ↓
Biceps activation 감소

D 또는 →
Triceps activation 증가

A 또는 ←
Triceps activation 감소
```

증가/감소량 기본값:

```txt
0.05
```

범위:

```txt
0.0 ~ 1.0
```

절대로 범위를 초과하지 않도록 clamp 처리한다.

예:

```python
value = max(0.0, min(1.0, value))
```

---

# 7. Auto Mock EMG 모드

자동으로 EMG가 변하는 테스트 모드를 구현한다.

예:

```txt
REST
   ↓
Activation 증가
   ↓
Peak
   ↓
Activation 감소
   ↓
REST
```

Biceps와 Triceps에 약간의 random noise를 추가한다.

예상 데이터 형태:

```txt
Biceps  : 0.63
Triceps : 0.12
```

또는

```txt
Biceps  : 0.15
Triceps : 0.71
```

---

# 8. EMG 처리

실제 EMG 신호 처리 모듈을 나중에 붙일 수 있도록 별도의 Processor 클래스를 만든다.

예:

```python
class EMGProcessor:

    def process(self, biceps, triceps):
        ...
```

현재 Mock 단계에서는 다음 값을 계산한다.

```txt
Biceps activation
Triceps activation
Muscle balance
Overall activation
Fatigue proxy
```

---

# 9. Muscle Balance

다음과 같이 계산한다.

```txt
balance = biceps - triceps
```

범위:

```txt
-1 ~ +1
```

해석:

```txt
+ 방향
→ Biceps dominant

0
→ Balanced

- 방향
→ Triceps dominant
```

UI에서 게이지로 표시한다.

---

# 10. Overall Activation

다음과 같이 계산한다.

```txt
overall_activation =
(biceps + triceps) / 2
```

범위:

```txt
0 ~ 1
```

---

# 11. Mock Fatigue Index

현재는 실제 근피로도 알고리즘을 구현하지 않는다.

Mock Prototype용 피로도를 구현한다.

지속적으로 높은 EMG activation이 유지되면 fatigue가 증가하고, 휴식하면 감소한다.

개념:

```txt
activation > threshold
       ↓
fatigue 증가

activation < threshold
       ↓
fatigue 회복
```

예:

```python
if overall_activation > 0.6:
    fatigue += 0.005
else:
    fatigue -= 0.003
```

범위:

```txt
0.0 ~ 1.0
```

반드시 clamp 처리한다.

이 값은 **실제 생리학적 피로도 값이 아니라 게임 테스트용 Mock 값**임을 코드와 README에 명확하게 명시한다.

---

# 12. 운동 강도 목표

사용자가 운동 강도 목표치를 설정할 수 있도록 한다.

예:

```txt
Target Activation

MIN : 40%
MAX : 70%
```

이 경우:

```txt
0 ~ 40%
LOW

40 ~ 70%
GOOD

70% 이상
OVER
```

---

# 13. 게임 기본 컨셉

게임 이름:

```txt
EMG Flight
```

화면에 작은 캐릭터 또는 공을 표시한다.

화면 구성 예:

```txt
┌─────────────────────────────────────┐
│            EMG FLIGHT               │
│                                     │
│              TARGET                 │
│                 ●                   │
│                                     │
│        ● Player                     │
│                                     │
│─────────────────────────────────────│
│ Biceps     ███████░░ 72%            │
│ Triceps    ███░░░░░░ 31%            │
│ Fatigue    ████░░░░░ 42%            │
└─────────────────────────────────────┘
```

---

# 14. 게임 조작 방식

Biceps activation이 캐릭터의 상승력을 결정한다.

예:

```txt
Biceps ↑
→ Player 상승

Biceps ↓
→ Player 하강
```

Triceps는 캐릭터의 안정성을 조절하도록 한다.

예:

```txt
Biceps 활성 + Triceps 적절

→ 안정적인 움직임
```

과도한 공동수축:

```txt
Biceps ↑
Triceps ↑

→ Co-contraction 상태
→ 이동 효율 감소
```

---

# 15. 첫 번째 게임 목표

화면 우측에서 왼쪽으로 이동하는 Target Ring을 생성한다.

Player는 적절한 근활성도로 고도를 조절하여 Target Ring을 통과한다.

개념:

```txt
                ○
                │
     ●──────────┘
 Player       Target
```

Target을 통과하면:

```txt
+100 Score
```

---

# 16. 운동 강도에 따른 게임 피드백

Target Activation Range를 이용한다.

### LOW

```txt
근활성도가 너무 낮습니다.
```

Player의 상승력이 부족하게 한다.

### GOOD

```txt
좋은 운동 강도입니다.
```

Player가 정상적으로 움직인다.

### OVER

```txt
강도가 너무 높습니다.
```

화면에 경고한다.

```txt
OVER ACTIVATION
```

계속 유지하면 fatigue가 빠르게 증가하도록 한다.

---

# 17. Fatigue 기반 게임 변화

Fatigue가 높아질수록 캐릭터의 성능이 감소하도록 구현한다.

예:

```txt
fatigue 0 ~ 0.4
정상

fatigue 0.4 ~ 0.7
이동 효율 약간 감소

fatigue > 0.7
운동 강도 감소 권장
```

Fatigue가 0.85 이상이면 다음 메시지를 표시한다.

```txt
REST RECOMMENDED
```

게임을 강제 종료하지는 않는다.

---

# 18. 실시간 그래프

최근 일정 구간의 EMG activation history를 표시한다.

그래프:

```txt
Biceps
Triceps
Fatigue
```

외부 그래프 라이브러리를 사용하지 않고 HTML Canvas를 우선 사용한다.

최근 약:

```txt
10초
```

정도의 데이터를 표시한다.

---

# 19. Dashboard UI

화면 우측 또는 상단에 Dashboard를 구성한다.

표시 항목:

```txt
Biceps Activation
Triceps Activation
Overall Activation
Muscle Balance
Fatigue
Target Range
Score
Game Time
Input Mode
```

---

# 20. 입력 모드 선택

UI에서 선택 가능하도록 한다.

```txt
INPUT MODE

[ Keyboard ]
[ Slider ]
[ Auto Mock ]
```

선택된 모드가 화면에 표시되어야 한다.

---

# 21. 게임 상태

게임은 다음 State를 가진다.

```txt
READY
PLAYING
PAUSED
FINISHED
```

버튼:

```txt
START
PAUSE
RESET
```

---

# 22. Flask API

최소 다음 API를 구현한다.

## GET `/`

메인 게임 페이지

## POST `/api/emg`

Mock EMG 입력 업데이트

예:

```json
{
  "biceps": 0.62,
  "triceps": 0.21
}
```

응답:

```json
{
  "biceps": 0.62,
  "triceps": 0.21,
  "overall_activation": 0.415,
  "balance": 0.41,
  "fatigue": 0.23
}
```

## GET `/api/state`

현재 상태 반환

예:

```json
{
  "biceps": 0.62,
  "triceps": 0.21,
  "overall_activation": 0.415,
  "balance": 0.41,
  "fatigue": 0.23,
  "score": 400,
  "game_state": "PLAYING"
}
```

## POST `/api/reset`

게임 상태 초기화

---

# 23. 데이터 구조

게임 상태를 한 객체에서 관리한다.

예:

```txt
GameState
```

포함할 값:

```txt
biceps
triceps
overall_activation
balance
fatigue
score
game_time
game_state
input_mode
target_min
target_max
```

---

# 24. 실제 EMG 확장을 위한 인터페이스

Mock 코드와 실제 EMG 코드를 분리한다.

예:

```python
class EMGProvider:

    def get_sample(self):
        raise NotImplementedError
```

Mock:

```python
class MockEMGProvider(EMGProvider):

    def get_sample(self):
        ...
```

향후:

```python
class ESP32EMGProvider(EMGProvider):

    def get_sample(self):
        ...
```

이렇게 변경 가능하게 한다.

다음과 같은 코드를 게임 내부에 직접 넣으면 안 된다.

```python
serial.Serial(...)
```

Sensor communication은 반드시 Provider 계층에서 처리하도록 한다.

---

# 25. 향후 실제 EMG 처리 확장 고려

실제 시스템에서는 다음 파이프라인을 추가할 예정이다.

```txt
Raw EMG
↓
Band-pass filtering
↓
Rectification
↓
Envelope
↓
Windowing
↓
Feature extraction
↓
MVC normalization
↓
Activation estimation
↓
Fatigue estimation
↓
Game controller
```

현재 Mock 버전에서는 구현하지 않는다.

그러나 나중에 다음 형태로 확장 가능해야 한다.

```python
processor.process(raw_emg)
```

---

# 26. UI 디자인

게임 느낌이 나도록 구성한다.

권장 스타일:

```txt
Dark background
Neon / medical-tech dashboard
Large game area
EMG gauges
Status indicators
```

다만 디자인보다 기능 구현을 우선한다.

PC 웹 환경을 기준으로 한다.

최소 해상도:

```txt
1280 × 720
```

창 크기가 변경되어도 주요 요소가 잘리지 않도록 responsive layout을 적용한다.

---

# 27. 화면 구성

권장 레이아웃:

```txt
┌─────────────────────────────────────────────────┐
│ EMG EXERCISE GAME                               │
├──────────────────────────────┬──────────────────┤
│                              │ Biceps           │
│                              │ ███████ 72%      │
│                              │                  │
│          GAME                │ Triceps          │
│          SCREEN              │ ███ 31%          │
│                              │                  │
│                              │ Fatigue          │
│                              │ ████ 42%         │
├──────────────────────────────┴──────────────────┤
│ EMG HISTORY GRAPH                              │
├─────────────────────────────────────────────────┤
│ INPUT MODE │ START │ PAUSE │ RESET             │
└─────────────────────────────────────────────────┘
```

---

# 28. 단위 테스트

최소 다음 테스트를 작성한다.

## EMG Processor

테스트:

```txt
activation calculation
balance calculation
fatigue increase
fatigue recovery
clamping
```

예:

```txt
biceps = 1.5
```

입력이 들어와도:

```txt
1.0
```

이 되도록 한다.

---

# 29. 브라우저 입력 예외 처리

다음 문제를 방지한다.

```txt
키를 계속 누르는 경우 activation > 1
키 입력이 게임 외 UI 입력창에도 전달되는 문제
게임 RESET 후 이전 animation loop가 남는 문제
START 버튼 여러 번 클릭 시 loop 중복 실행
PAUSE 후 resume 시 speed 증가
```

animation loop는 하나만 유지하도록 한다.

---

# 30. 최초 실행 검증

처음부터 모든 기능을 구현하지 말고 다음 순서로 진행한다.

먼저 최소 Flask 서버를 구성하고 실행한다.

```bash
python app.py
```

초기 실행 과정에서 다음 오류 가능성을 먼저 확인한다.

```txt
ModuleNotFoundError
TemplateNotFound
404 static resource
port already in use
JavaScript fetch 404
JSON serialization error
```

실제로 실행해서 오류를 확인하고 수정한 다음 다음 단계로 진행한다.

오류를 숨기거나 예외를 단순히 무시하지 않는다.

---

# 31. 구현 순서

다음 순서를 반드시 따른다.

### STEP 1
프로젝트 디렉터리 생성

### STEP 2
Flask 최소 서버 생성

### STEP 3
`/` 페이지 접속 테스트

### STEP 4
Mock EMG state 구현

### STEP 5
`/api/emg` 구현

### STEP 6
Slider 입력 구현

### STEP 7
Keyboard 입력 구현

### STEP 8
Auto Mock 입력 구현

### STEP 9
EMG Processor 구현

### STEP 10
Game Canvas 구현

### STEP 11
Player physics 구현

### STEP 12
Target 생성

### STEP 13
Collision detection

### STEP 14
Score

### STEP 15
Fatigue system

### STEP 16
Dashboard

### STEP 17
Realtime EMG graph

### STEP 18
START / PAUSE / RESET

### STEP 19
unit test

### STEP 20
전체 실행 검증

---

# 32. 중요 구현 원칙

다음 원칙을 반드시 지킨다.

1. HTML이나 JavaScript 내부에 Python 알고리즘을 중복 구현하지 않는다.
2. 게임 물리와 EMG 처리 로직을 분리한다.
3. 실제 EMG 입력을 추가할 수 있는 구조로 만든다.
4. Mock Fatigue를 실제 의학적 근피로도 분석 결과처럼 표현하지 않는다.
5. 모든 activation 값은 `0.0 ~ 1.0`으로 관리한다.
6. 게임 rendering은 JavaScript에서 처리한다.
7. EMG 계산 및 상태 관리는 Python Backend 중심으로 작성한다.

---

# 33. README 작성

README에는 다음 내용을 포함한다.

```txt
Project Description
Architecture
Directory Structure
Installation
Execution
Keyboard Controls
Input Modes
API
Mock Fatigue Disclaimer
Future EMG Integration
```

실행:

```bash
pip install -r requirements.txt
python app.py
```

접속:

```txt
http://127.0.0.1:5000
```

---

# 34. Checklist

- [ ] Flask 서버 정상 실행
- [ ] `/` 페이지 정상 접속
- [ ] CSS 정상 로드
- [ ] JS 정상 로드
- [ ] Biceps Mock 입력 동작
- [ ] Triceps Mock 입력 동작
- [ ] Slider 입력 동작
- [ ] Keyboard 입력 동작
- [ ] Auto Mock 입력 동작
- [ ] Input Mode 전환 가능
- [ ] activation 0~1 clamp
- [ ] Overall Activation 계산
- [ ] Muscle Balance 계산
- [ ] Mock Fatigue 계산
- [ ] Player 움직임 정상
- [ ] Target 움직임 정상
- [ ] Collision detection 정상
- [ ] Score 증가 정상
- [ ] LOW / GOOD / OVER 판정
- [ ] REST RECOMMENDED 표시
- [ ] 실시간 그래프 정상
- [ ] START 정상
- [ ] PAUSE 정상
- [ ] RESET 정상
- [ ] animation loop 중복 없음
- [ ] Flask API 정상
- [ ] 테스트 통과
- [ ] README 작성
- [ ] 실제 ESP32 Provider 확장 가능

---

# 35. TODO

## Priority 1 — Mock Prototype

- [ ] Flask 프로젝트 생성
- [ ] Game UI 생성
- [ ] 2-channel EMG Mock 입력
- [ ] Keyboard control
- [ ] Slider control
- [ ] Auto EMG generator
- [ ] EMG Processor
- [ ] Player control
- [ ] Target game
- [ ] Score system
- [ ] Fatigue mock
- [ ] Dashboard
- [ ] Graph

## Priority 2 — 안정화

- [ ] unit test
- [ ] input validation
- [ ] duplicate animation loop 방지
- [ ] Flask exception handling
- [ ] browser resize 대응
- [ ] README 작성

## Priority 3 — 향후 확장

현재 단계에서는 구현하지 말고 구조만 고려한다.

- [ ] ESP32 serial input
- [ ] 실제 EMG filtering
- [ ] RMS
- [ ] MAV
- [ ] MVC normalization
- [ ] Median Frequency
- [ ] Mean Frequency
- [ ] fatigue classifier
- [ ] trained ML/DL model integration
- [ ] 사용자별 calibration
- [ ] 운동 기록 저장
- [ ] 사용자 profile
- [ ] 운동량 기반 adaptive threshold

---

# 36. 완료 조건

다음 시나리오를 직접 테스트한다.

## Test 1

프로그램 실행:

```bash
python app.py
```

브라우저:

```txt
http://127.0.0.1:5000
```

정상 접속되어야 한다.

## Test 2

Keyboard Mode 선택 후 `W` 입력 시 Biceps 값이 올라가고 Player가 상승해야 한다.

## Test 3

Biceps activation이 목표 범위에 들어오면 `GOOD` 표시.

## Test 4

Biceps activation을 과도하게 높이면 `OVER ACTIVATION` 표시 및 Fatigue 증가.

## Test 5

activation을 낮추면 Fatigue 감소.

## Test 6

Player가 Target을 통과하면 `Score +100`.

## Test 7

RESET 실행 후 다음이 초기화되어야 한다.

```txt
Score = 0
Fatigue = 0
Player position reset
Game time reset
```

---

# 37. 작업 완료 후 반드시 보고할 내용

Codex는 구현 완료 후 다음 형식으로 결과를 보고한다.

```txt
1. 생성된 파일 목록
2. 프로젝트 구조
3. 구현된 기능
4. 실행 방법
5. 테스트 결과
6. 발견된 오류와 수정 내용
7. 현재 Mock 처리된 부분
8. 실제 EMG 연결 시 변경해야 할 파일
9. 향후 구현 권장 순서
```

단순히 "완료했습니다"라고 보고하지 않는다.

실제로 생성된 파일과 실행 결과를 기준으로 보고한다.

---

# 38. 최종 목표 아키텍처와의 연결

현재 구현해야 할 범위:

```txt
Mock EMG
    ↓
EMG Processor
    ↓
Game Controller
    ↓
Flask API
    ↓
HTML / JS Game
```

향후:

```txt
Biceps EMG ─┐
            ├─ ESP32
Triceps EMG ┘
       ↓
Raw EMG Processing
       ↓
Feature Extraction
       ↓
ML / DL Model
       ↓
Activation / Fatigue
       ↓
Game Controller
       ↓
Web Game
```

따라서 이번 작업에서는 **게임 자체보다 실제 EMG 시스템으로 교체 가능한 소프트웨어 아키텍처를 만드는 것을 중요하게 생각한다.**

기존 Mock Game 로직 내부에 ESP32, Serial 또는 특정 센서 종속 코드를 직접 삽입하지 않는다.
