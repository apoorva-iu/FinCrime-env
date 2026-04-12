# Validator Fix for Hackathon Submission - APPROVED PLAN

**Current Status**: Plan approved. Integrating external graders into env.py.

## Detailed Steps from Approved Plan:

### 1. Create/Update TODO.md [✅ COMPLETED]

- Document approved plan with progress tracking.

### 2. Edit env.py [⏳ PENDING]

- Import graders/task1_grader.py, task2_grader.py, task3_grader.py
- In FinCrimeEnv.step(): replace internal \_grade_taskX() calls with grader.grade(obs.model_dump(by_alias=True), action)
- Preserve env info dicts (add grader score to info).
- Remove/comment internal \_grade_taskX methods.

### 3. Test Locally [⏳ PENDING]

- Run `python validate_submission.py`
- Start server: `uvicorn main:app --host 0.0.0.0 --port 7860 --reload`
- Test /reset + /step API calls for all 3 tasks, verify grader scores (0.001-0.999).
- Run `openenv validate .` if openenv-core installed.

### 4. Validation & Resubmit [⏳ PENDING]

- Commit changes: `git add . && git commit -m "Integrate external graders per validator reqs"`
- Push to GitHub: `git push`
- Resubmit to HF Space.
- Monitor Phase 2 deep validation.

**Next Action**: Proceed with env.py edit. User: Confirm after each step.
