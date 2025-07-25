#!/bin/bash

# 鼠标点击工具GUI启动脚本（使用虚拟环境）

echo "正在启动鼠标模拟点击工具..."

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "虚拟环境不存在，正在创建..."
    python3 -m venv venv
    echo "虚拟环境创建完成"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 检查依赖是否安装
echo "检查依赖包..."
python -c "import pyautogui, tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装依赖包..."
    pip install -r requirements.txt
fi

# 启动GUI程序
echo "启动图形界面..."
python mouse_clicker_gui.py