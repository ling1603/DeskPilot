@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

cd /d "%~dp0"

if not exist "README_new.md" (
    echo [ERROR] 未找到 README_new.md
    echo 请将本文件与 README_new.md 一起放到 DeskPilot 仓库根目录。
    pause
    exit /b 1
)

for /f "tokens=1-4 delims=/ " %%a in ("%date%") do (
    set D=%%a-%%b-%%c
)

for /f "tokens=1-3 delims=:." %%a in ("%time%") do (
    set T=%%a%%b%%c
)

set T=%T: =0%
set BACKUP=README.backup.%D%-%T%.md

if exist "README.md" (
    copy /Y "README.md" "%BACKUP%" >nul
    echo [OK] 已备份旧 README：%BACKUP%
) else (
    echo [WARN] 当前目录没有旧 README.md，将直接创建新 README.md
)

copy /Y "README_new.md" "README.md" >nul

if errorlevel 1 (
    echo [ERROR] README 替换失败。
    pause
    exit /b 1
)

echo.
echo [OK] README.md 已替换完成。
echo 建议继续执行：git diff README.md
echo.
pause
