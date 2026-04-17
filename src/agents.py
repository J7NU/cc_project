"""Gemma agent calls via Ollama. Each agent has a typed Pydantic output schema."""
import json
import re
import time
import logging
from typing import Optional
import httpx
from pydantic import BaseModel, ValidationError

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma-4-e4b-it"
MAX_RETRIES = 3
logger = logging.getLogger(__name__)


class StrategistOutput(BaseModel):
    direction: str
    goals: list[str]
    assumptions: list[str]


class ExecutorOutput(BaseModel):
    plan: list[str]
    blockers: list[str]
    deliverables: list[str]


class CriticOutput(BaseModel):
    blindspots: list[str]
    risks: list[str]
    converged: bool


def _call_ollama(prompt: str) -> str:
    payload = {"model": MODEL, "prompt": prompt, "stream": False}
    resp = httpx.post(OLLAMA_URL, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()["response"]


def _extract_json(text: str) -> dict:
    """Extract first JSON object from model output."""
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        raise ValueError("No JSON object found in response")
    return json.loads(match.group())


def call_gemma(prompt: str, schema: type[BaseModel]) -> Optional[BaseModel]:
    """Call Gemma and parse output into schema. Returns None after MAX_RETRIES failures."""
    json_schema = schema.model_json_schema()
    full_prompt = (
        f"{prompt}\n\n"
        f"Respond with ONLY a valid JSON object matching this schema (no markdown, no extra text):\n"
        f"{json.dumps(json_schema, ensure_ascii=False)}"
    )
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            raw = _call_ollama(full_prompt)
            data = _extract_json(raw)
            return schema.model_validate(data)
        except (httpx.HTTPError, ValueError, ValidationError) as e:
            logger.warning("Attempt %d/%d failed: %s", attempt, MAX_RETRIES, e)
            if attempt < MAX_RETRIES:
                time.sleep(1)
    logger.warning("skip + retry exhausted for %s", schema.__name__)
    return None


def run_strategist(task: str, prev_output: Optional[StrategistOutput] = None) -> Optional[StrategistOutput]:
    context = f"\nPrevious output to refine:\n{prev_output.model_dump_json()}" if prev_output else ""
    prompt = (
        f"You are a strategic planner. Given the following task, produce a strategic direction.\n"
        f"Task: {task}{context}"
    )
    return call_gemma(prompt, StrategistOutput)


def run_executor(task: str, strategy: StrategistOutput, prev_output: Optional[ExecutorOutput] = None) -> Optional[ExecutorOutput]:
    context = f"\nPrevious output to refine:\n{prev_output.model_dump_json()}" if prev_output else ""
    prompt = (
        f"You are an execution planner. Given this task and strategy, produce a concrete execution plan.\n"
        f"Task: {task}\n"
        f"Strategy: {strategy.model_dump_json()}{context}"
    )
    return call_gemma(prompt, ExecutorOutput)


def run_critic(task: str, strategy: StrategistOutput, execution: ExecutorOutput) -> Optional[CriticOutput]:
    prompt = (
        f"You are a critical reviewer. Identify blindspots and risks in this plan.\n"
        f"Task: {task}\n"
        f"Strategy: {strategy.model_dump_json()}\n"
        f"Execution: {execution.model_dump_json()}\n"
        f"Set converged=true ONLY if you find zero blindspots and zero risks."
    )
    return call_gemma(prompt, CriticOutput)
