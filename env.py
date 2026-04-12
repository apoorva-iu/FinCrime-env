"""
FinCrimeEnv — Core Environment
21 cases across three difficulty levels.
Task routing: task1=easy(CASE001-005), task2=medium(CASE006-015), task3=hard(CASE016-021)
"""
import json, random
from pathlib import Path
from typing import Any, Tuple, Dict, List
from models import Observation, StepResponse, Transaction, Account, TransferHop, Email, SupportingDoc
from graders.task1_grader import grade as grade_task1
from graders.task2_grader import grade as grade_task2
from graders.task3_grader import grade as grade_task3

CASES_PATH = Path(__file__).parent / "cases.json"

def load_cases():
    with open(CASES_PATH) as f:
        return json.load(f)

ALL_CASES = load_cases()

TASK_POOLS = {
    "task1": [c for c in ALL_CASES if c.get("difficulty") == "easy"],
    "task2": [c for c in ALL_CASES if c.get("difficulty") == "medium"],
    "task3": [c for c in ALL_CASES if c.get("difficulty") == "hard"],
}

CASE_RECOMMENDATIONS = {
    "CASE016": (
        "🚨 RECOMMENDATION: FREEZE AND ESCALATE\n"
        "CRIMES IDENTIFIED: insider_trading, money_laundering, structuring\n"
        "ACTION: Freeze all three linked accounts immediately — Robert Chen personal (ACC8001), "
        "RC Holdings Ltd (ACC8002), and John Doe (ACC8003). Place Robert Chen on administrative leave "
        "and revoke all trading system access without delay. Preserve the email chain between "
        "robert.chen@bank.com and rc_personal@gmail.com — forward directly to SEC Market Abuse Division. "
        "File a SAR for structuring: three identical $9,000 cash withdrawals on the same day constitute "
        "deliberate avoidance of the $10,000 CTR threshold under 31 U.S.C. § 5324. "
        "Refer to the DOJ for concurrent insider trading and money laundering prosecution."
    ),
    "CASE017": (
        "🚨 RECOMMENDATION: FREEZE AND ESCALATE\n"
        "CRIMES IDENTIFIED: embezzlement, money_laundering, fraud\n"
        "ACTION: Freeze Diana Ross's personal account (ACC9001) and DR Holdings LLC (ACC9003) immediately. "
        "Notify TechCorp Inc (ACC9002) board of directors and Audit Committee — the CFO has self-approved "
        "fraudulent vendor invoices totalling $600,000 payable to a personally controlled shell company. "
        "Engage an independent forensic auditor to review all vendor payments approved by Diana Ross "
        "in the past 24 months. Preserve both email records, including the asset-protection communication "
        "with external legal counsel, as evidence of intent to conceal. "
        "Refer to FBI Economic Crimes Division and file SAR. Seek emergency asset preservation order "
        "to prevent the threatened offshore transfer before the internal audit."
    ),
    "CASE018": (
        "✅ RECOMMENDATION: CLOSE — NO ACTION REQUIRED\n"
        "VERDICT: clear_suspect\n"
        "All three supporting documents — death certificate, will, and real estate contract — are "
        "independently verified. The $25,000 inheritance wire, $20,000 home deposit, and $15,000 "
        "international family support transfer are fully consistent with documented inheritance proceeds. "
        "The $5,000 jewelry purchase is within normal discretionary spending for the account balance. "
        "Update Maria Garcia's KYC record to note verified inheritance as the source of funds. "
        "Send standard account clearance notification. No monitoring escalation required."
    ),
    "CASE019": (
        "🚨 RECOMMENDATION: FREEZE AND ESCALATE\n"
        "CRIMES IDENTIFIED: tax_evasion, money_laundering\n"
        "ACTION: Freeze Cayman Trust Alpha (ACC11002) and BVI Holdings (ACC11003) immediately. "
        "The unverified trust deed and tax filings, combined with an email explicitly stating that the "
        "beneficial owner has been 'fully obscured from regulators', constitute strong evidence of "
        "deliberate tax fraud and money laundering. File SAR immediately citing beneficial ownership "
        "concealment. Escalate to IRS Criminal Investigation Division for tax evasion review. "
        "Invoke FATF mutual legal assistance treaty provisions for both the Cayman Islands and BVI "
        "to obtain mandatory beneficial ownership disclosure. Do not release any funds until the true "
        "beneficiary is identified and full tax compliance across all jurisdictions is confirmed."
    ),
    "CASE020": (
        "🚨 RECOMMENDATION: FREEZE AND ESCALATE — TERRORISM FINANCING PRIORITY\n"
        "CRIMES IDENTIFIED: possible_terrorism_financing, money_laundering, tax_evasion\n"
        "ACTION: Freeze Anonymous User account (ACC15001) and Unnamed LLC (ACC15002) immediately. "
        "The email requesting cash delivery in Damascus by end of week is a definitive terrorism "
        "financing indicator under 31 U.S.C. § 5318. Crypto mixer usage with wholly unverified KYC "
        "documents confirms deliberate identity concealment. File FinCEN SAR with the highest-urgency "
        "terrorism financing flag — do not use standard processing timelines. Report immediately to "
        "FBI Counterterrorism Division and submit to OFAC for sanctions screening of the Damascus "
        "destination. Alert FinCEN's Financial Institutions Advisory Program for crypto mixer "
        "intelligence sharing. Initiate Egmont Group notification for international cooperation. "
        "Do not alert the account holder — preserve investigative integrity at all costs."
    ),
    "CASE021": (
        "🚨 RECOMMENDATION: FREEZE AND ESCALATE — ACTIVE PONZI COLLAPSE\n"
        "CRIMES IDENTIFIED: fraud, money_laundering, embezzlement, securities_fraud\n"
        "ACTION: Freeze all Whitmore-linked accounts immediately — Charles Whitmore personal (ACC13001), "
        "Whitmore Capital LLC (ACC13002), and CW Offshore Holdings (ACC13003). "
        "The email directing movement of all investor funds to BVI before investors discover the scheme "
        "is definitive evidence of Ponzi fraud, active flight of assets, and intent to defraud. "
        "Alert SEC Enforcement Division — this is an active securities fraud collapse requiring emergency "
        "coordination. Initiate the investor protection notification protocol without delay. "
        "Refer to FBI for wire fraud, securities fraud, money laundering, and embezzlement investigation. "
        "Seek an emergency court injunction to freeze Anonymous BVI Account (ACC13004) via British Virgin "
        "Islands mutual legal assistance treaty. Engage forensic accountants to reconstruct all investor "
        "fund flows and quantify total investor losses."
    ),
}

VERDICT_REASONS = {
    "freeze_and_escalate": {
        "card_fraud":
            "Multiple high-value transactions at unknown vendors in a foreign jurisdiction within minutes "
            "are a definitive card fraud pattern. Account frozen; escalated to fraud team.",
        "sanctions_violation":
            "Wire transfer to a sanctioned jurisdiction is a direct OFAC violation "
            "under 31 C.F.R. Part 500. Immediate freeze; refer to compliance and legal counsel.",
        "card_skimming":
            "Micro-test charges ($1.00) followed by a large purchase at an unusual location and time "
            "are a textbook card-skimming pattern. Account frozen pending cardholder contact.",
        "structuring":
            "Multiple cash withdrawals just below the $10,000 threshold on the same day constitute "
            "structuring under 31 U.S.C. § 5324. Account frozen; SAR filed immediately.",
        "account_takeover":
            "A large transfer at an unusual hour from an unknown location while the account holder's "
            "normal activity is domestic is consistent with account takeover. Freeze and contact account holder.",
        "fraud":
            "Multiple identical transfers to an unknown exchange within a short window indicate "
            "coordinated fraud. Account frozen; escalated for investigation.",
        "identity_theft":
            "A large loan drawn overnight followed by immediate luxury purchases on an account with "
            "minimal balance are hallmarks of identity theft. Freeze; notify account holder.",
        "money_laundering":
            "Consecutive transfers of diminishing amounts through multiple shell entities constitute a "
            "classic money laundering layering scheme. All linked accounts frozen; SAR filed.",
        "bribery":
            "A Politically Exposed Person receiving anonymous wire transfers without documented "
            "business purpose is a high-risk bribery indicator. Freeze; escalate to compliance.",
        "corruption":
            "Unexplained high-value inflows to a PEP account from unknown sources constitute a strong "
            "corruption indicator under FATF Recommendation 12. Immediate escalation required.",
        "insider_trading":
            "Internal email evidence confirms the employee used non-public material information to direct "
            "stock trades — a clear securities violation. Freeze assets; alert SEC and legal team.",
        "embezzlement":
            "CFO self-approved vendor invoices payable to a personally controlled shell company and "
            "subsequently withdrew cash. This is embezzlement and money laundering. Freeze all linked accounts; refer to law enforcement.",
        "trade_based_money_laundering":
            "Email evidence confirms deliberate over-invoicing to shift value cross-border. "
            "This is trade-based money laundering. Freeze all accounts; notify FinCEN and customs.",
        "terrorism_financing":
            "Crypto mixer usage followed by an international wire with email directing cash delivery in a "
            "conflict zone are strong terrorism financing indicators. Immediate freeze; report to FinCEN and FBI.",
        "possible_terrorism_financing":
            "Crypto mixer usage followed by an international wire with email directing cash delivery in a "
            "conflict zone are strong terrorism financing indicators. Immediate freeze; report to FinCEN and FBI.",
        "tax_evasion":
            "Offshore trust layering with explicitly obscured beneficial ownership, combined with unverified "
            "tax filings and an email admitting regulatory evasion, indicate deliberate tax fraud. Freeze; refer to IRS CI.",
        "securities_fraud":
            "Email evidence and fund movement patterns confirm active securities fraud. "
            "Freeze all linked accounts and refer immediately to SEC Enforcement Division.",
        "default":
            "Multiple confirmed financial crime indicators detected. Account frozen; case escalated to senior compliance officers."
    },
    "request_info": {
        "possible_money_laundering":
            "Transaction pattern is elevated risk but a plausible explanation exists. "
            "Request: source of funds declaration, purpose of transfer, and third-party verification before a final determination.",
        "possible_structuring":
            "Cash deposits are consistent with structuring but the account holder holds a verified business license. "
            "Request: 90-day business cash-flow records and most recent tax return to rule out willful structuring.",
        "possible_terrorism_financing":
            "High-risk indicators present but KYC is incomplete. "
            "Request: full KYC documentation, source of funds proof, and stated purpose of international wire.",
        "default":
            "Case presents ambiguous signals with a plausible legitimate explanation. "
            "Request further documentation from the account holder before delivering a final verdict."
    },
    "clear_suspect": {
        "default":
            "All transactions match the account holder's documented profile and verified activity. "
            "Supporting documents are independently confirmed. No suspicious indicators found. Case closed — no action required."
    }
}

def _get_verdict_reason(verdict: str, crimes: list, case_id: str) -> str:
    if case_id in CASE_RECOMMENDATIONS:
        return CASE_RECOMMENDATIONS[case_id]
    if verdict not in VERDICT_REASONS:
        return "Verdict delivered based on available evidence."
    pool = VERDICT_REASONS[verdict]
    for crime in crimes:
        key = crime.replace(" ", "_").lower()
        if key in pool:
            return pool[key]
    return pool.get("default", "Verdict delivered based on available evidence.")


class FinCrimeEnv:
    def __init__(self, task_id: str = "task1"):
        assert task_id in TASK_POOLS, f"task_id must be one of {list(TASK_POOLS.keys())}"
        self.task_id           = task_id
        self.current_case      = None
        self.current_step      = 0
        self.max_steps         = 5
        self.done              = False
        self.last_reward       = 0.0
        self.cumulative_reward = 0.0
        self.last_action_type  = None
        self.repeat_count      = 0

    def reset(self) -> Observation:
        self.current_case      = random.choice(TASK_POOLS[self.task_id])
        self.current_step      = 0
        self.done              = False
        self.last_reward       = 0.0
        self.cumulative_reward = 0.0
        self.last_action_type  = None
        self.repeat_count      = 0
        return self._build_observation()

    def step(self, action: Dict[str, Any]) -> StepResponse:
        if self.done:
            return StepResponse(
                observation=self._build_observation(),
                reward=0.0, done=True,
                info={"error": "Episode done. Call reset()."}
            )

        self.current_step += 1
        action_type = action.get("type", "unknown")

        penalty = 0.0
        if action_type == self.last_action_type:
            self.repeat_count += 1
            penalty = round(0.1 * self.repeat_count, 2)
            if self.repeat_count >= 2:
                self.done = True
        else:
            self.repeat_count = 0
        self.last_action_type = action_type

        obs_dict = self._build_observation().model_dump(by_alias=True)
        if self.task_id == "task1":
            raw_reward = grade_task1(obs_dict, action)
            info = {"grader": "task1_grader", "raw_score": raw_reward}
        elif self.task_id == "task2":
            raw_reward = grade_task2(obs_dict, action)
            info = {"grader": "task2_grader", "raw_score": raw_reward}
        else:
            raw_reward = grade_task3(obs_dict, action)
            info = {"grader": "task3_grader", "raw_score": raw_reward}

        # Validator requires task scores strictly between 0 and 1.
        # Enforce exclusive bounds by clamping to (eps, 1-eps).
        eps = 1e-3
        final = round(min(max(raw_reward - penalty, eps), 1.0 - eps), 3)
        self.last_reward        = final
        self.cumulative_reward  = round(self.cumulative_reward + final, 3)

        if self.current_step >= self.max_steps:
            self.done = True

        if penalty > 0:
            info["loop_penalty"] = penalty
            info["warning"] = "Repeated action penalized. Try a different action type."

        return StepResponse(
            observation=self._build_observation(),
            reward=final, done=self.done,
            info={**info,
                  "case_id":       self.current_case["case_id"],
                  "case_category": self.current_case.get("category", "unknown")}
        )

    def state(self) -> dict:
        return {
            "observation": self._build_observation(),
            "reward":      self.last_reward,
            "done":        self.done,
            "info": {
                "task_id":           self.task_id,
                "step":              self.current_step,
                "max_steps":         self.max_steps,
                "cumulative_reward": self.cumulative_reward,
                "case_id":           self.current_case["case_id"] if self.current_case else None,
                "case_category":     self.current_case.get("category") if self.current_case else None
            }
        }

    # DEPRECATED: Internal grader replaced by external graders/task1_grader.py
    def _grade_task1(self, action: dict) -> Tuple[float, dict]:
        \"\"\"Placeholder - now using external grader.\"\"\"
        return 0.0, {\"deprecated\": \"Use graders/task1_grader.py\"}

    # DEPRECATED: Internal grader replaced by external graders/task2_grader.py
    def _grade_task2(self, action: dict) -> Tuple[float, dict]:
        \"\"\"Placeholder - now using external grader.\"\"\"
        return 0.0, {\"deprecated\": \"Use graders/task2_grader.py\"}

    # DEPRECATED: Internal grader replaced by external graders/task3_grader.py
    def _grade_task3(self, action: dict) -> Tuple[float, dict]:
        \"\"\"Placeholder - now using external grader.\"\"\"
        return 0.0, {\"deprecated\": \"Use graders/task3_grader.py\"}

    def _grade_task3(self, action: dict) -> Tuple[float, dict]:
        gt    = self.current_case["ground_truth"]
        atype = action.get("type")

        if atype == "investigate":
            notes    = action.get("notes", "").lower()
            crimes   = gt.get("crimes", [])
            evids    = gt.get("key_evidence", [])
            accounts = self.current_case.get("accounts", [])
            txs      = self.current_case.get("transactions", [])

            crime_hits = sum(1 for c in crimes
                             if c.lower().replace("_", " ") in notes or c.lower() in notes)
            evid_hits  = sum(1 for e in evids
                             if e.lower().replace("_", " ") in notes or e.lower() in notes)
            acc_hits   = sum(1 for a in accounts if a.get("account_id", "").lower() in notes)
            tx_hits    = sum(1 for t in txs      if t.get("tx_id", "").lower() in notes)

            reward = round(min(
                0.15
                + crime_hits * 0.07
                + evid_hits  * 0.05
                + acc_hits   * 0.02
                + tx_hits    * 0.01,
                0.40
            ), 3)

            return reward, {
                "investigation_reward":     reward,
                "crimes_mentioned":         crime_hits,
                "crimes_expected":          len(crimes),
                "evidence_mentioned":       evid_hits,
                "accounts_referenced":      acc_hits,
                "transactions_referenced":  tx_hits,
                "max_investigation_reward": 0.40,
                "hint": (
                    f"Investigation covers {crime_hits}/{len(crimes)} expected crime type(s). "
                    f"Consider mentioning: {', '.join(c.replace('_',' ') for c in crimes)}. "
                    "Reference specific transaction IDs and account IDs for a higher score."
                )
            }

        if atype == "deliver_verdict":
            case_id         = self.current_case["case_id"]
            correct_verdict = gt.get("verdict", "")
            pred_verdict    = action.get("verdict", "")
            v_match         = 1.0 if pred_verdict == correct_verdict else 0.0

            true_crimes = set(gt.get("crimes", []))
            pred_crimes = set(action.get("crimes", []))
            if true_crimes:
                union_c = true_crimes | pred_crimes
                c_score = round(len(true_crimes & pred_crimes) / len(union_c), 3) if union_c else 0.0
            else:
                c_score = 1.0 if not pred_crimes else round(max(0.0, 1.0 - len(pred_crimes) * 0.15), 3)

            true_evid = set(gt.get("key_evidence", []))
            pred_evid = set(action.get("evidence", []))
            if true_evid:
                e_score = round(len(true_evid & pred_evid) / len(true_evid), 3)
            else:
                e_score = 1.0 if not pred_evid else 0.5

            reasoning    = action.get("reasoning", "")
            words        = reasoning.split()
            length_score = min(len(words) / 50, 1.0)
            reason_lower = reasoning.lower()
            cr_hits = sum(1 for c in true_crimes
                          if c.lower().replace("_", " ") in reason_lower or c.lower() in reason_lower)
            ev_hits = sum(1 for e in true_evid
                          if e.lower().replace("_", " ") in reason_lower or e.lower() in reason_lower)
            r_score = round(min(
                length_score * 0.4
                + (cr_hits / max(len(true_crimes), 1)) * 0.3
                + (ev_hits  / max(len(true_evid),  1)) * 0.3,
                1.0
            ), 3)

            reward = round(
                v_match * 0.40
                + c_score * 0.25
                + e_score * 0.25
                + r_score * 0.10,
                3
            )
            self.done = True

            return reward, {
                "verdict_correct":       bool(v_match),
                "expected_verdict":      correct_verdict,
                "predicted_verdict":     pred_verdict,
                "crime_score":           c_score,
                "expected_crimes":       list(true_crimes),
                "predicted_crimes":      list(pred_crimes),
                "evidence_score":        e_score,
                "expected_evidence":     list(true_evid),
                "reasoning_score":       r_score,
                "reasoning_word_count":  len(words),
                "score_breakdown": {
                    "verdict_weight_0.40":   round(v_match  * 0.40, 3),
                    "crime_weight_0.25":     round(c_score  * 0.25, 3),
                    "evidence_weight_0.25":  round(e_score  * 0.25, 3),
                    "reasoning_weight_0.10": round(r_score  * 0.10, 3),
                    "total":                 reward
                },
                "recommendation": _get_verdict_reason(correct_verdict, list(true_crimes), case_id),
                "improvement_hint": _build_improvement_hint(
                    v_match, c_score, e_score, r_score,
                    correct_verdict, true_crimes, true_evid, pred_crimes, pred_evid
                ),
                "category": self.current_case.get("category", "unknown")
            }

        return 0.0, {
            "error": "Unknown action type for task3. Use 'investigate' or 'deliver_verdict'.",
            "hint": (
                'Step 1: {"type":"investigate","notes":"Your detailed investigation notes..."}\n'
                'Step 2: {"type":"deliver_verdict","verdict":"freeze_and_escalate",'
                '"crimes":["money_laundering"],"evidence":["TX001"],"reasoning":"..."}'
            )
        }

    def _build_observation(self) -> Observation:
        if not self.current_case:
            return Observation(
                case_id="NONE", task_id=self.task_id,
                description="No case loaded", step=0, max_steps=self.max_steps
            )
        c = self.current_case

        if self.task_id == "task1":
            instr = (
                'Analyze transactions and flag suspicious ones.\n'
                'Action: {"type":"flag_transactions","tx_ids":["TX001",...],"risk_level":"low/medium/high/critical"}'
            )
        elif self.task_id == "task2":
            instr = (
                'Identify the shell account network: which accounts are shells, the source account, '
                'and the final beneficiary. Use the transfer_chain field to trace the money flow.\n'
                'Action: {"type":"identify_network","shell_accounts":["ACC001",...],"source":"ACC001","beneficiary":"ACC005"}'
            )
        else:
            instr = (
                'Conduct a multi-step investigation then deliver a verdict.\n'
                'Step 1 — Investigate: {"type":"investigate","notes":"Detailed analysis..."}\n'
                'Step 2 — Verdict:     {"type":"deliver_verdict","verdict":"freeze_and_escalate/clear_suspect/request_info",'
                '"crimes":["money_laundering",...],"evidence":["TX001","email_tip",...],"reasoning":"..."}\n'
                'Verdicts: freeze_and_escalate (confirmed crime), clear_suspect (no fraud), request_info (needs more info).'
            )

        def safe_txs(lst):
            out = []
            for t in lst:
                try:
                    out.append(Transaction.model_validate(t))
                except Exception:
                    pass
            return out

        def safe_accs(lst):
            out = []
            for a in lst:
                try:
                    out.append(Account.model_validate(a))
                except Exception:
                    pass
            return out

        def safe_chain(lst):
            out = []
            for h in lst:
                try:
                    out.append(TransferHop.model_validate(h))
                except Exception:
                    pass
            return out

        def safe_emails(lst):
            out = []
            for e in lst:
                try:
                    out.append(Email.model_validate(e))
                except Exception:
                    pass
            return out

        def safe_docs(lst):
            out = []
            for d in lst:
                try:
                    out.append(SupportingDoc.model_validate(d))
                except Exception:
                    pass
            return out

        # Heuristic for base risk (0.0 to 1.0)
        risk = 0.05 # Baseline
        txs = c.get("transactions", [])
        if len(txs) > 3: risk += 0.1
        if any(t.get("amount", 0) > 10000 for t in txs): risk += 0.15
        if any(t.get("location") == "International" for t in txs): risk += 0.2
        
        emails = c.get("emails", [])
        keywords = ["urgent", "secret", "private", " Damascus", "Cayman", "BVI", "mixer", "obscure", "investor"]
        if any(any(k.lower() in e.get("body", "").lower() for k in keywords) for e in emails):
            risk += 0.25
            
        docs = c.get("supporting_docs", [])
        if any(not d.get("verified", True) for d in docs): risk += 0.1
        
        risk = round(min(risk, 0.95), 3)

        return Observation(
            case_id=c["case_id"],
            task_id=self.task_id,
            description=c["description"],
            instruction=instr,
            step=self.current_step,
            max_steps=self.max_steps,
            transactions=safe_txs(c.get("transactions", [])),
            accounts=safe_accs(c.get("accounts", [])),
            transfer_chain=safe_chain(c.get("transfer_chain", [])),
            emails=safe_emails(c.get("emails", [])),
            supporting_docs=safe_docs(c.get("supporting_docs", [])),
            suspect=c.get("suspect"),
            base_risk=risk
        )


def _build_improvement_hint(
    v_match, c_score, e_score, r_score,
    correct_verdict, true_crimes, true_evid, pred_crimes, pred_evid
) -> str:
    hints = []
    if not v_match:
        hints.append(f"Verdict wrong — expected '{correct_verdict}'.")
    if c_score < 0.8:
        missing = list(true_crimes - pred_crimes)
        extra   = list(pred_crimes - true_crimes)
        if missing: hints.append(f"Missing crime(s): {', '.join(missing)}.")
        if extra:   hints.append(f"Incorrect crime(s): {', '.join(extra)}.")
    if e_score < 0.7:
        missing_ev = list(true_evid - pred_evid)
        if missing_ev:
            hints.append(f"Missing evidence: {', '.join(list(missing_ev)[:4])}.")
    if r_score < 0.6:
        hints.append(
            "Reasoning too short or lacks crime/evidence references. "
            "Aim for 50+ words and name specific transaction IDs and crime types."
        )
    return " | ".join(hints) if hints else "Good verdict — review score breakdown for incremental improvements."
