#!/bin/bash

# 虚拟环境激活脚本

echo "激活Python虚拟环境..."

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "虚拟环境不存在，正在创建..."
    python3 -m venv venv
    echo "虚拟环境创建完成"
fi

# 激活虚拟环境
source venv/bin/activate

echo "虚拟环境已激活"
echo "Python路径: $(which python)"
echo "Pip路径: $(which pip)"

# 检查依赖是否安装
echo "检查依赖包..."
python -c "import pyautogui, tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装依赖包..."
    pip install -r requirements.txt
    echo "依赖包安装完成"
else
    echo "依赖包已安装"
fi

echo ""
echo "=== 使用说明 ==="
echo "1. 运行命令行版本: python mouse_clicker.py --help"
echo "2. 运行GUI版本: python mouse_clicker_gui.py"
echo "3. 运行配置执行器: python config_executor.py --help"
echo "4. 退出虚拟环境: deactivate"
echo ""