@echo off
REM Remove committed .env from git index (Windows)
git rm --cached .env || goto :end
del .env
echo Removed .env from index and working tree. Commit the change and push.
:end
