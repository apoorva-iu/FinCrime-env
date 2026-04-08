import random
import json
from fastapi.testclient import TestClient
from env import FinCrimeEnv
from main import app


def test_env_reset_and_step_task1():
    random.seed(0)
    env = FinCrimeEnv(task_id="task1")
    obs = env.reset()
    assert obs.case_id is not None
    # Build action from ground truth to ensure high reward
    gt = env.current_case.get("ground_truth", {})
    txs = gt.get("suspicious_tx_ids", [])
    action = {"type": "flag_transactions", "tx_ids": txs, "risk_level": gt.get("risk_level", "high")}
    resp = env.step(action)
    assert 0.0 <= resp.reward <= 1.0
    assert resp.done is True


def test_api_reset_and_step():
    client = TestClient(app)
    r = client.post("/reset", json={"task_id": "task1"})
    assert r.status_code == 200
    data = r.json()
    assert "session_id" in data
    sid = data["session_id"]
    obs = data["observation"]
    # Send a no-op action (expect low reward but API returns payload)
    step = client.post("/step", json={"session_id": sid, "action": {"type": "flag_transactions", "tx_ids": []}})
    assert step.status_code == 200
    sdata = step.json()
    assert "reward" in sdata and "done" in sdata
