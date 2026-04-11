# Changelog

## Unreleased — Phase 2 fixes (2026-04-11)

- Add graders for tasks `task1`, `task2`, `task3` under `graders/`.
- Clamp grader and environment scores to be strictly within (0, 1) to satisfy validator.
- Update `openenv.yaml` to reference graders for each task.
- Harden `inference.py` to prevent unhandled exceptions and always emit structured logs.
- Update `validate_submission.py` to call `openenv validate` on the project directory.
- Add CI workflow (GitHub Actions) to run `python validate_submission.py` on push.

## Notes
- After making these changes, run `python validate_submission.py` locally and resubmit.
