"""
FinCrimeEnv — FastAPI Server
OpenEnv compatible: /reset /step /state
"""
import uuid
from typing import Any, Dict, Optional
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from env import FinCrimeEnv, TASK_POOLS
from models import Observation

sessions: Dict[str, FinCrimeEnv] = {}

app = FastAPI(
    title="FinCrimeEnv",
    description="AI Financial Crime Investigation Environment — OpenEnv Compatible",
    version="1.2.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

STATIC_DIR = Path(__file__).parent / "static"
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


def obs_dump(obs: Observation) -> dict:
    """Serialize with by_alias=True so TransferHop.from_account → 'from' in JSON."""
    return obs.model_dump(by_alias=True)


class ResetRequest(BaseModel):
    task_id: str = "task1"
    session_id: Optional[str] = None

class StepRequest(BaseModel):
    session_id: str
    action: Dict[str, Any]

class SessionRequest(BaseModel):
    session_id: str

def get_session(sid: str) -> FinCrimeEnv:
    if sid not in sessions:
        raise HTTPException(status_code=404, detail=f"Session '{sid}' not found. Call /reset first.")
    return sessions[sid]


@app.get("/ui")
def ui():
    return FileResponse(str(STATIC_DIR / "index.html"))

@app.get("/")
def root():
    return {
        "name": "FinCrimeEnv",
        "version": "1.2.0",
        "tasks": ["task1", "task2", "task3"],
        "case_counts": {tid: len(pool) for tid, pool in TASK_POOLS.items()},
        "endpoints": ["/reset", "/step", "/state", "/tasks", "/health", "/ui", "/docs"]
    }

@app.get("/health")
def health():
    return {"status": "ok", "sessions_active": len(sessions)}

@app.get("/tasks")
def list_tasks():
    return {"tasks": [
        {
            "task_id":       "task1",
            "name":          "Spot the Fraud",
            "difficulty":    "easy",
            "description":   "Flag suspicious transactions using F1-score grader",
            "case_count":    len(TASK_POOLS["task1"]),
            "max_steps":     5,
            "scoring":       "f1 * 0.9 + risk_level_correct * 0.1",
            "action_format": '{"type":"flag_transactions","tx_ids":["TX001",...],"risk_level":"low/medium/high/critical"}'
        },
        {
            "task_id":       "task2",
            "name":          "Trace the Network",
            "difficulty":    "medium",
            "description":   "Identify shell accounts, source, and beneficiary",
            "case_count":    len(TASK_POOLS["task2"]),
            "max_steps":     5,
            "scoring":       "shell_f1 * 0.4 + source_correct * 0.3 + beneficiary_correct * 0.3",
            "action_format": '{"type":"identify_network","shell_accounts":["ACC001",...],"source":"ACC001","beneficiary":"ACC005"}'
        },
        {
            "task_id":       "task3",
            "name":          "Deliver the Verdict",
            "difficulty":    "hard",
            "description":   "Multi-step investigation then deliver a legal verdict",
            "case_count":    len(TASK_POOLS["task3"]),
            "max_steps":     5,
            "scoring":       "verdict_correct * 0.4 + crime_score * 0.25 + evidence_score * 0.25 + reasoning_score * 0.1",
            "action_format": {
                "investigate":     '{"type":"investigate","notes":"..."}',
                "deliver_verdict": '{"type":"deliver_verdict","verdict":"freeze_and_escalate/clear_suspect/request_info","crimes":[...],"evidence":[...],"reasoning":"..."}'
            }
        }
    ]}

@app.post("/reset")
def reset(request: ResetRequest):
    sid = request.session_id or str(uuid.uuid4())
    env = FinCrimeEnv(task_id=request.task_id)
    obs = env.reset()
    sessions[sid] = env
    return {
        "session_id":     sid,
        "observation":    obs_dump(obs),
        "task_id":        request.task_id,
        "case_pool_size": len(TASK_POOLS[request.task_id])
    }

@app.post("/step")
def step(request: StepRequest):
    env    = get_session(request.session_id)
    result = env.step(request.action)
    return {
        "session_id":  request.session_id,
        "observation": obs_dump(result.observation),
        "reward":      result.reward,
        "done":        result.done,
        "info":        result.info
    }

@app.post("/state")
def state(request: SessionRequest):
    env    = get_session(request.session_id)
    result = env.state()
    obs    = result["observation"]
    return {
        "session_id":  request.session_id,
        "observation": obs_dump(obs) if isinstance(obs, Observation) else obs,
        "reward":      result["reward"],
        "done":        result["done"],
        "info":        result["info"]
    }


def main():
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7860, reload=False)

if __name__ == "__main__":
    main()
