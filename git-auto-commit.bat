@echo off

REM Change to your Git repository directory
cd /d "C:\path\to\your\repository"

REM Check the status of changes
git status

REM Add all changes to the staging area
git add .

REM Commit changes with a default message or a custom one
git commit -m "Auto commit message"

REM Push the changes to the remote repository (e.g., main branch)
git push origin main

REM Pause so the window doesn't close immediately
pause
