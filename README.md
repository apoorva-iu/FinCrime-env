---
title: FinCrime-env
emoji: 🕵️
colorFrom: blue
colorTo: red
sdk: docker
app_file: app.py
app_port: 7860
pinned: false
---

# Pre-submission validation (recommended)

Run the lightweight validator before submitting or deploying. It parses openenv.yaml, lints the Dockerfile, attempts a /health check, and — if available — runs openenv validate:

python validate_submission.py
To run a stricter CI-style validation (includes a Docker build) set the env var and enable Docker locally or in CI:

# Optional: attempt docker build during validation (may take several minutes)

RUN_DOCKER_BUILD=1 python validate_submission.py
Hugging Face Spaces (Docker) — notes
This repo includes a working Dockerfile. To deploy to a Hugging Face Space using Docker:

Create a new Space and choose the Dockerfile option.
Push this repository to the Space's GitHub repo or upload the files.
Set the required secrets/variables in the Space: HF_TOKEN (or OPENAI_API_KEY), MODEL_NAME, API_BASE_URL.
The Space will build the provided Dockerfile and serve the FastAPI app on port 7860.

FinCrimeEnv 🕵️⚖️
openenv HuggingFace

AI Financial Crime Investigation Environment — OpenEnv Compatible

An environment where AI agents investigate financial crimes — spotting fraud, tracing money laundering networks, and delivering legal verdicts. Built for the Meta PyTorch OpenEnv Hackathon.

Motivation
Banks lose $485 billion annually to financial crime. Every major bank employs teams of investigators who manually review transactions, trace money flows, and write case reports. This environment simulates exactly that workflow — allowing AI agents to be trained and evaluated on the same tasks human investigators perform daily.

FinCrimeEnv fills a real gap: no existing OpenEnv environment covers financial crime investigation, despite it being one of the highest-value applications for AI agents in regulated industries.

Environment Description
The agent plays the role of a financial crime investigator at a bank. It receives case files containing transactions, account details, emails, and documents. It must analyze the evidence and take appropriate action.

Tasks
Task Difficulty Description Max Steps
task1 Easy Flag suspicious transactions from a list 5
task2 Medium Trace money laundering network — find shell accounts, source, beneficiary 5
task3 Hard Full investigation — analyze emails, transactions, docs → deliver verdict 5
Task 1 — Spot the Fraud (Easy)
Agent receives a list of bank transactions. Must identify suspicious ones and set overall risk level.

Scoring: F1(flagged*transactions) * 0.8 + risk*level_accuracy * 0.2
Task 2 — Trace the Network (Medium)
Agent receives multiple accounts with a transfer chain. Must identify shell companies, source, and final beneficiary.

Scoring: shell*f1 * 0.4 + source*correct * 0.3 + beneficiary_correct \* 0.3
Task 3 — Deliver the Verdict (Hard)
Agent receives a full case file with transactions, emails, and supporting documents. Must investigate over multiple steps then deliver a legal verdict.

Scoring: verdict*correct * 0.4 + crime*score * 0.25 + evidence*score * 0.25 + reasoning*score * 0.1
Action Space
Task 1
{
"type": "flag_transactions",
"tx_ids": ["TX002", "TX003"],
"risk_level": "high"
}
Task 2
{
"type": "identify_network",
"shell_accounts": ["ACC001", "ACC002", "ACC003"],
"source": "ACC001",
"beneficiary": "ACC005"
}
Task 3 — Investigation step
{
"type": "investigate",
"notes": "Found structuring pattern with 3x $9000 withdrawals and insider email evidence"
}
Task 3 — Final verdict
{
"type": "deliver_verdict",
"verdict": "freeze_and_escalate",
"crimes": ["money_laundering", "structuring", "insider_trading"],
"evidence": ["TX101", "TX102", "TX103", "email_tip"],
"reasoning": "Three financial crimes confirmed. Large transfers through shell company ACC6002 constitute money laundering. Three $9000 withdrawals indicate deliberate structuring below $10,000 reporting threshold. Insider email confirms trading coordination."
}
Verdict options: freeze_and_escalate | request_info | clear_suspect

Observation Space
{
"case_id": "CASE011",
"task_id": "task3",
"description": "Insider trading + money laundering + structuring by bank employee",
"step": 1,
"max_steps": 5,
"instruction": "Investigate fully then deliver verdict...",
"suspect": {"name": "Robert Chen", "employee": true, "department": "Trading Desk"},
"transactions": [...],
"accounts": [...],
"emails": [...],
"supporting_docs": [...]
}
Reward Function
Rewards are milestone-based — partial credit at every step:

Investigation steps: 0.15 – 0.35 based on quality of findings
Verdict step: 0.0 – 1.0 based on 4 components
Loop penalty: repeated actions penalized with escalating -0.1 per repeat
Better actions always yield higher reward than worse ones
Setup & Usage
Local
git clone https://github.com/apoorva-iu/fincrime-env
cd fincrime-env
pip install uv
uv pip install -r requirements.txt

# Create .env file

echo "API_BASE_URL=https://api-inference.huggingface.co/v1" > .env
echo "MODEL_NAME=Qwen/Qwen2.5-72B-Instruct" >> .env
echo "HF_TOKEN=hf_your_token_here" >> .env

# Start server

uvicorn main:app --host 0.0.0.0 --port 7860

# Open UI

# http://localhost:7860/ui

Docker
docker build -t fincrime-env .
docker run -p 7860:7860 \
 -e HF_TOKEN=your_token \
 -e MODEL_NAME=Qwen/Qwen2.5-72B-Instruct \
 fincrime-env
Run Inference
python inference.py --task task1 # Easy
python inference.py --task task2 # Medium
python inference.py --task task3 # Hard

### Windows-specific instructions & explanations

1. Environment variables (Windows PowerShell):

```powershell
$env:HF_TOKEN = "hf_your_token_here"
$env:MODEL_NAME = "Qwen/Qwen2.5-72B-Instruct"
$env:ENV_BASE_URL = "http://localhost:7860"
python -m uvicorn main:app --host 0.0.0.0 --port 7860
In CMD use set instead of $env::

set HF_TOKEN=hf_your_token_here
set MODEL_NAME=Qwen/Qwen2.5-72B-Instruct
set ENV_BASE_URL=http://localhost:7860
python -m uvicorn main:app --host 0.0.0.0 --port 7860
What the example curl commands do:
curl -sS http://localhost:7860/health — checks the server health endpoint and prints the JSON response.
curl -sS -X POST http://localhost:7860/reset -H 'Content-Type: application/json' -d '{"task_id":"task1"}' — starts a new session for task1; the response includes session_id and the initial observation.
On Windows use the PowerShell equivalents in run_smoke_tests.bat.

Running the baseline inference (what those export lines mean):
export HF_TOKEN="hf_..." (Linux/macOS) or set HF_TOKEN=... (Windows): set your Hugging Face/OpenAI API key used by inference.py.
export MODEL_NAME="Qwen/..." sets which model identifier to call.
export ENV_BASE_URL="http://localhost:7860" tells the inference script where the local environment is running.
After setting the env vars, run:

python inference.py --task task1
python inference.py --task task2
python inference.py --task task3
Each run will print a single [START] block, multiple [STEP] lines, and one [END] block. These are the structured logs required by the contest validator.

Submission: GitHub + Hugging Face Spaces (recommended flow)
Commit and push your repository to GitHub (see git commands earlier).
On Hugging Face create a new Space and select the Dockerfile option. Connect it to the GitHub repo or push the code to the Space's repo.
In the Space settings add secrets: HF_TOKEN (or OPENAI_API_KEY) and MODEL_NAME.
The Space will build the provided Dockerfile and host the FastAPI app. The validator will ping /reset; ensure it returns HTTP 200.
Pre-submission quick checklist (Windows)
Open a PowerShell terminal and run:
python validate_submission.py
Start the server in PowerShell (leave it running):
python -m uvicorn main:app --host 0.0.0.0 --port 7860
In another PowerShell terminal run:
Invoke-WebRequest -UseBasicParsing http://localhost:7860/health
Invoke-WebRequest -UseBasicParsing -Uri http://localhost:7860/reset -Method POST -Body '{"task_id":"task1"}' -ContentType 'application/json'
python inference.py --task task1
If all commands succeed and the inference prints [START]/[STEP]/[END], you are ready to push to GitHub and deploy to a Hugging Face Space.

See COMPLIANCE.md for the full compliance checklist and grading estimate.


---

## API Endpoints

| Endpoint  | Method | Description                                                   |
| --------- | ------ | ------------------------------------------------------------- |
| `/reset`  | POST   | Start new episode — returns observation                       |
| `/step`   | POST   | Take action — returns observation, reward, done, info         |
| `/state`  | POST   | Get current state — returns last step reward (NOT cumulative) |
| `/tasks`  | GET    | List all tasks with descriptions                              |
| `/health` | GET    | Health check                                                  |
| `/ui`     | GET    | Interactive dashboard UI                                      |
| `/docs`   | GET    | Swagger API documentation                                     |

---

## Baseline Scores

Scores using `Qwen/Qwen2.5-72B-Instruct` via HuggingFace Inference API:

| Task                        | Score      | Difficulty |
| --------------------------- | ---------- | ---------- |
| task1 — Spot the Fraud      | 0.85 – 1.0 | Easy       |
| task2 — Trace the Network   | 0.80 – 1.0 | Medium     |
| task3 — Deliver the Verdict | 0.70 – 1.0 | Hard       |

_Scores vary across runs due to random case selection from 15 diverse cases._

---

## Environment Variables

API_BASE_URL = https://api-inference.huggingface.co/v1 MODEL_NAME = Qwen/Qwen2.5-72B-Instruct HF_TOKEN = hf_your_token_here OPENAI_API_KEY = (alternative to HF_TOKEN) ENV_BASE_URL = http://localhost:7860


---

## Project Structure

fincrime-env/ ├── main.py — FastAPI server (reset/step/state endpoints) ├── env.py — Environment logic + graders + reward function ├── models.py — Typed Pydantic models (Observation, Action, Reward) ├── inference.py — Baseline LLM agent script ├── cases.json — 15 synthetic fraud cases (easy/medium/hard) ├── openenv.yaml — OpenEnv spec metadata ├── pyproject.toml — Project dependencies ├── Dockerfile — Container configuration ├── static/ │ └── index.html — Interactive dashboard UI └── README.md — This file


```
