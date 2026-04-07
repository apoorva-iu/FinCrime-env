@echo off
REM Windows smoke test: validate, start server, check health, reset, run inference
echo [SMOKE] Running validate_submission.py
python validate_submission.py || echo validate failed

echo [SMOKE] Start server (run this in a separate terminal if you prefer)
start "FinCrime Server" cmd /k "python -m uvicorn main:app --host 0.0.0.0 --port 7860"
echo Server started in new window; waiting 4 seconds
timeout /t 4 >nul

echo [SMOKE] Checking /health
powershell -Command "(Invoke-WebRequest -UseBasicParsing http://localhost:7860/health).Content" || echo health check failed

echo [SMOKE] Resetting a session (task1)
powershell -Command "Invoke-WebRequest -Uri http://localhost:7860/reset -Method POST -Body '{\"task_id\":\"task1\"}' -ContentType 'application/json' | Select-Object -Expand Content" || echo reset failed

echo [SMOKE] Run inference in this terminal (requires env vars set)
echo set HF_TOKEN=your_token
echo set MODEL_NAME=Qwen/...
echo set ENV_BASE_URL=http://localhost:7860
echo python inference.py --task task1

echo [SMOKE] Done
