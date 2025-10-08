#!/bin/bash

# 学生选座系统启动脚本

echo "=================================="
echo "🎯 学生选座系统启动脚本"
echo "=================================="

# 检查Python是否已安装
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

echo "✅ Python3 已安装"

# 启动应用
echo "🚀 正在启动学生选座系统..."
echo "=================================="
python3 seat_selection.py