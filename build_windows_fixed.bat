@echo off
REM Windows 构建脚本 - 修复版本
REM 解决交互式输入和构建中断问题

setlocal enabledelayedexpansion

echo ==========================================
echo 🚀 开始构建 Windows 版本 (修复版)
echo ==========================================

REM 设置环境变量避免交互式输入
set PYTHONUNBUFFERED=1
set PYTHONDONTWRITEBYTECODE=1
set PYINSTALLER_CONFIG_DIR=%TEMP%\pyinstaller

REM 激活虚拟环境（如果存在）
if exist "venv_py311\Scripts\activate.bat" (
    call venv_py311\Scripts\activate.bat
    echo ✅ 已激活虚拟环境 venv_py311
) else if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ 已激活虚拟环境 venv
) else (
    echo ⚠️ 未找到虚拟环境，使用系统Python
)

REM 检查Python版本
python --version
if !ERRORLEVEL! NEQ 0 (
    echo ❌ Python未安装或不在PATH中
    exit /b 1
)

REM 升级pip
echo 📦 升级pip...
python -m pip install --upgrade pip --quiet --no-warn-script-location

REM 安装依赖（添加错误处理和超时设置）
echo 📦 安装PyInstaller...
python -m pip install --timeout=600 --quiet --no-warn-script-location pyinstaller>=5.0.0 || (
    echo ⚠️ PyInstaller安装失败，尝试重新安装...
    python -m pip install --timeout=900 --quiet --no-warn-script-location pyinstaller>=5.0.0
)

echo 📦 安装项目依赖...
python -m pip install --timeout=600 --quiet --no-warn-script-location -r requirements.txt || (
    echo ⚠️ 依赖安装失败，尝试重新安装...
    python -m pip install --timeout=900 --quiet --no-warn-script-location -r requirements.txt
)

echo ✅ 依赖安装完成

REM 清理之前的构建文件
echo 🧹 清理之前的构建文件...
if exist "build" rmdir /s /q "build" 2>nul
if exist "dist" rmdir /s /q "dist" 2>nul
if exist "*.spec" del /q "*.spec" 2>nul

REM 创建输出目录
mkdir "dist\windows" 2>nul

REM 构建设置
set "build_success=0"
set "max_attempts=3"
set "app_name=小宝工具集之点击器"

echo 🔨 开始构建可执行文件...
echo ====================================

for /L %%i in (1,1,%max_attempts%) do (
    echo 🔄 尝试构建 %%i/%max_attempts%...
    
    REM 使用Windows专用spec文件构建（如果存在）
    if exist "pyinstaller_windows.spec" (
        echo 📋 使用pyinstaller_windows.spec文件构建...
        python -m PyInstaller pyinstaller_windows.spec ^|
            --noconfirm ^
            --clean ^
            --log-level=ERROR ^
            --distpath=dist ^
            --workpath=build ^
            --specpath=. 2>build_error.log
    ) else (
        echo 📋 使用命令行参数构建...
        python -m PyInstaller ^
            --onefile ^
            --windowed ^
            --name="%app_name%" ^
            --icon=icon.png ^
            --hidden-import=pynput ^
            --hidden-import=pynput.mouse ^
            --hidden-import=pynput.keyboard ^
            --hidden-import=pyautogui ^
            --hidden-import=PIL ^
            --hidden-import=PIL.Image ^
            --hidden-import=PIL.ImageTk ^
            --hidden-import=tkinter ^
            --hidden-import=tkinter.ttk ^
            --hidden-import=tkinter.scrolledtext ^
            --hidden-import=threading ^
            --hidden-import=json ^
            --add-data="background.png;." ^
            --add-data="icon.png;." ^
            --noconfirm ^
            --clean ^
            --log-level=ERROR ^
            --distpath=dist ^
            --workpath=build ^
            --specpath=. ^
            mouse_clicker_gui.py 2>build_error.log
    )
    
    REM 检查构建结果
    if !ERRORLEVEL! EQU 0 (
        REM 检查输出文件
        if exist "dist\windows\%app_name%.exe" (
            set "build_success=1"
            echo ✅ 构建成功（尝试 %%i/%max_attempts%）
            goto :build_complete
        ) else if exist "dist\%app_name%.exe" (
            REM 移动文件到windows目录
            move "dist\%app_name%.exe" "dist\windows\%app_name%.exe" >nul 2>&1
            if exist "dist\windows\%app_name%.exe" (
                set "build_success=1"
                echo ✅ 构建成功（尝试 %%i/%max_attempts%）
                goto :build_complete
            )
        )
    )
    
    echo ⚠️ 构建尝试 %%i 失败，错误代码: !ERRORLEVEL!
    if exist "build_error.log" (
        echo 📋 错误详情:
        type build_error.log
    )
    
    if %%i LSS %max_attempts% (
        echo ⏳ 等待5秒后重试...
        timeout /t 5 /nobreak >nul 2>&1
        REM 清理失败的构建文件
        if exist "build" rmdir /s /q "build" 2>nul
        if exist "dist" rmdir /s /q "dist" 2>nul
        mkdir "dist\windows" 2>nul
    )
)

:build_complete
if %build_success% EQU 0 (
    echo ❌ 所有构建尝试都失败了
    if exist "build_error.log" (
        echo 📋 最终错误日志:
        type build_error.log
    )
    exit /b 1
)

REM 验证最终输出
if exist "dist\windows\%app_name%.exe" (
    echo ✅ Windows 版本构建完成: dist\windows\%app_name%.exe
    dir "dist\windows\%app_name%.exe"
    echo ==========================================
    echo 🎉 构建成功完成！
    echo ==========================================
) else (
    echo ❌ 未找到最终输出文件
    exit /b 1
)

REM 清理临时文件
if exist "build_error.log" del "build_error.log" 2>nul

echo 按任意键退出...
pause >nul
exit /b 0