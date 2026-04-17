# HANDOFF — Claude Code 인수인계 문서
> 이 프로젝트를 처음 받는 Claude Code 인스턴스를 위한 전체 컨텍스트.

---

## 한 문장 요약
Gemma(로컬 Ollama)가 L1/L2 반복 루프를 처리하고, Claude Code가 3개 체크포인트에서만 감독하는 **비용 0원 멀티에이전트 오케스트레이션 시스템**을 단계적으로 구현한다.

---

## 현재 상태 (구현 전)

아키텍처 설계는 **완전히 확정**되었고, 대시보드 UI도 완성되어 있다. **구현은 아직 시작하지 않았다.**

| 항목 | 상태 |
|------|------|
| 아키텍처 설계 | ✅ 확정 (v3) |
| 데이터 스키마 | ✅ 확정 |
| 구현 로드맵 | ✅ 확정 (7단계) |
| 대시보드 JSX | ✅ 완성 (목 데이터) |
| 규칙 파일 | ✅ 이 핸드오프에 포함 |
| 백엔드 코드 | ❌ 미구현 |
| LangGraph 오케스트레이터 | ❌ 미구현 |
| FastAPI 서버 | ❌ 미구현 |

---

## 핵심 파일 위치

```
CLAUDE.md                          ← 전역 규칙 (자동 읽힘)
PROJECT_CLAUDE.md                  ← 프로젝트 규칙
HANDOFF.md                         ← 이 파일

.claude/
  agents/core/
    strategist.md                  ← 전략가 에이전트 정의
    executor.md                    ← 실행가 에이전트 정의
    critic.md                      ← 비판가 에이전트 정의
  agents/modules/
    designer.md / marketer.md / bm.md
  commands/
    start.md                       ← /start 명령어
    checkpoint-l1.md               ← /checkpoint-l1 명령어
    checkpoint-l2.md               ← /checkpoint-l2 명령어

registry/
  active.json                      ← 현재 시즌 + 활성 에이전트
  state_bridge.json                ← FastAPI ↔ LangGraph 공유 상태

seasons/S01/                       ← 시즌 데이터 (시작 후 생성)
  tickets.json
  logs.json
  checkpoints.json
  budget.json

src/                               ← 구현할 Python 소스
dashboard/
  orchestration-dashboard.jsx      ← 완성된 React 대시보드
```

---

## 기술 스택

| 구성 요소 | 기술 | 비고 |
|-----------|------|------|
| 워커 LLM | Gemma (gemma-4-e4b-it) | Ollama via localhost:11434 |
| 오케스트레이션 | AutoGen + LangGraph | AutoGen으로 에이전트 루프, LangGraph가 OrchestrationState 소유 |
| 백엔드 | FastAPI + Uvicorn | REST + WebSocket |
| 프론트엔드 | React (JSX 완성됨) | WS_URL만 교체하면 연결 |
| 런타임 | MacBook Pro M5 | Ollama 네이티브 Apple Silicon |
| 외부 접근 | ngrok | 7단계에서 구성 |

---

## 구현 로드맵 요약

| 단계 | 제목 | 핵심 결과물 | 우선순위 |
|------|------|-------------|---------|
| **1** | 로컬 기반 구축 | Ollama + Gemma 동작 확인, 의존성 설치 | 🔴 즉시 |
| **2** | 규칙 및 파일 구조 | 이 핸드오프 파일들 검증 및 보완 | 🔴 즉시 |
| **3** | 단일 에이전트 L1 루프 | 1개 에이전트가 Gemma로 반복 + 수렴 | 🔴 핵심 |
| **4** | 멀티에이전트 + CP1/CP2 | 코어 3개 에이전트 + 체크포인트 통합 | 🔴 크리티컬 패스 |
| **5** | FastAPI 백엔드 | REST + WebSocket 서버 | 🟡 4단계 후 |
| **6** | 대시보드 연결 + CP3 | 목 데이터 → 실제 데이터 교체 | 🟡 5단계 후 |
| **7** | 실행·회고·ngrok | 전체 파이프라인 완성 | 🟢 마지막 |

**크리티컬 패스**: 1 → 2 → 3 → 4 (여기서 대부분의 시간 소요)

---

## 파이프라인 흐름

```
사용자 인풋
    ↓
/start (Claude Code — 시즌 초기화)
    ↓
[L1 루프] ← Gemma 전담
  strategist: L1 반복 → 수렴
  executor:   L1 반복 → 수렴
  critic:     매 반복마다 맹점 검토
    ↓
/checkpoint-l1 (Claude Code — 4요소 평가)
  통과 → L2 진입
  실패 → L1 재진입
    ↓
[L2 루프] ← Gemma 전담
  에이전트 간 크로스 피드백
  충돌 감지 → 조율 → 수렴
    ↓
/checkpoint-l2 (Claude Code — 통합 제안서 작성)
  통과 → CP3 대기
  실패 → L2 재진입
    ↓
[CP3] 사용자 승인 (대시보드)
  승인 → 실행
  거절A → L2 재진입
  거절B → 인풋 재진입
    ↓
실행 (Claude Code — Bash/Write/Edit)
    ↓
회고 (Claude Code — 경험 슬롯 업데이트)
    ↓
아카이브 → 다음 시즌
```

---

## 비용 구조

- **L1/L2 반복**: Gemma (Ollama 로컬) = **0원**
- **CP1/CP2/CP3 감독**: Claude Code Max 구독 = **정액 (추가 비용 없음)**
- **실행/회고**: Claude Code Max 구독 = **정액**
- **인프라**: MacBook 로컬 = **0원**

→ 총 API 과금: **0원**

---

## WebSocket 메시지 타입 (대시보드 연동)

| 타입 | 트리거 | payload 핵심 필드 |
|------|--------|-------------------|
| `agent_status` | 에이전트 상태 변경 | agentId, status, tasks, completed |
| `ticket_update` | 티켓 생성/상태 변경 | ticket (Ticket 객체 전체) |
| `log_entry` | 모든 로그 이벤트 | ts, level, agent, msg |
| `checkpoint_result` | CP1/CP2 평가 완료 | checkpointId, status, feedback |
| `convergence_metric` | 매 반복 완료 | agentId, level, iteration, delta, blindspots, converged |

---

## 대시보드 연결 방법 (6단계)

`dashboard/orchestration-dashboard.jsx` 상단의 `WS_URL` 상수만 변경:

```javascript
// 현재 (목 데이터)
const WS_URL = 'ws://localhost:8000/ws';  // 이미 설정됨

// ngrok 사용 시
const WS_URL = 'wss://{ngrok-id}.ngrok.io/ws';
```

백엔드가 `schema_visualization_ko.pdf`의 형태 그대로 데이터를 반환하면
대시보드 코드 수정 없이 연결 완료.

---

## 지금 당장 시작하려면

```bash
# 1. Ollama + Gemma 확인
curl localhost:11434/api/tags

# 2. Python 환경
python -m venv .venv && source .venv/bin/activate
pip install pyautogen langgraph langchain-ollama fastapi uvicorn pydantic

# 3. Hello World — Gemma 통신 확인
python -c "
from langchain_ollama import OllamaLLM
llm = OllamaLLM(model='gemma-4-e4b-it')
print(llm.invoke('안녕하세요, 한 문장으로 자기소개 해줘'))
"

# 4. 준비 완료 → /start 명령어로 S01 시작
```

---

## 참고 문서

| 문서 | 내용 |
|------|------|
| `system_architecture_v3.pdf` | 전체 아키텍처 설계 (완성) |
| `implementation_roadmap_ko.pdf` | 7단계 구현 로드맵 (완성) |
| `schema_visualization_ko.pdf` | 데이터 스키마 + REST API + WebSocket 명세 (완성) |
| `dashboard/orchestration-dashboard.jsx` | 완성된 대시보드 (목 데이터) |

---

*이 문서는 구현 진행에 따라 업데이트하세요. 특히 "현재 상태" 섹션의 체크박스.*
