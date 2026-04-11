"""Simple grader for task1 — returns a score strictly between 0 and 1.
This grader supports both import-time use (function `grade(observation, action)`)
and CLI use (reads JSON from stdin with keys `observation` and `action` and
prints a JSON object with `score`).
"""
import sys, json

EPS = 1e-3


def grade(observation: dict, action: dict) -> float:
    # Basic heuristic: if action properly typed and contains tx_ids, give moderate score
    try:
        if action and isinstance(action, dict) and action.get("type") == "flag_transactions":
            txs = action.get("tx_ids", [])
            if len(txs) == 0:
                return 0.2
            return 0.6
    except Exception:
        pass
    return 0.4


if __name__ == "__main__":
    try:
        payload = json.load(sys.stdin)
        obs = payload.get("observation", {})
        action = payload.get("action", {})
        s = float(grade(obs, action))
        s = max(EPS, min(1.0 - EPS, s))
        print(json.dumps({"score": round(s, 3)}))
    except Exception as e:
        print(json.dumps({"score": 0.5, "error": str(e)}))
