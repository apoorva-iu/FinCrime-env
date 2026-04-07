"""validate_submission.py — basic pre-submission checks
Performs lightweight checks:
- parses openenv.yaml
- ensures Dockerfile doesn't contain unsafe COPY patterns
- tries to run a quick /health HTTP check against ENV_BASE_URL
- (optional) tries to run `docker build` if docker is available
This script is a convenience helper; CI should run stricter checks.
"""
import os
import sys
import yaml
import subprocess
import requests
import shutil

ROOT = os.path.dirname(__file__)
OPENENV = os.path.join(ROOT, "openenv.yaml")
DOCKERF = os.path.join(ROOT, "Dockerfile")

errors = []
print("[VALIDATE] Starting basic submission validation...")

# 1) openenv.yaml parse
try:
    with open(OPENENV, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    print("[VALIDATE] openenv.yaml parsed OK. Found tasks:", [t.get("id") for t in data.get("tasks", [])])
except Exception as e:
    errors.append(f"openenv.yaml parse error: {e}")

# 2) Dockerfile quick lint
try:
    with open(DOCKERF, "r", encoding="utf-8") as f:
        df = f.read()
    if "COPY uv.lock" in df or "uv.lock*" in df:
        errors.append("Dockerfile contains 'uv.lock*' copy which will fail if file missing.")
    else:
        print("[VALIDATE] Dockerfile basic checks OK.")
except Exception as e:
    errors.append(f"Dockerfile read error: {e}")

# 3) ENV health check (if ENV_BASE_URL set)
env_url = os.environ.get("ENV_BASE_URL", "http://localhost:7860")
try:
    r = requests.get(f"{env_url}/health", timeout=5)
    if r.status_code == 200:
        print(f"[VALIDATE] Environment health OK at {env_url}/health")
    else:
        print(f"[VALIDATE] Environment health returned status {r.status_code}")
except Exception as e:
    print(f"[VALIDATE] Could not reach {env_url}/health: {e}")

# 3b) openenv CLI validate (if installed)
if shutil.which("openenv"):
    try:
        print("[VALIDATE] Running 'openenv validate openenv.yaml'")
        proc = subprocess.run(["openenv", "validate", OPENENV], check=True, capture_output=True, text=True, timeout=30)
        print("[VALIDATE] openenv validate output:\n", proc.stdout)
    except Exception as e:
        errors.append(f"openenv validate failed: {e}")
else:
    print("[VALIDATE] openenv CLI not found — skipping schema validate (install openenv-core to enable)")

# 4) Docker build (optional)
if os.environ.get("RUN_DOCKER_BUILD", "0") == "1":
    print("[VALIDATE] Attempting docker build (this may take a while)...")
    try:
        proc = subprocess.run(["docker", "build", "-t", "fincrime-env", ROOT], check=True, capture_output=True, text=True, timeout=900)
        print("[VALIDATE] docker build succeeded")
    except Exception as e:
        errors.append(f"docker build failed: {e}")

if errors:
    print("[VALIDATE] ERRORS FOUND:")
    for e in errors:
        print(" - ", e)
    sys.exit(2)

print("[VALIDATE] Basic validation completed — no blocking issues detected.")
sys.exit(0)
