"""Simple grader for task3 — returns a score strictly between 0 and 1.
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
        return 0.45

    gt = gt_case.get("ground_truth", {})
    atype = action.get("type")

    if atype == "investigate":
        notes = (action.get("notes", "") or "").lower()
        crimes = gt.get("crimes", [])
        evids = gt.get("key_evidence", [])
        crime_hits = sum(1 for c in crimes if c.lower() in notes)
        evid_hits = sum(1 for e in evids if e.lower() in notes)
        score = 0.15 + crime_hits * 0.07 + evid_hits * 0.05
        return max(EPS, min(1 - EPS, min(score, 0.4)))

    if atype == "deliver_verdict":
        pred_verdict = action.get("verdict", "")
        correct_verdict = gt.get("verdict", "")
        v_match = 1.0 if pred_verdict == correct_verdict else 0.0

        true_crimes = set(gt.get("crimes", []))
        pred_crimes = set(action.get("crimes", []))
        c_score = len(true_crimes & pred_crimes) / max(len(true_crimes | pred_crimes), 1)

        true_evid = set(gt.get("key_evidence", []))
        pred_evid = set(action.get("evidence", []))
        e_score = len(true_evid & pred_evid) / max(len(true_evid), 1)

        reasoning = action.get("reasoning", "")
        r_score = min(len(reasoning.split()) / 50, 1.0) * 0.6 + 0.4  # base for reasoning

        score = v_match * 0.4 + c_score * 0.25 + e_score * 0.25 + r_score * 0.1
        return max(EPS, min(1 - EPS, score))

    return EPS


if __name__ == "__main__":
    import sys
    print('{"grader": "task3"}', flush=True)
    try:
        payload = json.load(sys.stdin)
        obs = payload.get("observation", {})
        action = payload.get("action", {})
        s = float(grade(obs, action))
        s = max(EPS, min(1.0 - EPS, s))
        print(json.dumps({"score": round(s, 3)}))
    except Exception as e:
        print(json.dumps({"score": 0.5, "error": str(e)}))
