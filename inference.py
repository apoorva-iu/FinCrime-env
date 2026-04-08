"""
FinCrimeEnv — Baseline Inference Script
Runs ONE task per invocation. Emits exactly ONE [START]...[END] block.
Usage:
    python inference.py --task task1
    python inference.py --task task2
    python inference.py --task task3
"""
import os, json, argparse, requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.environ.get("API_BASE_URL", "https://api-inference.huggingface.co/v1")
MODEL_NAME   = os.environ.get("MODEL_NAME",   "Qwen/Qwen2.5-72B-Instruct")
# Do NOT provide a default for HF_TOKEN — validator requires no fallback default.
# Allow alternative OPENAI_API_KEY but do not set an explicit default value.
HF_TOKEN     = os.environ.get("HF_TOKEN") or os.environ.get("OPENAI_API_KEY")
ENV_BASE_URL = os.environ.get("ENV_BASE_URL", "http://localhost:7860")

client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)

def call_env(ep, body):
    r = requests.post(f"{ENV_BASE_URL}/{ep}", json=body, timeout=60)
    r.raise_for_status()
    return r.json()

def ask_llm(system, user):
    try:
        r = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role":"system","content":system},{"role":"user","content":user}],
            max_tokens=1024, temperature=0.1)
        return r.choices[0].message.content.strip()
    except Exception:
        return ""

def parse_json(text):
    text = text.replace("```json","").replace("```","").strip()
    try:
        return json.loads(text)
    except Exception:
        s = text.find("{"); e = text.rfind("}")+1
        if s != -1 and e > s:
            try:
                return json.loads(text[s:e])
            except Exception:
                pass
    return {}

def _chain_get(obj: dict, key: str):
    """Get a field that may be stored as 'from' or 'from_account' (handles alias serialization)."""
    if key in obj:
        return obj[key]
    alias_map = {"from": "from_account", "to": "to_account"}
    return obj.get(alias_map.get(key, key))

def get_action(obs, step, notes):
    # Use the LLM to produce the next action. If parsing fails, fall back to heuristics.
    task = obs.get("task_id", "task1")
    system = (
        "You are a specialist financial crime investigator agent. Given a JSON observation from the FinCrimeEnv, "
        "output EXACTLY one JSON object that matches the action schema for the current task and step. "
        "Do not output any explanation, only the JSON. Use fields and types shown in examples."
    )

    # Build a concise user prompt including the observation and the required action schema.
    user = (
        f"Task: {task}\nStep: {step}\nObservation:\n{json.dumps(obs, default=str)}\n\n"
    )

    if task == "task1":
        user += (
            "Return a FlagTransactionsAction JSON. Example: {\"type\":\"flag_transactions\",\"tx_ids\":[\"TX001\"],\"risk_level\":\"low|medium|high|critical\"}"
        )
    elif task == "task2":
        user += (
            "Return an IdentifyNetworkAction JSON. Example: {\"type\":\"identify_network\",\"shell_accounts\":[\"ACC001\"],\"source\":\"ACC001\",\"beneficiary\":\"ACC005\"}"
        )
    else:
        # For task3, prefer 'investigate' for intermediate steps and 'deliver_verdict' on final step.
        if step < 3:
            user += (
                "Return an InvestigateAction JSON. Example: {\"type\":\"investigate\",\"notes\":\"Your investigation notes...\"}"
            )
        else:
            user += (
                "Return a DeliverVerdictAction JSON. Example: {\"type\":\"deliver_verdict\",\"verdict\":\"freeze_and_escalate|request_info|clear_suspect\",\"crimes\":[\"money_laundering\"],\"evidence\":[\"TX001\"],\"reasoning\":\"...\"}"
            )

    # Query LLM (low temperature for determinism)
    llm_out = ask_llm(system, user)
    action = parse_json(llm_out)

    # Basic validation: must have a 'type' field.
    if not isinstance(action, dict) or "type" not in action:
        # Fallback to original heuristic if LLM fails to produce valid JSON.
        txs = obs.get("transactions", [])
        accs = obs.get("accounts", [])
        if task == "task1":
            susp = [t["tx_id"] for t in txs if
                    t.get("amount", 0) > 5000 or
                    t.get("location", "") in ["Lagos", "Unknown", "Romania", "North Korea", "International"] or
                    "Unknown" in (t.get("merchant", "") or "") or
                    t.get("amount") == 9999.99]
            rl = "high" if len(susp) >= 2 else ("medium" if susp else "low")
            return {"type": "flag_transactions", "tx_ids": susp, "risk_level": rl}

        if task == "task2":
            chain = obs.get("transfer_chain", []) or []
            all_ids = [a["account_id"] for a in accs]
            if not chain:
                return {"type": "identify_network", "shell_accounts": all_ids, "source": "", "beneficiary": ""}
            src = _chain_get(chain[0], "from") or ""
            ben = _chain_get(chain[-1], "to") or ""
            shells = all_ids if src == ben else [a for a in all_ids if a != ben]
            return {"type": "identify_network", "shell_accounts": shells, "source": src, "beneficiary": ben}

        # task3 fallback
        emails = obs.get("emails", [])
        docs = obs.get("supporting_docs", [])
        tx_ids = [t.get("tx_id") for t in txs]
        has_mail = len(emails) > 0
        ver_docs = sum(1 for d in docs if d.get("verified"))
        large = [t for t in txs if t.get("amount", 0) >= 50000]
        small = [t for t in txs if 8000 <= t.get("amount", 0) < 10000]

        if step == 1:
            n = []
            if large:
                n.append(f"Large transfers detected: {[t['tx_id'] for t in large]}")
            if len(small) >= 2:
                n.append(f"Structuring pattern (below $10k threshold): {[t['tx_id'] for t in small]}")
            if has_mail:
                subj = emails[0].get("subject", "")
                n.append(f"Suspicious email found: '{subj}'")
            if ver_docs >= 2:
                n.append(f"{ver_docs} supporting docs verified — checking legitimacy")
            notes.append(" | ".join(n) if n else "Reviewing all evidence for suspicious patterns")
            return {"type": "investigate", "notes": notes[-1]}

        if step == 2:
            crimes = []
            if large:
                crimes.append("money_laundering")
            if len(small) >= 2:
                crimes.append("structuring")
            if has_mail:
                crimes.append("insider_trading")
            n = f"Identified crimes: {crimes}. Key evidence: {tx_ids[:5]}. Emails present: {has_mail}."
            notes.append(n)
            return {"type": "investigate", "notes": n}

        crimes = []
        if large:
            crimes.append("money_laundering")
        if len(small) >= 2:
            crimes.append("structuring")
        if has_mail:
            crimes.append("insider_trading")
        innocent = ver_docs >= 2 and not has_mail and not crimes
        verdict = "clear_suspect" if innocent else "freeze_and_escalate"
        evidence = (["supporting_docs_verified"] if innocent else tx_ids + (["email_tip"] if has_mail else []))
        reasoning = (
            f"All {ver_docs} supporting documents verified. No suspicious transactions or email evidence. "
            f"Account activity matches documented profile. Cleared — no action required."
            if innocent else
            f"Confirmed {len(crimes)} financial crime(s): {', '.join(crimes)}. "
            f"Key evidence includes: {', '.join(evidence[:6])}. "
            f"{'Email evidence confirms coordinated activity. ' if has_mail else ''}"
            f"{'Structuring pattern detected below $10k reporting threshold. ' if 'structuring' in crimes else ''}"
            f"{'Large transfers through shell accounts indicate layering. ' if 'money_laundering' in crimes else ''}"
            f"Immediate freeze and escalation to compliance team recommended."
        )
        return {"type": "deliver_verdict", "verdict": verdict, "crimes": crimes, "evidence": evidence, "reasoning": reasoning}

def run_episode(task_id):
    resp = call_env("reset", {"task_id": task_id})
    sid  = resp["session_id"]
    obs  = resp["observation"]

    total = 0.0; step = 0; done = False; last = 0.0; notes = []
    rewards = []
    # Emit a strict key=value [START] record per validator spec
    env_name = os.environ.get("ENV_NAME", "fincrime-env")
    print(f"[START] task={task_id} env={env_name} model={MODEL_NAME}", flush=True)

    while not done and step < 5:
        step += 1
        action = get_action(obs, step, notes)
        r      = call_env("step", {"session_id": sid, "action": action})
        obs    = r["observation"]
        last   = r["reward"]
        done   = r["done"]
        total += last
        rewards.append(last)
        # Emit a strict key=value [STEP] record per validator spec
        # action must be a single-line string; serialize compactly
        try:
            action_str = json.dumps(action, ensure_ascii=False, separators=(",", ":"))
        except Exception:
            action_str = str(action)
        reward_str = f"{last:.2f}"
        done_str = str(done).lower()
        error_str = r.get("info", {}).get("error") if isinstance(r.get("info", {}), dict) else None
        error_field = error_str if error_str else "null"
        print(f"[STEP] step={step} action={action_str} reward={reward_str} done={done_str} error={error_field}", flush=True)

    score = round(last if task_id == "task3" else total / max(step, 1), 3)
    # Emit a strict key=value [END] record per validator spec
    rewards_str = ",".join(f"{rv:.2f}" for rv in rewards)
    steps_val = step
    # success true if score > 0 (non-zero positive score) and within [0,1]
    success_str = str((score >= 0.0 and score <= 1.0 and score > 0.0)).lower()
    print(f"[END] success={success_str} steps={steps_val} score={score:.2f} rewards={rewards_str}", flush=True)
    return score

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--task", default="task1", choices=["task1", "task2", "task3"])
    run_episode(p.parse_args().task)

if __name__ == "__main__":
    main()
