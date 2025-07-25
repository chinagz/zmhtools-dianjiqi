#!/bin/bash

# GitHub Actions 自动化构建设置脚本
# 使用方法：./setup_github_actions.sh

echo "🚀 开始设置GitHub Actions自动化构建..."

# 检查是否已经是Git仓库
if [ ! -d ".git" ]; then
    echo "📁 初始化Git仓库..."
    git init
    
    # 创建.gitignore文件
    echo "📝 创建.gitignore文件..."
    cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
PYTHONPATH

# PyInstaller
*.manifest
*.spec

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# macOS
.DS_Store
.AppleDouble
.LSOverride

# Windows
Thumbs.db
ehthumbs.db
Desktop.ini

# 构建产物
dist/
build/
*.app
*.exe

# 配置文件（可能包含敏感信息）
config.ini
*.log
EOF
    
    echo "✅ Git仓库初始化完成"
else
    echo "✅ 已存在Git仓库"
fi

# 检查GitHub Actions配置文件
if [ -f ".github/workflows/build.yml" ]; then
    echo "✅ GitHub Actions配置文件已存在"
else
    echo "❌ 未找到GitHub Actions配置文件"
    echo "请确保已创建 .github/workflows/build.yml 文件"
    exit 1
fi

# 检查构建脚本
echo "🔍 检查构建脚本..."
scripts=("build_macos.sh" "build_windows.bat" "build_linux.sh")
for script in "${scripts[@]}"; do
    if [ -f "$script" ]; then
        echo "✅ $script 存在"
        # 为shell脚本添加执行权限
        if [[ "$script" == *.sh ]]; then
            chmod +x "$script"
            echo "  → 已添加执行权限"
        fi
    else
        echo "❌ $script 不存在"
    fi
done

# 检查requirements.txt
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt 存在"
else
    echo "⚠️  requirements.txt 不存在，创建基本版本..."
    cat > requirements.txt << EOF
pyinstaller>=5.0
pynput>=1.7.6
tkinter-tooltip>=2.0.0
EOF
    echo "✅ 已创建 requirements.txt"
fi

# 添加所有文件到Git
echo "📦 添加文件到Git..."
git add .

# 检查是否有变更需要提交
if git diff --staged --quiet; then
    echo "ℹ️  没有新的变更需要提交"
else
    echo "💾 提交变更..."
    git commit -m "添加GitHub Actions自动化构建配置
    
- 添加多平台构建工作流
- 配置Windows、macOS、Linux自动构建
- 添加构建脚本和依赖文件
- 更新.gitignore文件"
    echo "✅ 变更已提交"
fi

# 显示下一步操作指南
echo ""
echo "🎉 GitHub Actions设置完成！"
echo ""
echo "📋 下一步操作："
echo "1. 在GitHub上创建新仓库（如果还没有）"
echo "2. 添加远程仓库："
echo "   git remote add origin https://github.com/你的用户名/你的仓库名.git"
echo ""
echo "3. 推送到GitHub："
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "4. 查看自动构建："
echo "   访问 https://github.com/你的用户名/你的仓库名/actions"
echo ""
echo "💡 提示："
echo "- 推送后会自动触发构建"
echo "- 构建完成后可在Actions页面下载可执行文件"
echo "- 创建Release标签会自动发布到Release页面"
echo ""
echo "📖 详细说明请查看：GITHUB_ACTIONS_GUIDE.md"

# 显示当前Git状态
echo ""
echo "📊 当前Git状态："
git status --short

echo ""
echo "🔗 有用的命令："
echo "查看远程仓库：git remote -v"
echo "查看分支：git branch -a"
echo "查看提交历史：git log --oneline -5"
echo "创建标签：git tag v1.0.0 && git push origin v1.0.0"