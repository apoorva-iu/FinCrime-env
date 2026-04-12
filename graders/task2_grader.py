"""Simple grader for task2 — returns a score strictly between 0 and 1.
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
    if action.get("type") != "identify_network":
        return EPS

    correct_shells = set(gt.get("shell_accounts", []))
    pred_shells = set(action.get("shell_accounts", []))

    if not correct_shells:
        shell_f1 = 1.0 if not pred_shells else 0.0
    else:
        tp_s = len(correct_shells & pred_shells)
        fp_s = len(pred_shells - correct_shells)
        fn_s = len(correct_shells - pred_shells)
        prec_s = tp_s / (tp_s + fp_s) if (tp_s + fp_s) > 0 else 0.0
        rec_s = tp_s / (tp_s + fn_s) if (tp_s + fn_s) > 0 else 0.0
        shell_f1 = 2*prec_s*rec_s / (prec_s + rec_s) if (prec_s + rec_s) > 0 else 0.0

    src_correct = action.get("source", "") == gt.get("source_account", "")
    bene_correct = action.get("beneficiary", "") == gt.get("beneficiary_account", "")

    score = shell_f1 * 0.4 + (0.3 if src_correct else 0.0) + (0.3 if bene_correct else 0.0)
    return max(EPS, min(1 - EPS, score))


if __name__ == "__main__":
    import sys
    print('{"grader": "task2"}', flush=True)
    try:
        payload = json.load(sys.stdin)
        obs = payload.get("observation", {})
        action = payload.get("action", {})
        s = float(grade(obs, action))
        s = max(EPS, min(1.0 - EPS, s))
        print(json.dumps({"score": round(s, 3)}))
    except Exception as e:
        print(json.dumps({"score": 0.5, "error": str(e)}))
