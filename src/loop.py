"""L1 loop: Strategist → Executor → Critic until convergence."""
import logging
from dataclasses import dataclass, field
from src.agents import (
    StrategistOutput, ExecutorOutput, CriticOutput,
    run_strategist, run_executor, run_critic,
)
from src.convergence import convergence_check, CONVERGE_CONSECUTIVE

logger = logging.getLogger(__name__)
MAX_ITERATIONS = 30


@dataclass
class IterationSnapshot:
    n: int
    strategist: StrategistOutput | None
    executor: ExecutorOutput | None
    critic: CriticOutput | None
    converged: bool
    streak: int


@dataclass
class LoopResult:
    task: str
    snapshots: list[IterationSnapshot] = field(default_factory=list)
    final_strategy: StrategistOutput | None = None
    final_execution: ExecutorOutput | None = None
    converged: bool = False
    total_iterations: int = 0


def run_l1_loop(task: str) -> LoopResult:
    result = LoopResult(task=task)
    critic_history: list[CriticOutput | None] = []
    prev_strategy: StrategistOutput | None = None
    prev_execution: ExecutorOutput | None = None

    for n in range(1, MAX_ITERATIONS + 1):
        logger.info("Iteration %d/%d", n, MAX_ITERATIONS)

        strategy = run_strategist(task, prev_strategy)
        if strategy is None:
            logger.warning("Strategist failed at iteration %d, skipping", n)
            critic_history.append(None)
            result.snapshots.append(IterationSnapshot(n, None, None, None, False, 0))
            continue

        execution = run_executor(task, strategy, prev_execution)
        if execution is None:
            logger.warning("Executor failed at iteration %d, skipping", n)
            critic_history.append(None)
            result.snapshots.append(IterationSnapshot(n, strategy, None, None, False, 0))
            continue

        critic = run_critic(task, strategy, execution)
        critic_history.append(critic)

        converged, streak = convergence_check(critic_history)
        logger.info(
            "Critic: blindspots=%s risks=%s converged=%s streak=%d/%d",
            len(critic.blindspots) if critic else "?",
            len(critic.risks) if critic else "?",
            converged,
            streak,
            CONVERGE_CONSECUTIVE,
        )

        result.snapshots.append(IterationSnapshot(n, strategy, execution, critic, converged, streak))
        prev_strategy = strategy
        prev_execution = execution

        if converged:
            result.final_strategy = strategy
            result.final_execution = execution
            result.converged = True
            result.total_iterations = n
            logger.info("Converged at iteration %d", n)
            return result

    result.total_iterations = MAX_ITERATIONS
    result.final_strategy = prev_strategy
    result.final_execution = prev_execution
    logger.warning("Did not converge after %d iterations", MAX_ITERATIONS)
    return result
