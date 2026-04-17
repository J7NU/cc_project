# CLAUDE.md — 전역 규칙 (Global Rules)
> 이 파일은 Claude Code가 자동으로 읽습니다. 모든 서브에이전트에 상속됩니다.

---

## 시스템 개요

멀티에이전트 오케스트레이션 시스템 **v3** — 시즌 기반 순차 실행 모델.

- **워커**: Gemma (gemma-4-e4b-it) via Ollama — L1/L2 반복 루프 전담
- **감독자**: Claude Code (Max 구독) — 체크포인트 3회 개입 한정
- **오케스트레이션**: AutoGen (에이전트 루프) + LangGraph (OrchestrationState 소유, CP 전환)
- **런타임**: MacBook Pro M5 로컬 + ngrok 외부 접근
- **API 비용**: 0원 (로컬 Gemma + Max 구독 정액)

---

## 불변 규칙 (mutable: false) — 절대 재정의 불가

### G1 — 사용자 승인 없이 실행 금지
CP3 사용자 승인 이전에 어떠한 코드 실행·파일 쓰기·시스템 변경도 금지.
승인 게이트: 대시보드 CP3 패널 또는 명시적 텍스트 승인.

### G2 — 수렴 기준 4요소 (모든 체크포인트 공통)
| 기준 | 설명 |
|------|------|
| 완결성 (Completeness) | 필수 출력물이 모두 존재하고 비어 있지 않음 |
| 일관성 (Consistency) | 에이전트 출력 내 내부 모순 없음 |
| 규칙 준수 (Rule Compliance) | CLAUDE.md + PROJECT_CLAUDE.md 전체 준수 |
| 추적가능성 (Traceability) | 모든 결정이 티켓 ID와 연결됨 |

### G3 — 규칙 상속
- CLAUDE.md의 모든 규칙은 PROJECT_CLAUDE.md에 자동 상속
- 서브에이전트는 이 파일을 컨텍스트로 자동 수신
- mutable: false 규칙은 프로젝트 규칙으로 재정의 불가

### G4 — Claude Code 개입 제한
Claude Code는 **CP1, CP2, CP3 세 체크포인트에서만** 개입한다.
L1/L2 반복 루프는 전적으로 Gemma가 처리한다. 비용 최적화 원칙.

---

## 가변 규칙 (mutable: true) — 경험으로 업데이트 가능

### G5 — 비판가 수렴 인정 조건
비판가가 N회 연속 맹점(blindspot) 0건을 보고하면 해당 레벨 수렴 인정.
N의 초기값: 3회. 경험에 따라 PROJECT_CLAUDE.md에서 재정의 가능.

---

## 에이전트 구조

### 코어 에이전트 (항상 ON)
| ID | 이름 | 역할 |
|----|------|------|
| strategist | 전략가 | 방향·기획·목표 설정 |
| executor | 실행가 | 구체적 구현·자동 전환 |
| critic | 비판가 | 맹점·리스크·반론 (항상 ON) |

### 선택 모듈 (프로젝트별 활성화)
| ID | 이름 | 역할 |
|----|------|------|
| designer | 디자이너 | 웹·앱 UI/UX |
| marketer | 마케터 | 공개·홍보 전략 |
| bm | BM설계 | 수익 모델 설계 |

에이전트 정의: `.claude/agents/core/{id}.md`, `.claude/agents/modules/{id}.md`

---

## 파이프라인 단계

```
① 인풋 → ②③ L1 루프 → ④ CP1 → ⑤⑥ L2 루프 → ⑦ CP2 → ⑧ CP3(사용자) → ⑨ 실행 → ⑩ 회고
```

- **L1**: 에이전트 내부 자기 정제 루프 (Gemma)
- **L2**: 에이전트 간 크로스 피드백 루프 (Gemma)
- **CP1**: L1 수렴 후 Claude Code 감독 (`/checkpoint-l1`)
- **CP2**: L2 수렴 후 Claude Code 감독 (`/checkpoint-l2`)
- **CP3**: 사용자 최종 승인 (대시보드 또는 텍스트)

---

## 경험 슬롯 (회고에서 자동 추가)

<!-- 이 섹션은 회고 단계에서 Claude Code가 자동으로 업데이트합니다 -->
<!-- [GLOBAL_SLOT_1] -->
<!-- [GLOBAL_SLOT_2] -->
