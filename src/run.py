"""Entry point. Usage: python -m src.run "your task here"
Runs the L1 loop and writes results to runs/<timestamp>.json (SQLite in Phase B).
"""
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from src.loop import run_l1_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

RUNS_DIR = Path("runs")


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.run \"<task>\"")
        sys.exit(1)

    task = " ".join(sys.argv[1:])
    logger.info("Starting L1 loop for task: %s", task)

    result = run_l1_loop(task)

    RUNS_DIR.mkdir(exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = RUNS_DIR / f"{ts}.json"

    payload = {
        "task": result.task,
        "converged": result.converged,
        "total_iterations": result.total_iterations,
        "final_strategy": result.final_strategy.model_dump() if result.final_strategy else None,
        "final_execution": result.final_execution.model_dump() if result.final_execution else None,
        "snapshots": [
            {
                "n": s.n,
                "converged": s.converged,
                "streak": s.streak,
                "blindspots": s.critic.blindspots if s.critic else None,
                "risks": s.critic.risks if s.critic else None,
            }
            for s in result.snapshots
        ],
    }

    out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    logger.info("Result written to %s", out_path)

    print("\n" + "=" * 60)
    print(f"Task:       {result.task}")
    print(f"Converged:  {result.converged}")
    print(f"Iterations: {result.total_iterations}")
    if result.final_strategy:
        print(f"\nFinal direction: {result.final_strategy.direction}")
    if result.final_execution:
        print(f"Execution plan ({len(result.final_execution.plan)} steps):")
        for i, step in enumerate(result.final_execution.plan, 1):
            print(f"  {i}. {step}")
    print("=" * 60)


if __name__ == "__main__":
    main()
