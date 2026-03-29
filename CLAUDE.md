# Bitwing — AI Secretary System

## Project overview
Bitwing(비트윙)은 음성 명령 기반 AI 비서 시스템이다. 5명의 AI 매니저가 업무를 전담 처리하고 사용자에게 보고한다. 단독 사용자(관리자 본인)만 사용한다.

## Architecture
- **bitwing-core**: FastAPI 서버 (AI100 Ubuntu 서버, ~/projects/bitwing/bitwingcore/)
- **bitwing-desktop**: PySide6 Windows 앱 (192.168.219.111)
  - 설치 경로: `\\192.168.219.111\public\bitwingdesk\` (읽기/쓰기 공유 폴더)
  - UNC 경로: `//192.168.219.111/public/bitwingdesk`
  - 로컬 경로: `C:\Users\Public\bitwingdesk\`
- **bitwing-mobile**: Flutter 앱 (Android + iOS)
  - 개발 머신: MacBook (192.168.219.112)
  - Mac ID: jundroid / PW: (직접 설정)
- **bitwing-dashboard**: React 웹 대시보드

모든 클라이언트는 bitwing-core의 REST API + WebSocket으로 통신한다.

## Tech stack
- Python 3.10+, FastAPI, SQLAlchemy, MySQL (스키마: bitwing, utf8mb4)
- Anthropic Claude API (claude-sonnet-4-20250514)
- PySide6 (desktop), Flutter/Dart (mobile), React+TypeScript (dashboard)
- Celery + Redis (매니저 작업 큐)

## AI managers (5)
1. schedule_mgr (📅 일정) — 캘린더, Google Calendar 연동
2. task_mgr (💼 업무) — 할일, 메모, 이메일, 파일
3. finance_mgr (💰 재무) — 가계부, 은행 연동, OCR, 크롤링
4. it_mgr (🖥️ IT) — 사원PC 관리, AI100 연동
5. report_mgr (📊 보고) — 리포트, 통계 분석

## Database
MySQL 스키마 `bitwing`, 20개 테이블. 전체 DDL은 bitwing_schema.sql 참조.
주요 도메인: 매니저(2), 핵심업무(3), 대화(2), 금융(5), PC관리(3), 이메일(2), 파일(2), 시스템(5)

## Coding rules
- 언어: Python (서버/데스크탑), Dart (모바일), TypeScript (대시보드)
- Python 코딩: type hints 필수, docstring 한국어, 변수/함수명 영문 snake_case
- API 응답: 항상 JSON, success/message/data 구조 통일
- 에러: HTTPException 사용, 한국어 에러 메시지
- 로깅: loguru 사용 (print 금지)
- 환경변수: python-dotenv, 민감정보 절대 코드에 하드코딩 금지
- DB: SQLAlchemy ORM, raw SQL 지양
- 비동기: async/await 기본 사용
- 모듈 확장: BaseModule 상속 + @ModuleRegistry.register 데코레이터

## File structure rules
- bitwing-core/는 AI100 서버에서만 수정
- bitwing-desktop/는 Windows PC(192.168.219.111)에서만 수정
  - 공유 폴더: \\192.168.219.111\public\bitwingdesk\ (읽기/쓰기)
- bitwing-mobile/는 MacBook(192.168.219.112)에서 Flutter 개발
- docs/는 어디서든 수정 가능
- .env, config/config.ini는 Git에 포함하지 않음

## Current status
- Phase 1 완료: 기획서, DB 스키마 13테이블 설계 및 200번 서버 배포 완료
- Phase 2 진행중: bitwing-core 서버 코드 구현 (프로젝트 골격 완료)
- GitHub: https://github.com/betona1/bitwingcore

## Key docs
- docs/BITWING_MASTER_PLAN.md — 통합 기획서
- bitwing_schema.sql — DB 전체 DDL
