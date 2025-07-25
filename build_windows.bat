
@echo off
REM Windows 构建脚本

echo 开始构建 Windows 版本...

REM 激活虚拟环境（如果存在）
if exist "venv" (
    call venv\Scripts\activate.bat
    echo ✅ 已激活虚拟环境
)

REM 安装依赖（添加错误处理和超时设置）
echo 正在安装PyInstaller...
pip install --timeout=300 --no-warn-script-location pyinstaller || (
    echo ⚠️ PyInstaller安装失败，尝试重新安装...
    pip install --timeout=600 --no-warn-script-location pyinstaller
)

echo 正在安装项目依赖...
pip install --timeout=300 --no-warn-script-location -r requirements.txt || (
    echo ⚠️ 依赖安装失败，尝试重新安装...
    pip install --timeout=600 --no-warn-script-location -r requirements.txt
)

echo ✅ 依赖安装完成

REM 清理之前的构建文件
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "*.spec" del /q "*.spec"

REM 构建（添加更多稳定性选项和中断处理）
echo 开始构建可执行文件...

REM 设置错误处理
setlocal enabledelayedexpansion
set "build_success=0"
set "max_attempts=2"

for /L %%i in (1,1,%max_attempts%) do (
    echo 尝试构建 %%i/%max_attempts%...
    
    REM 使用Windows专用spec文件构建（如果存在）
     if exist "pyinstaller_windows.spec" (
         echo 使用pyinstaller_windows.spec文件构建...
         pyinstaller pyinstaller_windows.spec --noconfirm --clean --log-level=WARN
     ) else if exist "pyinstaller.spec" (
         echo 使用pyinstaller.spec文件构建...
         pyinstaller pyinstaller.spec --noconfirm --clean --log-level=WARN
     ) else (
        echo 使用命令行参数构建...
        pyinstaller --onefile --windowed --name="小宝工具集之点击器" ^
            --icon=icon.png ^
            --hidden-import=pynput ^
            --hidden-import=pynput.mouse ^
            --hidden-import=pynput.keyboard ^
            --hidden-import=pyautogui ^
            --hidden-import=PIL ^
            --hidden-import=tkinter ^
            --hidden-import=tkinter.ttk ^
            --hidden-import=threading ^
            --hidden-import=json ^
            --add-data="background.png;." ^
            --add-data="icon.png;." ^
            --noconfirm ^
            --clean ^
            --log-level=WARN ^
            mouse_clicker_gui.py
    )
    
    REM 检查构建结果
     if !ERRORLEVEL! EQU 0 (
         REM 检查Windows专用spec文件的输出路径
         if exist "dist\windows\小宝工具集之点击器.exe" (
             set "build_success=1"
             echo ✅ 构建成功（尝试 %%i/%max_attempts%）
             goto :build_complete
         ) else if exist "dist\小宝工具集之点击器.exe" (
             set "build_success=1"
             echo ✅ 构建成功（尝试 %%i/%max_attempts%）
             goto :build_complete
         )
     )
    
    echo ⚠️ 构建尝试 %%i 失败，错误代码: !ERRORLEVEL!
    if %%i LSS %max_attempts% (
        echo 等待5秒后重试...
        timeout /t 5 /nobreak >nul
        REM 清理失败的构建文件
        if exist "build" rmdir /s /q "build"
        if exist "dist" rmdir /s /q "dist"
    )
)

:build_complete
if %build_success% EQU 0 (
    echo ❌ 所有构建尝试都失败了
    exit /b 1
)

echo ✅ 构建成功

REM 确保输出文件在正确位置
if exist "dist\小宝工具集之点击器.exe" (
    if not exist "dist\windows" mkdir "dist\windows"
    move "dist\小宝工具集之点击器.exe" "dist\windows\"
    echo ✅ 文件已移动到Windows目录
)

REM 验证最终输出
if exist "dist\windows\小宝工具集之点击器.exe" (
    echo ✅ Windows 版本构建完成: dist\windows\小宝工具集之点击器.exe
) else (
    echo ❌ 未找到最终输出文件
    exit /b 1
)
