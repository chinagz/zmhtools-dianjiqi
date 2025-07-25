#!/bin/bash
# 快速构建脚本 - macOS版本
# 用于快速打包当前项目为可执行程序

set -e  # 遇到错误立即退出

echo "🚀 开始快速构建 macOS 版本..."
echo "======================================"

# 检查主程序文件
if [ ! -f "mouse_clicker_macos.py" ]; then
    echo "❌ 错误: 未找到 mouse_clicker_macos.py 文件"
    echo "请在包含主程序文件的目录中运行此脚本"
    exit 1
fi

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo "📦 激活虚拟环境..."
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
else
    echo "⚠️  未找到虚拟环境，使用系统Python"
fi

# 检查并安装 PyInstaller
echo "🔍 检查 PyInstaller..."
if ! python -c "import PyInstaller" 2>/dev/null; then
    echo "📥 安装 PyInstaller..."
    pip install pyinstaller
    echo "✅ PyInstaller 安装完成"
else
    echo "✅ PyInstaller 已安装"
fi

# 安装项目依赖
if [ -f "requirements.txt" ]; then
    echo "📥 安装项目依赖..."
    pip install -r requirements.txt
    echo "✅ 依赖安装完成"
fi

# 清理之前的构建
echo "🧹 清理之前的构建..."
rm -rf build dist *.spec
echo "✅ 清理完成"

# 开始构建
echo "🔨 开始构建可执行程序..."
pyinstaller \
    --onefile \
    --windowed \
    --name="小宝工具集之点击器" \
    --hidden-import=pynput \
    --hidden-import=pyautogui \
    --hidden-import=PIL \
    --hidden-import=tkinter \
    --hidden-import=threading \
    --hidden-import=json \
    --hidden-import=time \
    --add-data="README.md:." \
    mouse_clicker_macos.py

# 检查构建结果
if [ -f "dist/小宝工具集之点击器" ]; then
    echo "✅ 构建成功！"
    echo "📁 可执行文件位置: $(pwd)/dist/小宝工具集之点击器"
    echo "📊 文件大小: $(du -h dist/小宝工具集之点击器 | cut -f1)"
    
    # 设置执行权限
    chmod +x "dist/小宝工具集之点击器"
    echo "✅ 已设置执行权限"
    
    echo ""
    echo "🎉 构建完成！"
    echo "======================================"
    echo "📋 使用说明:"
    echo "  1. 双击运行: dist/小宝工具集之点击器"
    echo "  2. 或命令行运行: ./dist/小宝工具集之点击器"
    echo "  3. 首次运行需要授予辅助功能权限"
    echo "     (系统偏好设置 > 安全性与隐私 > 隐私 > 辅助功能)"
    echo ""
    echo "📦 分发说明:"
    echo "  - 可以直接分发 dist/小宝工具集之点击器 文件"
    echo "  - 无需安装Python环境即可运行"
    echo "  - 文件较大是正常现象（包含了完整的Python运行时）"
else
    echo "❌ 构建失败！"
    echo "请检查上面的错误信息"
    exit 1
fi