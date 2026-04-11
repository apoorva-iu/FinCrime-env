# Validator Fix for Hackathon Submission

Current Issue: "Not enough tasks with graders" (3 graders exist but not detected).

Plan Steps:

1. Install openenv-core & run `openenv validate .`
2. Fix openenv.yaml grader refs/paths
3. Test graders CLI
4. Rerun validate_submission.py + docker build
5. Commit/push/resubmit

Progress:

- 🔄 Installing openenv-core & validating
- ⏳ Awaiting validate output to edit
