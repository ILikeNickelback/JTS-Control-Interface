@echo off

REM Change to your Git repository directory
cd /d "C:\Users\Christopher\Desktop\Code"
<<<<<<< HEAD

REM Prompt the user for a commit message
set /p commit_message=Enter commit message: 
=======
>>>>>>> c3363de (Auto commit message)

REM Check the status of changes
git status

REM Add all changes to the staging area
git add .

REM Commit changes with the user-provided message
git commit -m "%commit_message%"

REM Push the changes to the remote repository (e.g., main branch)
git push origin main

REM Pause so the window doesn't close immediately
pause
