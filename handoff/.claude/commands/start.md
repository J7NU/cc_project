# /start — 새 시즌 시작 명령어

## 사용법
```
/start
프로젝트명: [이름]
활성 모듈: [designer|marketer|bm] (선택, 쉼표 구분)
```

## Claude Code 실행 절차

### 1. 사전 확인
- [ ] 이전 시즌이 archived 상태인지 확인
- [ ] Ollama + Gemma 실행 중인지 확인 (`curl localhost:11434/api/tags`)
- [ ] registry/active.json 초기화

### 2. 새 시즌 초기화
```json
// registry/active.json
{
  "season": "S{NN}",
  "project": "<프로젝트명>",
  "startDate": "<YYYY-MM-DD>",
  "agents": ["strategist", "executor", "critic"],
  "modules": [<활성화된 모듈 목록>],
  "status": "active"
}
```

### 3. 시즌 디렉터리 생성
```
seasons/S{NN}/
  tickets.json      → []
  logs.json         → []
  checkpoints.json  → [CP1 waiting, CP2 waiting, CP3 waiting]
  budget.json       → { gemma: { iterations: 0 }, claude: { checkpoints: 0 } }
```

### 4. PROJECT_CLAUDE.md 업데이트
- 시즌 ID, 프로젝트명, 시작일 기입
- 이전 시즌 경험 슬롯 내용 유지

### 5. 초기 티켓 생성
사용자가 제공한 프로젝트 인풋을 기반으로 L1 초기 티켓 생성.
최소 구성:
- strategist: T-001 (목표/페르소나 정의)
- executor: T-002 (기술 스택/아키텍처 초안)
- critic: T-003 (초기 리스크 체크)

### 6. 시작 로그
```json
{ "level": "info", "agent": "system", "msg": "시즌 S{NN} 시작 — 프로젝트 '{name}' 활성화" }
```

### 7. L1 루프 시작 신호
LangGraph 오케스트레이터에 L1 루프 시작 이벤트 전송.

## 주의사항
- /start는 Claude Code가 실행하는 유일한 비-체크포인트 개입
- 이후 L1/L2 루프는 Gemma가 자율 처리
- 다음 Claude Code 개입 시점: /checkpoint-l1
