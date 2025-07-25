
#!/bin/bash
# macOS 构建脚本

echo "开始构建 macOS 版本..."

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 已激活虚拟环境"
fi

# 安装依赖
pip install pyinstaller
pip install -r requirements.txt

# 构建
pyinstaller --onefile --windowed --name="鼠标点击器"     --hidden-import=pynput     --hidden-import=pyautogui     --hidden-import=PIL     --hidden-import=tkinter     mouse_clicker_macos.py

# 创建输出目录
mkdir -p dist/macos
mv dist/鼠标点击器 dist/macos/

echo "✅ macOS 版本构建完成: dist/macos/鼠标点击器"
