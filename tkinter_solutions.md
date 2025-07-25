# macOS上安装支持tkinter的Python解决方案

由于当前Python环境不支持tkinter，以下是几种不使用Homebrew的解决方案：

## 方案1：从python.org下载官方Python（推荐）

1. 访问 https://www.python.org/downloads/
2. 下载最新的macOS安装包（.pkg文件）
3. 运行安装包，官方Python自带tkinter支持
4. 安装完成后，使用以下命令：

```bash
# 使用官方Python创建虚拟环境
/usr/local/bin/python3 -m venv venv_official
source venv_official/bin/activate
pip install -r requirements.txt
python mouse_clicker_gui.py
```

## 方案2：使用Miniconda/Anaconda

1. 下载Miniconda：https://docs.conda.io/en/latest/miniconda.html
2. 安装后创建新环境：

```bash
# 创建conda环境
conda create -n mouse_clicker python=3.11 tk
conda activate mouse_clicker
pip install -r requirements.txt
python mouse_clicker_gui.py
```

## 方案3：使用pyenv

1. 安装pyenv（不使用brew）：

```bash
# 使用curl安装pyenv
curl https://pyenv.run | bash

# 添加到shell配置
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc

# 重新加载shell
source ~/.zshrc

# 安装Python
pyenv install 3.11.0
pyenv local 3.11.0

# 创建虚拟环境
python -m venv venv_pyenv
source venv_pyenv/bin/activate
pip install -r requirements.txt
python mouse_clicker_gui.py
```

## 方案4：临时解决方案 - 仅使用命令行版本

如果暂时无法安装支持tkinter的Python，可以使用命令行版本：

```bash
# 激活现有虚拟环境
source venv/bin/activate

# 使用命令行版本
python mouse_clicker.py --help
python mouse_clicker.py --position
python mouse_clicker.py --click 100 200

# 或使用交互模式
python mouse_clicker.py
```

## 方案5：修改现有Python（高级用户）

尝试重新编译Python以支持tkinter（需要Xcode命令行工具）：

```bash
# 安装Xcode命令行工具
xcode-select --install

# 下载Python源码并重新编译（复杂，不推荐）
```

## 推荐顺序

1. **方案1（官方Python）** - 最简单可靠
2. **方案2（Conda）** - 环境管理最好
3. **方案4（命令行）** - 临时使用
4. **方案3（pyenv）** - 灵活但复杂
5. **方案5（重新编译）** - 最复杂

## 验证tkinter是否可用

安装完成后，使用以下命令验证：

```bash
python -c "import tkinter; print('tkinter可用')"
```

如果没有错误输出，说明tkinter已可用。