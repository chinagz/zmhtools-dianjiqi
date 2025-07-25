
@echo off
REM Windows 构建脚本

echo 开始构建 Windows 版本...

REM 激活虚拟环境（如果存在）
if exist "venv" (
    call venv\Scripts\activate.bat
    echo ✅ 已激活虚拟环境
)

REM 安装依赖
pip install pyinstaller
pip install -r requirements.txt

REM 构建
pyinstaller --onefile --windowed --name="小宝工具集之点击器" ^
    --icon=icon.png ^
    --hidden-import=pynput ^
    --hidden-import=pynput.mouse ^
    --hidden-import=pynput.keyboard ^
    --hidden-import=pyautogui ^
    --hidden-import=PIL ^
    --hidden-import=tkinter ^
    --noconfirm ^
    --clean ^
    mouse_clicker_gui.py

REM 创建输出目录
if not exist "dist\windows" mkdir "dist\windows"
move dist\小宝工具集之点击器.exe dist\windows\

echo ✅ Windows 版本构建完成: dist\windows\小宝工具集之点击器.exe
