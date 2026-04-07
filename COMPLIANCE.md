# FinCrimeEnv — Compliance & Submission Checklist

This document summarizes the automated validation steps required before submitting the environment to the OpenEnv contest or deploying to Hugging Face Spaces.

Required checks (must pass before submission)

- [ ] `openenv validate openenv.yaml` — OpenEnv schema validation (install `openenv` CLI via `pip install openenv-core`).
- [ ] `python validate_submission.py` — lightweight validator (parses `openenv.yaml`, lints Dockerfile, tries `/health`).
- [ ] Start server and confirm `/health` and `/reset` respond with HTTP 200.
- [ ] `python inference.py --task task1|task2|task3` — run baseline inference end-to-end; confirm structured stdout follows the `[START]...[STEP]...[END]` format and all JSON actions parse correctly.
- [ ] `docker build -t fincrime-env .` — Docker image builds without errors.
- [ ] Deploy to Hugging Face Space (Docker) and confirm the automated ping returns HTTP 200 for `/reset`.

Notes & remediation steps

- If `openenv validate` fails: adjust `openenv.yaml` according to the validator errors. Common fixes: quote `const`/`enum` strings, ensure `observation_space` and `action_space` conform to JSON Schema.
- If Docker build fails: inspect the Docker build log for missing files or permission issues. Use `.dockerignore` to keep context small.
- If inference output is not valid JSON: open `inference.py` and run with a small sample observation; the script contains robust fallbacks to heuristics.

Grading estimate (preliminary)

- Real-world utility: 26/30
- Tasks & graders: 22/25
- Environment design: 17/20
- Code & spec compliance: 11/15 (pending `openenv validate` and final inference smoke runs)
- Creativity & novelty: 8/10

Total (estimated): 84 / 100

Next actions I can perform for you

- Run `python validate_submission.py` in CI (I already added a GitHub Actions workflow). You must enable Docker in the runner to build the image.
- Run the inference smoke tests locally with your credentials (I cannot call your LLM keys). I can help tune prompts if the validator rejects the output.
