# Validator Fix - Grader Integration [APPROVED & IN PROGRESS]

Current Status: Editing env.py for external graders.

## Steps:

### 1. Create TODO.md [✅ DONE]

### 2. Edit env.py [⏳ IN PROGRESS]

- Replace internal \_grade_taskX with graders/taskX_grader.grade()
- Remove deprecated methods
- Test API calls

### 3. Test [⏳ PENDING]

- curl localhost:8000/health
- reset/step task1-3
- python validate_submission.py
- python inference.py --task task1

### 4. Update TODO & Resubmit [⏳ PENDING]

- Mark steps ✅
- Commit/push to GitHub
- Resubmit HF Space

Next: env.py edit complete → test.
