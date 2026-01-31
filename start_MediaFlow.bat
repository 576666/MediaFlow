@echo off
chcp 65001 >nul
title MediaFlow 启动器

REM 获取当前脚本所在目录
set "SCRIPT_DIR=%~dp0"

REM 切换到脚本所在目录并使用start命令运行Python脚本，隐藏控制台
cd /d "%SCRIPT_DIR%"

REM 使用start命令启动Python脚本，这将减少控制台窗口的显示
start /min pythonw.exe main.py

REM 如果pythonw.exe不存在，则使用python.exe
if errorlevel 1 (
    start /min python.exe main.py
)