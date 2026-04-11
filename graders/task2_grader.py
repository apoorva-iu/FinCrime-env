"""Simple grader for task2 — returns a score strictly between 0 and 1.
"""
import sys, json

EPS = 1e-3


def grade(observation: dict, action: dict) -> float:
    try:
        if action and isinstance(action, dict) and action.get("type") == "identify_network":
            shells = action.get("shell_accounts", [])
            if shells:
                return 0.55
            return 0.25
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
