# 🏛️ BITWING — AI 비서 시스템 통합 기획서 v2.0

> *"Bitwing(비트윙) — Bit(디지털) + Wing(날개). 디지털 날개로 업무를 비상시키다."*
>
> AI 매니저들이 업무를 전담 처리하는 전략적 비서 시스템
> *(Bitwing은 등록 상표입니다)*

**문서 버전**: v2.0 | 2026-03-29

---

# 📋 목차

1. 프로젝트 정체성
2. 시스템 아키텍처
3. AI 매니저 시스템
4. 기술 스택
5. 서버 코어 (Bitwing Core)
6. 데스크탑 앱 (Bitwing Desktop)
7. 모바일 앱 (Bitwing Mobile)
8. 웹 대시보드 (Bitwing Dashboard)
9. 외부 서비스 연동
10. 데이터베이스 설계
11. API 설계
12. AI 엔진 (Claude 연동)
13. 개발 환경 구축
14. 프로젝트 디렉토리 구조
15. 개발 로드맵
16. 보안 정책

이 문서는 모든 기존 기획 문서(PLANNING, BITWING_OVERVIEW, DESKTOP_PLANNING, DEV_SETUP, PROJECT_NAMING)를 하나로 통합한 마스터 플랜입니다.

---

# 1. 프로젝트 정체성

## 1.1 네이밍

- **프로젝트명**: Bitwing (비트윙)
- **유래**: Bit(디지털 데이터) + Wing(날개) — 디지털 날개로 업무를 비상시키는 AI 비서
- **슬로건**: "Your Strategic AI Assistant"
- **상표권**: 등록 상표 (bitwing)
- **성격**: 프로페셔널, 전략적, 신뢰감

## 1.2 네이밍 체계

- 🏛️ **Bitwing** (`bitwing`) — AI 비서 통합 시스템
- ⚙️ **Bitwing Core** (`bitwing-core`) — FastAPI + Claude AI + MySQL
- 🖥️ **Bitwing Desktop** (`bitwing-desktop`) — PySide6 시스템 트레이 + 음성
- 📱 **Bitwing Mobile** (`bitwing-mobile`) — Flutter (Android + iOS)
- 🌐 **Bitwing Dashboard** (`bitwing-dashboard`) — React 웹 관리

## 1.3 목적

- AI 매니저(1~5명)가 각 업무를 전담 처리하고 사용자에게 보고
- 음성 명령으로 모든 업무 처리 (데스크탑/핸드폰 마이크)
- 외부 앱 연동: Google 캘린더, 이메일, 메모앱, 금융/가계부
- 사원 PC 관리: 10~50대 (Windows/Linux 혼합)
- 모든 플랫폼: Windows + Android + iOS + 웹
- 단독 사용자 (관리자 본인)
- AI100 시스템 크롤링/로컬 프로그램 전체 활용

---

# 2. 시스템 아키텍처

## 2.1 전체 구조

```
┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ Bitwing Mobile  │ │ Bitwing Desktop │ │Bitwing Dashboard│ │  Bitwing Web    │
│ (Flutter)     │ │ (PySide6)     │ │ (React)       │ │  (모바일웹)   │
│ Android+iOS   │ │ Windows       │ │ 관리/모니터링 │ │               │
│ 🎤 음성      │ │ 🎤 음성      │ │ 📊 대시보드   │ │               │
│ 💬 챗봇      │ │ 💬 팝업채팅  │ │ 📁 파일관리   │ │               │
│ 🔔 푸시알림  │ │ 🖥️ PC제어    │ │ 👥 매니저관리 │ │               │
└──────┬────────┘ └──────┬────────┘ └──────┬────────┘ └──────┬────────┘
       │                  │                  │                  │
       └──────────────────┼──────────────────┼──────────────────┘
                          │ REST API + WebSocket (HTTPS)
                          │
       ┌──────────────────▼──────────────────────────────────────┐
       │              Bitwing Core (AI100 서버)                     │
       │                                                          │
       │  ┌────────────────────────────────────────────────────┐  │
       │  │ FastAPI Gateway — 인증 · 라우팅 · WebSocket        │  │
       │  └───────────────────────┬────────────────────────────┘  │
       │                          │                                │
       │  ┌───────────────────────▼────────────────────────────┐  │
       │  │           AI 매니저 디스패처                        │  │
       │  │  사용자 명령 → 적합한 매니저에게 배분              │  │
       │  └───────────────────────┬────────────────────────────┘  │
       │                          │                                │
       │  ┌────────┬────────┬─────┴───┬────────┬────────┐        │
       │  │📅 일정 │💼 업무 │💰 재무  │🖥️ IT  │📊 보고 │        │
       │  │매니저  │매니저  │매니저   │매니저  │매니저  │        │
       │  │캘린더  │할일    │가계부   │PC관리  │리포트  │        │
       │  │구글연동│메모    │금융     │원격제어│일일요약│        │
       │  │알림    │이메일  │OCR     │모니터링│통계    │        │
       │  │        │파일관리│크롤링   │AI100   │        │        │
       │  └────────┴────────┴─────────┴────────┴────────┘        │
       │                          │                                │
       │  ┌───────────────────────▼────────────────────────────┐  │
       │  │ MySQL │ 파일스토리지(퍼블릭자료) │ 외부API연동     │  │
       │  └────────────────────────────────────────────────────┘  │
       │  ┌────────────────────────────────────────────────────┐  │
       │  │ 기존 AI100 시스템: 크롤러·로컬프로그램·사원PC에이전트│  │
       │  └────────────────────────────────────────────────────┘  │
       └──────────────────────────────────────────────────────────┘
```

## 2.2 클라이언트별 역할

| 기능 | Mobile(Flutter) | Desktop(PySide6) | Dashboard(React) |
|------|----------------|-------------------|-------------------|
| 음성 명령 | ✅ | ✅ | ❌ |
| 채팅 UI | ✅ 전체화면 | ✅ 팝업 | ✅ 웹챗 |
| TTS 응답 | ✅ | ✅ | ❌ |
| 알림 | 푸시(FCM/APNS) | 토스트 | 브라우저 |
| 로컬PC제어 | ❌ | ✅ | ❌ |
| 단축키 | ❌ | ✅ | ❌ |
| 파일/권한관리 | 조회 | 조회+편집 | ✅전체 |
| 퍼블릭자료 | 조회/다운 | 조회/업로드 | ✅전체 |
| 매니저상태 | 간략 | 간략 | ✅상세 |
| 가계부 | ✅입력/조회 | ✅입력/조회 | ✅리포트 |
| 영수증OCR | ✅카메라 | ❌ | 업로드 |

---

# 3. AI 매니저 시스템

## 3.1 개념

Bitwing 안에 AI 매니저(가상 에이전트) 1~5명이 각 업무 전담. 사용자 명령 → 디스패처가 적합한 매니저에게 배분 → 처리 후 보고.

## 3.2 매니저 구성

| 매니저 | 코드명 | 담당 | 연동 |
|--------|--------|------|------|
| 📅 일정 매니저 | `schedule_mgr` | 캘린더, 일정, 알림 | Google Calendar |
| 💼 업무 매니저 | `task_mgr` | 할일, 메모, 이메일, 파일 | Gmail, Outlook, 메모앱 |
| 💰 재무 매니저 | `finance_mgr` | 가계부, 금융, 통장정리, 영수증 | 은행API, OCR, 크롤링 |
| 🖥️ IT 매니저 | `it_mgr` | 사원PC 관리, 시스템 감독 | AI100, 원격 에이전트 |
| 📊 보고 매니저 | `report_mgr` | 리포트, 통계 분석 | 모든 매니저 데이터 종합 |

## 3.3 디스패처 흐름

```
사용자: "이번 달 식비 얼마 썼어?"
  → Claude 의도분석: finance.category_summary
  → 디스패처: 💰 재무 매니저에게 배분
  → 재무 매니저: DB 조회 + 분석 + 자연어 보고
  → 응답: "이번 달 식비는 680,000원입니다. 지난달 대비 5.6% 감소."
```

## 3.4 매니저 상태 대시보드

```
📅 일정 매니저    [🟢 대기중]    작업: 0건
💼 업무 매니저    [🟡 처리중]    작업: 2건
💰 재무 매니저    [🟢 대기중]    작업: 0건
🖥️ IT 매니저     [🟡 처리중]    작업: 1건
📊 보고 매니저    [🟢 대기중]    작업: 0건
```

서버 용량에 따라 1~5명 동적 조절. 각 매니저 독립 Claude API 세션.

---

# 4. 기술 스택

## 4.1 서버 (Bitwing Core)

| 구분 | 기술 |
|------|------|
| OS | Ubuntu (AI100 서버) |
| 백엔드 | Python 3.10+ / FastAPI |
| DB | MySQL |
| AI | Anthropic Claude API |
| 통신 | REST API + WebSocket |
| 작업큐 | Celery + Redis |
| 크롤링 | Scrapy / Playwright |
| OCR | Tesseract / Google Vision |
| 파일스토리지 | 로컬 (/data/bitwing/) |

## 4.2 데스크탑 (Bitwing Desktop)

| 구분 | 기술 |
|------|------|
| OS | Windows (192.168.219.111) |
| GUI | **PySide6** |
| STT | speech_recognition + Google |
| TTS | pyttsx3 |
| 단축키 | pynput |
| HTTP | httpx |
| WebSocket | websockets |
| 시스템 | subprocess + psutil |

## 4.3 모바일 (Bitwing Mobile)

| 구분 | 기술 |
|------|------|
| 프레임워크 | **Flutter** (Dart) |
| 지원OS | **Android + iOS** |
| STT | speech_to_text |
| TTS | flutter_tts |
| HTTP | dio |
| 푸시 | Firebase (FCM + APNS) |
| 상태관리 | Riverpod |
| 차트 | fl_chart |

## 4.4 웹 대시보드 (Bitwing Dashboard)

| 구분 | 기술 |
|------|------|
| 프레임워크 | **React 18** + TypeScript |
| UI | Ant Design 또는 MUI |
| 차트 | Recharts |
| 상태관리 | Zustand |
| HTTP | Axios |
| 빌드 | Vite |
| 호스팅 | AI100 Nginx |

---

# 5. 서버 코어 (Bitwing Core)

## 5.1 음성 명령 → 매니저 배분 예시

| 음성 명령 | 매니저 | 의도 |
|-----------|--------|------|
| "내일 오후 2시에 회의" | 📅 일정 | schedule.create |
| "구글 캘린더 동기화" | 📅 일정 | schedule.sync_google |
| "이번주 할일 보여줘" | 💼 업무 | task.list |
| "읽지 않은 메일 확인" | 💼 업무 | task.email_unread |
| "카드 사용내역 보여줘" | 💰 재무 | finance.transactions |
| "영수증 등록해줘" | 💰 재무 | finance.receipt_ocr |
| "이번달 지출 리포트" | 💰 재무 | finance.monthly_report |
| "김과장 PC 상태 확인" | 🖥️ IT | it.pc_status |
| "오늘 업무 요약" | 📊 보고 | report.daily |

## 5.2 퍼블릭 자료 관리

```
/data/bitwing/
├── public/           # 퍼블릭 (대시보드에서 권한 관리)
│   ├── documents/
│   ├── reports/
│   ├── receipts/
│   └── shared/
├── private/          # 비공개 (금융 등)
└── temp/             # 임시
```

대시보드에서 폴더별 권한 설정, 매니저별 접근 제어.

## 5.3 서버 requirements.txt

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
websockets==14.1
sqlalchemy==2.0.36
mysqlclient==2.2.6
alembic==1.14.0
anthropic==0.42.0
celery==5.4.0
redis==5.2.1
python-jose[cryptography]==3.3.0
python-dotenv==1.0.1
pydantic-settings==2.7.0
httpx==0.28.1
google-api-python-client==2.150.0
google-auth-oauthlib==1.2.1
pytesseract==0.3.13
Pillow==11.0.0
playwright==1.49.0
beautifulsoup4==4.12.3
openpyxl==3.1.5
python-dateutil==2.9.0
loguru==0.7.3
```

---

# 6. 데스크탑 앱 (Bitwing Desktop)

## 6.1 시스템 트레이 메뉴

```
🎤 음성 명령 (Ctrl+Shift+M)
💬 채팅 열기 (Ctrl+Shift+C)
──────────────
📅 오늘 일정
✅ 할일 목록
📝 빠른 메모
💰 오늘 지출
📊 일일 리포트
👥 매니저 상태
──────────────
⚙️ 설정
❌ 종료
```

## 6.2 단축키

| 단축키 | 기능 |
|--------|------|
| Ctrl+Shift+M | 음성 입력 |
| Ctrl+Shift+C | 채팅 윈도우 |
| Ctrl+Shift+N | 빠른 메모 |
| Ctrl+Shift+T | 오늘 할일 |
| Ctrl+Shift+R | 일일 리포트 |

## 6.3 로컬 PC 제어

"메모장 열어줘", "다운로드 폴더 열어", "스크린샷 찍어", "클립보드 메모해줘", "시스템 상태 알려줘", "볼륨 올려"

## 6.4 requirements.txt

```
PySide6==6.8.0
SpeechRecognition==3.11.0
pyttsx3==2.98
PyAudio==0.2.14
pynput==1.7.7
httpx==0.28.1
websockets==14.1
psutil==6.1.0
pyperclip==1.9.0
mss==9.0.2
Pillow==11.0.0
python-dotenv==1.0.1
loguru==0.7.3
```

## 6.5 설정 파일

`C:\Users\Public\bitwing\bitwing-desktop\config\config.ini`

```ini
[server]
url = http://AI100서버IP:8000
api_key = your-bitwing-api-key
websocket_url = ws://AI100서버IP:8000/api/v1/ws

[voice]
stt_engine = google
tts_engine = pyttsx3
tts_language = ko
silence_timeout = 2.0

[hotkeys]
voice_input = ctrl+shift+m
chat_window = ctrl+shift+c

[notifications]
enabled = true
sound = true

[appearance]
theme = system
```

---

# 7. 모바일 앱 (Bitwing Mobile)

## 7.1 Flutter — Android + iOS 동시 지원

주요 화면: 홈(챗봇), 캘린더, 할일, 메모, 가계부, 영수증(카메라OCR), 매니저상태, 설정

## 7.2 주요 패키지 (pubspec.yaml)

```yaml
dependencies:
  dio: ^5.4.0
  web_socket_channel: ^2.4.0
  speech_to_text: ^6.6.0
  flutter_tts: ^4.0.0
  flutter_riverpod: ^2.5.0
  firebase_messaging: ^15.0.0
  camera: ^0.11.0
  fl_chart: ^0.68.0
  table_calendar: ^3.1.0
```

## 7.3 연동 시나리오

- 핸드폰에서 "점심 12,000원" → 재무 매니저 기록 → 데스크탑에서 조회
- 핸드폰 카메라로 영수증 촬영 → OCR → 자동 가계부 등록
- 알림 동시 수신: 핸드폰 푸시 + 데스크탑 토스트

---

# 8. 웹 대시보드 (Bitwing Dashboard)

## 8.1 React + TypeScript

주요 페이지: 대시보드홈, 매니저관리, 캘린더, 할일/메모, 가계부, 이메일, 파일관리, PC관리, 리포트, 설정

## 8.2 파일/권한 관리

```
📁 퍼블릭 자료
│ 이름        │ 크기  │ 권한        │
│ documents/  │ -     │ R/W 전체    │
│ reports/    │ -     │ R/W 매니저  │
│ receipts/   │ -     │ R/W 재무    │
│ shared/     │ -     │ R 전체      │

[📤 업로드] [📁 새 폴더] [⚙️ 권한 설정]
```

권한: 전체 / 특정매니저 / 사용자만 / 읽기(R) / 읽기+쓰기(R/W)

---

# 9. 외부 서비스 연동

## 9.1 Google 캘린더

Google Calendar API v3 / OAuth 2.0 / 양방향 동기화

## 9.2 이메일

Gmail(API), Outlook(IMAP) / 읽지않은메일, AI요약, 알림

## 9.3 메모앱

Google Keep, Notion API, 파일기반(txt/md)

## 9.4 금융/가계부

| 기능 | 구현 |
|------|------|
| 수입/지출 수동입력 | 앱/웹 UI |
| 은행 API 연동 | 오픈뱅킹 또는 크롤링 |
| 카드 사용내역 | AI100 크롤러 |
| 영수증 OCR | 모바일 카메라 → Tesseract/Google Vision |
| 월별 리포트 | 카테고리 분석, 차트, AI 인사이트 |
| 통장 정리 | 자동 분류 (식비/교통/쇼핑 등) |

카테고리: 수입(급여/보너스/이자/기타), 지출(식비/교통/쇼핑/의료/주거/통신/보험/교육/여가/기타)

## 9.5 AI100 시스템 활용

크롤링(은행/카드/뉴스/환율), 로컬프로그램(엑셀/PDF), 사원PC관리, 자동화(정기보고/백업)

---

# 10. 데이터베이스 설계

## 10.1 MySQL 테이블 (총 13개)

### 기존 테이블 (6개)

```sql
-- 일정 (+ Google 연동 필드)
CREATE TABLE calendars (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    start_at DATETIME NOT NULL,
    end_at DATETIME NOT NULL,
    location VARCHAR(500),
    reminder_minutes INT DEFAULT 30,
    status ENUM('active','cancelled','completed') DEFAULT 'active',
    google_event_id VARCHAR(200),
    source ENUM('bitwing','google','manual') DEFAULT 'bitwing',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 할일 (+ 담당매니저)
CREATE TABLE todos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    priority ENUM('urgent','high','normal','low') DEFAULT 'normal',
    status ENUM('pending','in_progress','completed','cancelled') DEFAULT 'pending',
    due_date DATE,
    assigned_manager VARCHAR(50),
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 메모 (+ 소스)
CREATE TABLE memos (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(500),
    content TEXT NOT NULL,
    tags JSON,
    category VARCHAR(100),
    source ENUM('bitwing','google_keep','notion','manual') DEFAULT 'bitwing',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 대화 히스토리 (+ 매니저, 클라이언트)
CREATE TABLE conversations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    role ENUM('user','assistant','manager') NOT NULL,
    message TEXT NOT NULL,
    intent VARCHAR(100),
    module VARCHAR(50),
    manager VARCHAR(50),
    client ENUM('mobile','desktop','web') DEFAULT 'desktop',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 사원 PC
CREATE TABLE managed_pcs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    hostname VARCHAR(200) NOT NULL,
    ip_address VARCHAR(45),
    os_type ENUM('windows','linux') NOT NULL,
    employee_name VARCHAR(100),
    department VARCHAR(100),
    status ENUM('online','offline','maintenance') DEFAULT 'offline',
    last_seen_at DATETIME,
    system_info JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 시스템 로그 (+ 매니저)
CREATE TABLE system_logs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    level ENUM('info','warning','error','critical') DEFAULT 'info',
    module VARCHAR(50),
    manager VARCHAR(50),
    message TEXT,
    details JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 신규 테이블 (7개)

```sql
-- AI 매니저
CREATE TABLE managers (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    role TEXT,
    status ENUM('active','busy','idle','disabled') DEFAULT 'idle',
    modules JSON,
    config JSON,
    total_tasks INT DEFAULT 0,
    last_active_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 매니저 작업 히스토리
CREATE TABLE manager_tasks (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    manager VARCHAR(50) NOT NULL,
    intent VARCHAR(100),
    request TEXT,
    response TEXT,
    status ENUM('pending','processing','completed','failed') DEFAULT 'pending',
    duration_ms INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME
);

-- 가계부 거래
CREATE TABLE finance_transactions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    type ENUM('income','expense') NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    description VARCHAR(500),
    payment_method VARCHAR(100),
    bank_name VARCHAR(100),
    card_name VARCHAR(100),
    merchant VARCHAR(200),
    receipt_image_path VARCHAR(500),
    source ENUM('manual','bank_api','ocr','crawling') DEFAULT 'manual',
    transaction_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 은행 계좌
CREATE TABLE bank_accounts (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    bank_name VARCHAR(100) NOT NULL,
    account_number_masked VARCHAR(50),
    account_type VARCHAR(50),
    balance DECIMAL(15,2),
    last_synced_at DATETIME,
    config JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 이메일 캐시
CREATE TABLE email_cache (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    email_provider ENUM('gmail','outlook','imap') NOT NULL,
    message_id VARCHAR(200) UNIQUE,
    subject VARCHAR(500),
    sender VARCHAR(200),
    received_at DATETIME,
    is_read BOOLEAN DEFAULT FALSE,
    ai_summary TEXT,
    labels JSON,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 파일 관리
CREATE TABLE managed_files (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(500) NOT NULL,
    filepath VARCHAR(1000) NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    category VARCHAR(100),
    access_level ENUM('public','manager','private') DEFAULT 'public',
    allowed_managers JSON,
    uploaded_by VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 외부 연동 설정
CREATE TABLE integrations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    service VARCHAR(100) NOT NULL,
    status ENUM('connected','disconnected','error') DEFAULT 'disconnected',
    config JSON,
    last_synced_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

# 11. API 설계

## 11.1 인증

API Key 기반. 헤더: `Authorization: Bearer <API_KEY>`

## 11.2 전체 엔드포인트

```
# 메인
POST   /api/v1/chat                          # 명령처리 (→매니저배분)
WS     /api/v1/ws                            # WebSocket
GET    /api/v1/modules                       # 모듈목록

# 매니저
GET    /api/v1/managers                      # 매니저 목록+상태
GET    /api/v1/managers/{name}               # 매니저 상세
GET    /api/v1/managers/{name}/tasks         # 작업 히스토리
PATCH  /api/v1/managers/{name}               # 설정 변경

# 캘린더
GET    /api/v1/calendar/events               # 일정 목록
POST   /api/v1/calendar/events               # 생성
PUT    /api/v1/calendar/events/{id}          # 수정
DELETE /api/v1/calendar/events/{id}          # 삭제
POST   /api/v1/calendar/sync/google          # Google 동기화

# 할일
GET    /api/v1/todos
POST   /api/v1/todos
PATCH  /api/v1/todos/{id}
DELETE /api/v1/todos/{id}

# 메모
GET    /api/v1/memos
POST   /api/v1/memos
GET    /api/v1/memos/search
PUT    /api/v1/memos/{id}
DELETE /api/v1/memos/{id}

# 금융/가계부
GET    /api/v1/finance/transactions          # 거래내역
POST   /api/v1/finance/transactions          # 수동입력
GET    /api/v1/finance/summary               # 월별요약
GET    /api/v1/finance/categories            # 카테고리통계
POST   /api/v1/finance/receipt/ocr           # 영수증OCR
GET    /api/v1/finance/accounts              # 연동계좌
POST   /api/v1/finance/sync                  # 은행동기화

# 이메일
GET    /api/v1/email/messages
GET    /api/v1/email/unread
GET    /api/v1/email/{id}/summary

# 파일관리
GET    /api/v1/files
POST   /api/v1/files/upload
GET    /api/v1/files/{id}/download
DELETE /api/v1/files/{id}
PATCH  /api/v1/files/{id}/permissions
GET    /api/v1/files/search

# PC관리
GET    /api/v1/pcs
GET    /api/v1/pcs/{id}/status
POST   /api/v1/pcs/{id}/command
GET    /api/v1/pcs/report

# 리포트
GET    /api/v1/report/daily
GET    /api/v1/report/weekly
GET    /api/v1/report/monthly
GET    /api/v1/report/managers

# 연동설정
GET    /api/v1/integrations
POST   /api/v1/integrations/{service}/connect
DELETE /api/v1/integrations/{service}/disconnect

# 시스템
GET    /health
```

---

# 12. AI 엔진 (Claude 연동)

## 12.1 흐름

사용자 → Claude 의도분석 → 디스패처 → 매니저 → 모듈실행 → Claude 자연어응답 → 사용자

## 12.2 한국어 날짜 파서

"내일"→내일09:00, "오후3시"→오늘15:00, "다음주월요일"→다음주월요일09:00, "이번달"→이번달1일~말일

---

# 13. 개발 환경 구축

## 13.1 환경 구조

```
Windows (192.168.219.111)          AI100 Server (Ubuntu)
C:\Users\Public\bitwing\             ~/bitwing/
├── bitwing-desktop/ ← 개발          ├── bitwing-core/ ← 개발
├── bitwing-mobile/ ← 개발           ├── bitwing-dashboard/ (빌드배포)
├── bitwing-dashboard/ ← 개발        └── (Git bare repo)
└── docs/
         ↕ Git push/pull ↕
      AI100: ~/git-repos/bitwing.git
```

## 13.2 AI100 서버 세팅

```bash
# Git bare repo
mkdir -p ~/git-repos && git init --bare ~/git-repos/bitwing.git
mkdir -p ~/bitwing && cd ~/bitwing && git init
git remote add origin ~/git-repos/bitwing.git

# Python
cd bitwing-core && python3 -m venv venv
source venv/bin/activate && pip install -r requirements.txt

# MySQL
sudo mysql
# CREATE DATABASE bitwing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
# CREATE USER 'bitwing'@'localhost' IDENTIFIED BY 'password';
# GRANT ALL PRIVILEGES ON bitwing.* TO 'bitwing'@'localhost';

# Redis
sudo apt install redis-server && sudo systemctl enable redis-server

# 퍼블릭 자료
sudo mkdir -p /data/bitwing/{public,private,temp}
sudo chown -R $USER:$USER /data/bitwing

# 환경변수
cp .env.example .env && nano .env

# 서버 실행
uvicorn bitwing-core.main:app --host 0.0.0.0 --port 8000 --reload
```

## 13.3 Windows 데스크탑 세팅

```powershell
# 설치: Git, Python 3.10+, Flutter SDK, Node.js 18+, Claude Code

# SSH 키
ssh-keygen -t ed25519 -C "bitwing-dev"
# → AI100 ~/.ssh/authorized_keys에 공개키 추가

# Clone
cd C:\Users\Public
git clone ssh://user@AI100IP:22/home/user/git-repos/bitwing.git

# Desktop
cd bitwing\bitwing-desktop
python -m venv venv && .\venv\Scripts\activate
pip install -r requirements.txt
pip install pipwin && pipwin install pyaudio

# Mobile
cd ..\bitwing-mobile && flutter pub get

# Dashboard
cd ..\bitwing-dashboard && npm install
```

## 13.4 개발 규칙

| 머신 | 담당 |
|------|------|
| AI100 | bitwing-core/ |
| Windows | bitwing-desktop/, bitwing-mobile/, bitwing-dashboard/ |
| 어디서든 | docs/ |

항상: 작업 전 `git pull`, 작업 후 `git push`

---

# 14. 프로젝트 디렉토리 구조

```
bitwing/
├── docs/
│   └── BITWING_MASTER_PLAN.md
├── bitwing-core/                    # ⚙️ 서버 (AI100)
│   ├── main.py
│   ├── config.py, database.py, auth.py
│   ├── ai_engine/
│   │   ├── claude_client.py
│   │   ├── intent_parser.py
│   │   └── response_builder.py
│   ├── managers/                  # 🆕 AI 매니저
│   │   ├── base.py, dispatcher.py
│   │   ├── schedule_mgr.py
│   │   ├── task_mgr.py
│   │   ├── finance_mgr.py
│   │   ├── it_mgr.py
│   │   └── report_mgr.py
│   ├── modules/
│   │   ├── base.py
│   │   ├── calendar_mod.py, todo_mod.py, memo_mod.py
│   │   ├── finance_mod.py        # 🆕
│   │   ├── email_mod.py, file_mod.py
│   │   ├── pc_manager_mod.py, report_mod.py
│   ├── api/
│   │   ├── chat.py, manager_api.py
│   │   ├── calendar_api.py, todo_api.py, memo_api.py
│   │   ├── finance_api.py        # 🆕
│   │   ├── email_api.py, file_api.py
│   │   ├── pc_api.py, report_api.py
│   │   └── integration_api.py    # 🆕
│   ├── integrations/              # 🆕
│   │   ├── google_calendar.py
│   │   ├── gmail_client.py
│   │   ├── bank_api.py
│   │   └── ocr_engine.py
│   ├── models/ (13개 테이블)
│   ├── utils/
│   └── requirements.txt
├── bitwing-desktop/                 # 🖥️ PySide6 (Windows)
│   ├── main.py, config.py
│   ├── core/ (api_client, ws_client, voice, hotkey, local_commands)
│   ├── ui/ (tray, chat, overlay, notification, settings)
│   ├── plugins/ (clipboard, screenshot, app_launcher, system_monitor)
│   ├── assets/, config/
│   └── requirements.txt
├── bitwing-mobile/                  # 📱 Flutter (Android+iOS)
│   ├── lib/
│   │   ├── api/, models/, screens/, services/, widgets/
│   ├── android/, ios/
│   └── pubspec.yaml
├── bitwing-dashboard/               # 🌐 React
│   ├── src/
│   │   ├── api/, components/, pages/, store/, hooks/
│   ├── package.json, vite.config.ts
└── scripts/
    ├── init_db.py, deploy.sh, install_desktop.sh
```

---

# 15. 개발 로드맵

## Phase 1: 기반 구축 ✅ 완료
- [x] 기획안, 프로젝트명(Bitwing), 구조 설계
- [x] 서버 코어 골격, DB 모델, API, Claude AI 엔진
- [x] 모듈 3개 (캘린더/할일/메모), 날짜파서, 알림
- [x] 개발 환경 가이드

## Phase 2: 매니저 시스템 + 서버 (2~3주)
- [ ] 코드 리네이밍 (ai-secretary → bitwing)
- [ ] AI 매니저 베이스 + 디스패처
- [ ] 5개 매니저 구현
- [ ] Celery + Redis
- [ ] 가계부/금융 모듈
- [ ] DB 마이그레이션, 서버 배포

## Phase 3: 클라이언트 앱 (3~4주)
- [ ] Bitwing Desktop (PySide6)
- [ ] Bitwing Mobile (Flutter Android+iOS)
- [ ] Bitwing Dashboard (React)
- [ ] WebSocket 전 클라이언트

## Phase 4: 외부 연동 (3~4주)
- [ ] Google 캘린더 양방향
- [ ] Gmail/이메일
- [ ] 은행API/크롤링
- [ ] 영수증 OCR
- [ ] 퍼블릭 자료 + 권한

## Phase 5: 고도화 (지속)
- [ ] Whisper(고품질 STT), Wake Word
- [ ] 자동 리포트, 매니저 학습
- [ ] 보안 강화 (SSL)

---

# 16. 보안 정책

| 항목 | 방식 |
|------|------|
| 서버 통신 | HTTPS (Let's Encrypt) |
| 인증 | API Key + IP 화이트리스트 |
| DB | MySQL 원격차단, 암호화 |
| 금융 데이터 | AES 암호화, private 폴더 |
| OAuth 토큰 | Fernet 암호화 |
| 민감 정보 | .env (Git 제외) |
| 데스크탑 | config.ini 로컬 (Git 제외) |
| 모바일 | Secure Storage |
| 파일 권한 | 매니저별+폴더별 접근제어 |
| 로그 | 전체 접근/명령 기록 |

---

> **v2.0** | 2026-03-29
> **변경사항**: AI 매니저 시스템, PySide6, Flutter(Android+iOS), React 대시보드, 금융/가계부, 외부연동, 파일권한
> **프로젝트명 변경**: Metis → **Bitwing** (등록 상표)
> **Bitwing — Your Strategic AI Assistant**
