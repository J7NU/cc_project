# TODOS.md
> Deferred items from architecture review. Each has context so future sessions can pick them up.

---

## TODO-1: Update HANDOFF.md and CLAUDE.md — CrewAI → AutoGen

**What:** Replace "LangGraph + CrewAI" with "AutoGen + LangGraph" in:
- `handoff/HANDOFF.md` (line 69: 기술 스택 테이블)
- `handoff/CLAUDE.md` (line 8: 시스템 개요)

**Why:** HANDOFF.md is the canonical handoff doc for future Claude Code instances. If it says CrewAI, the next session will implement CrewAI instead of AutoGen. This creates a divergence between the approved design doc (AutoGen) and the implementation.

**Pros:** Single source of truth. Future Claude sessions don't implement the wrong framework.

**Cons:** Minor doc-only change. Low risk.

**Context:** Architecture review on 2026-04-17 locked AutoGen as the agent loop framework (not CrewAI). The design doc at `~/.gstack/projects/J7NU-cc_project/root-claude/install-external-skills-BPPqE-design-20260417-030231.md` already says AutoGen. HANDOFF.md was written before this decision and hasn't been updated.

**Depends on:** Nothing. Can be done immediately.

---

## TODO-2: Phase A quality validation protocol

**What:** Create `handoff/test_tasks.md` with 5 standard test tasks + scoring rubric. Gate Phase B entry on avg output score >7/10 across 5 tasks.

**Why:** Without a quality bar, Phase A "completes" when the loop converges mechanically, but you don't know if Gemma loops actually produce useful outputs. The design doc says "Phase A에서 검증" — this is what that validation looks like concretely.

**Pros:** Turns Phase A from "does it converge?" to "does convergence produce quality?" — the real research question.

**Cons:** Adds a manual evaluation step. Scoring is somewhat subjective.

**Context:** Test tasks should span 3+ domains (e.g., product strategy, technical spec design, market analysis) to validate Gemma generalizes. Human rating: read final Strategist + Executor outputs after convergence. Rate 1-10 against: does this output give me real actionable information? Average >7 across 5 tasks = Phase B green light.

**Depends on:** Phase A implementation (need a working loop to run tasks through).

---

## TODO-3: WebSocket authentication before ngrok deploy

**What:** Add bearer token auth to the FastAPI WebSocket endpoint (`/ws`). Token read from env var (`WS_SECRET_TOKEN`). Dashboard sends token in URL query param or header on connect.

**Why:** When ngrok exposes the WebSocket publicly (Phase C, HANDOFF.md Phase 7), anyone with the URL can stream real-time agent outputs, trigger fork executions, and potentially interfere with runs. A simple token check adds negligible complexity.

**Pros:** Prevents unauthorized access to research outputs. Required for any public-facing deploy.

**Cons:** Adds one env var + one FastAPI middleware. Minimal complexity.

**Context:** HANDOFF.md Phase 7 already plans ngrok setup. The auth must be added in the same phase — not before (no deploy yet) and not after (security hole). FastAPI WebSocket auth pattern: `async def ws_endpoint(websocket: WebSocket, token: str = Query(...)): if token != os.environ['WS_SECRET_TOKEN']: await websocket.close(code=1008); return`.

**Depends on:** Phase C FastAPI server implementation. Phase B can build the endpoint without auth (localhost-only).

---

## TODO-4: Alembic database migration setup (Phase B, before first schema write)

**What:** Initialize Alembic in the project. Create the initial migration for: sessions, iterations, snapshots, metrics, checkpoints tables — with proper indexes on `(session_id, iteration_n)`.

**Why:** Without Alembic, every schema change in Phase B or C requires manually writing `ALTER TABLE` SQL and coordinating with existing data. The Replay Debugger alone will add 2-3 new tables in Phase C.

**Pros:** Schema changes become one `alembic revision --autogenerate` command. Migration history is version-controlled. Easy rollbacks.

**Cons:** Adds ~30 minutes of initial setup. Minor learning curve if unfamiliar with Alembic.

**Context:** Set up immediately when starting Phase B PostgreSQL integration. Directory: `src/migrations/`. Command: `alembic init migrations && alembic revision --autogenerate -m "initial schema"`. Use SQLAlchemy models defined with typed columns — not raw SQL strings.

**Depends on:** Phase B implementation start. Can be done before any other Phase B code.

---

## TODO-5: outlines library contingency for Gemma JSON failures (Phase A validation trigger)

**What:** If Phase A experiment shows Gemma 4B fails to produce valid JSON (after 3 retries) more than ~30% of iterations, add the `outlines` library as a structured generation wrapper.

**Why:** The outside voice correctly flagged that systematic JSON schema violations make the convergence metrics meaningless — if the Critic's output is skipped every other iteration, "0 blindspots 3x" becomes noise, not signal. `outlines` forces valid JSON at the token-sampling level, not via prompt engineering.

**Pros:** Structurally guaranteed valid JSON output. Works with Ollama. Removes the retry fallibility entirely.

**Cons:** Adds a dependency. Constrained generation is slightly slower. Only needed if Gemma actually fails systematically.

**Context:** Trigger condition: in Phase A experiment logs, if WARN-level "skip + retry exhausted" appears more than 6 times in a 20-iteration run, activate this TODO. Install: `pip install outlines`. Wrap the `call_gemma()` function: `outlines.generate.json(model, CriticOutput)`.

**Depends on:** Phase A experiment results. Don't implement unless trigger condition fires.

---

## TODO-6: CP latency measurement and logging (Phase B)

**What:** Add `time.perf_counter()` timing around every CP1 and CP2 call. Log the measured latency to the `checkpoints` table. Emit a WARN log if latency exceeds 30s but continue async (don't block the pipeline).

**Why:** The 30s CP latency SLO is a design target with no enforcement mechanism. Without measurement, you have no idea if you're hitting it or not. This converts a decorative SLO into an observable metric.

**Pros:** Real data for tuning. Latency spikes become visible in the dashboard. Can trigger summary compression tuning if needed.

**Cons:** Adds ~10 lines to the CP handler. Near-zero cost.

**Context:** Add to `src/orchestrator/checkpoints.py`. Schema addition: `latency_ms INTEGER` column in the `checkpoints` table (add in the Alembic initial migration from TODO-4). Dashboard can show CP latency in the timeline view.

**Depends on:** TODO-4 (Alembic + checkpoints table).

---

## TODO-7: Create DESIGN.md — document existing design system (Phase A)

**What:** Create `handoff/dashboard/DESIGN.md` extracting the existing design system from `orchestration-dashboard.jsx`:
- `COLORS` object (full token list with semantic names)
- Spacing scale (values actually used: 4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 40, 48)
- Typography scale (font sizes used: 10, 11, 12, 13, 14, 15, 16, 18, 20, 22, 28, 36)
- Component inventory: Card, MetricCard, StatusBadge, ProgressBar, TabButton, SectionTitle
- Viewport target: desktop-first, min-width 1024px recommended
- Deferred a11y spec (ARIA, keyboard nav, contrast) to TODO-9 / Phase B

**Why:** Without DESIGN.md, future contributors (or future sessions) guess at padding and font sizes. By Phase B when the backend connects and 2+ developers might contribute, design drift will cause visual inconsistencies.

**Pros:** Single source of truth. Future components align with the existing system automatically.

**Cons:** ~30 min to write. Minor maintenance overhead.

**Context:** From `/plan-design-review` on 2026-04-17. No DESIGN.md existed in the project. The inline COLORS object and component system in `orchestration-dashboard.jsx` are clean enough to extract directly. This is purely documentation, no code changes needed.

**Depends on:** Nothing. Can be done before Phase B starts.

---

## TODO-8: Implement ReplayPage — Replay Debugger UI (Phase B/C)

**What:** Implement the full `ReplayPage` component in `orchestration-dashboard.jsx` (currently a stub). Design decisions are locked:
- 3 horizontal swimlane timeline (Strategist/Executor/Critic), each with brand color, clickable iteration ticks
- Iteration tick colors: green=converged, purple=active, amber=pending, gray=past
- Left panel: snapshot detail (agent ID, iteration N, input/output text diff with green=added/red=removed, diff% badge, blindspot count badge)
- Right panel: Recharts `<LineChart>` showing diff% + blindspot count per iteration, converged flag marker
- Fork Execution: modal dialog with original prompt (read-only), modified prompt textarea, session ID (auto-generated), [Cancel] [Fork ⊕ Run] buttons
- Session selector: deferred — Phase B decides (list in sidebar or dropdown in header)

**Why:** This is THE differentiating feature per the locked architecture (Approach C). Without it, this is "just another orchestrator."

**Pros:** Makes the research value of the platform visible and usable. Enables academic publication workflow.

**Cons:** Requires Phase B backend: WebSocket `convergence_metric` messages, PostgreSQL `iterations` table, `/api/sessions/{id}/iterations` endpoint.

**Context:** From `/plan-design-review` on 2026-04-17. Architecture locked in `install-external-skills-BPPqE-design-20260417-030231.md`. `ReplayPage` stub exists at line ~838 in dashboard. Chart library: `recharts` (add to package.json / import in JSX). The Replay Debugger requires the `iterations` table from TODO-4's Alembic migration.

**Depends on:** TODO-4 (Alembic + iterations schema), Phase B WebSocket API, Phase B `/api/sessions` endpoint.

---

## TODO-9: Full accessibility audit (Phase B, before public demo)

**What:** Conduct a full a11y audit of `orchestration-dashboard.jsx`:
- ARIA landmarks: `role="navigation"` on nav, `role="main"` on main, `role="banner"` on header
- Keyboard navigation: Tab order through all interactive elements, Escape closes modals
- Touch targets: 44×44px minimum on all clickable elements (check: some icons are 18-20px)
- Contrast ratios: verify all body text meets 4.5:1 WCAG AA (textMuted `#64748B` on bg `#0A0812`)
- Screen reader flow: test with VoiceOver or NVDA
- Currently fixed: toggle switches converted to `<button role="switch" aria-checked>`, `:focus-visible` outline added

**Why:** This is a developer research tool, not a consumer app. But if it becomes a startup product (the stated goal), a11y issues at launch are embarrassing and legally risky.

**Pros:** WCAG AA compliance. Keyboard-only users can operate the tool. No screen-reader surprises at first public demo.

**Cons:** ~2-4 hours of systematic audit work.

**Context:** From `/plan-design-review` on 2026-04-17. Basic a11y was applied (TODO-9 partial): toggle switches fixed, focus styles added. The deeper audit is deferred to Phase B. `#64748B` on `#0A0812` should be verified — textMuted is used heavily and may fail contrast.

**Depends on:** Phase B implementation (dashboard connected to real data, worth auditing for real).
