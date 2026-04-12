"""Simple grader for task1 — returns a score strictly between 0 and 1.
This grader supports both import-time use (function `grade(observation, action)`)
and CLI use (reads JSON from stdin with keys `observation` and `action` and
prints a JSON object with `score`).
"""
import sys, json

EPS = 1e-3


def load_cases():
    import json, os
    try:
        cases_path = os.path.join(os.path.dirname(__file__), "../cases.json")
        with open(cases_path) as f:
            return json.load(f)
    except:
        return []

def grade(observation: dict, action: dict) -> float:
    import json
    EPS = 1e-3
    cases = load_cases()
    case_id = observation.get("case_id", "unknown")
    gt_case = next((c for c in cases if c.get("case_id") == case_id), None)
    if not gt_case:
        return 0.4

    gt = gt_case.get("ground_truth", {})
    correct = set(gt.get("suspicious_tx_ids", []))
    flagged = set(action.get("tx_ids", []))

    if action.get("type") != "flag_transactions":
        return EPS

    tp = len(correct & flagged)
    fp = len(flagged - correct)
    fn = len(correct - flagged)
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2*precision*recall / (precision + recall) if (precision + recall) > 0 else 0.0

    correct_risk = gt.get("risk_level", "high")
    risk_match = 1.0 if action.get("risk_level", "").lower() == correct_risk.lower() else 0.0

    score = f1 * 0.8 + risk_match * 0.2
    return max(EPS, min(1 - EPS, score))


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
