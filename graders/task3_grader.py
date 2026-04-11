"""Simple grader for task3 — returns a score strictly between 0 and 1.
"""
import sys, json

EPS = 1e-3


def grade(observation: dict, action: dict) -> float:
    try:
        if action and isinstance(action, dict):
            if action.get("type") == "deliver_verdict":
                return 0.65
            if action.get("type") == "investigate":
                return 0.35
    except Exception:
        pass
    return 0.45


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
