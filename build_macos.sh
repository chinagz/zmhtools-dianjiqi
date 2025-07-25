
#!/bin/bash
# macOS 构建脚本

echo "开始构建 macOS 版本..."

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 已激活虚拟环境"
fi

# 安装依赖（添加错误处理和超时设置）
echo "正在安装PyInstaller..."
pip install --timeout=300 --no-warn-script-location pyinstaller || {
    echo "⚠️ PyInstaller安装失败，尝试重新安装..."
    pip install --timeout=600 --no-warn-script-location pyinstaller
}

echo "正在安装项目依赖..."
pip install --timeout=300 --no-warn-script-location -r requirements.txt || {
    echo "⚠️ 依赖安装失败，尝试重新安装..."
    pip install --timeout=600 --no-warn-script-location -r requirements.txt
}

echo "✅ 依赖安装完成"

# 构建（添加更多稳定性选项）
echo "开始构建可执行文件..."
pyinstaller --onefile --windowed --name="小宝工具集之点击器" \
    --icon=icon.png \
    --hidden-import=pynput \
    --hidden-import=pynput.mouse \
    --hidden-import=pynput.keyboard \
    --hidden-import=pyautogui \
    --hidden-import=PIL \
    --hidden-import=tkinter \
    --hidden-import=tkinter.ttk \
    --hidden-import=threading \
    --hidden-import=json \
    --add-data="background.png:." \
    --add-data="icon.png:." \
    --noconfirm \
    --clean \
    --log-level=INFO \
    mouse_clicker_macos.py

if [ $? -ne 0 ]; then
    echo "❌ 构建失败，错误代码: $?"
    exit $?
fi

echo "✅ 构建成功"

# 创建输出目录
mkdir -p dist/macos
mv dist/小宝工具集之点击器 dist/macos/

echo "✅ macOS 版本构建完成: dist/macos/小宝工具集之点击器"
