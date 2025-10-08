@echo off
chcp 65001 >nul

echo ==================================
echo 🎯 学生选座系统启动脚本
echo ==================================

REM 检查Python是否已安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 未安装，请先安装Python
    pause
    exit /b 1
)

echo ✅ Python 已安装

REM 启动应用
echo 🚀 正在启动学生选座系统...
echo ==================================
python seat_selection.py

pause