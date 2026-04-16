# /checkpoint-l1 — CP1 감독 명령어

## 트리거 조건
- 모든 L1 티켓 (level: L1) status == done
- 비판가 L1 수렴 신호 수신

## Claude Code 실행 절차

### 1. 출력 파일 수집
```
seasons/S01/tickets.json     → L1 완료 티켓 목록
seasons/S01/checkpoints.json → CP1 현재 상태
.claude/agents/core/         → 각 에이전트 정의
```

### 2. 평가 체크리스트 (4요소)
- [ ] **완결성**: strategist, executor, critic 출력 파일 모두 존재하고 비어 있지 않음
- [ ] **일관성**: 각 에이전트 출력 내부 모순 없음
- [ ] **규칙 준수**: CLAUDE.md G1~G5, PROJECT_CLAUDE.md P1~P4 전체 항목 대조
- [ ] **추적가능성**: 모든 L1 티켓에 에이전트 결정 근거 연결됨

### 3. 결과 처리

#### 통과 (passed)
```json
// seasons/S01/checkpoints.json CP1 업데이트
{
  "id": "CP1",
  "status": "passed",
  "timestamp": "<ISO8601>",
  "feedback": "<요약 피드백>"
}
```
→ WebSocket: `checkpoint_result` 메시지 발송
→ L2 루프 진입 허가

#### 실패 (failed)
```json
{ "id": "CP1", "status": "failed", "feedback": "<실패 이유 + 재작업 지시>" }
```
→ 해당 에이전트 L1 루프 재진입
→ 실패한 수렴 기준 명시하여 에이전트에 피드백 전달

### 4. 로그 기록
```json
{ "level": "success|warn", "agent": "claude", "msg": "CP1 통과|실패 — <요약>" }
```

## 주의사항
- 이 명령어 실행 = Claude Code 토큰 사용 (Max 구독 정액)
- 불필요한 재실행 금지. L1 수렴 신호 확인 후에만 실행.
- CP1 통과 전까지 L2 루프 절대 시작하지 않음
