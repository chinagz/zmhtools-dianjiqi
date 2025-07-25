#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多平台打包脚本
自动为 macOS、Windows、Linux 三个平台打包鼠标点击器GUI程序
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(cmd, description=""):
    """执行命令并处理错误"""
    print(f"\n{'='*50}")
    print(f"执行: {description}")
    print(f"命令: {cmd}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        print("✅ 执行成功")
        if result.stdout:
            print(f"输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 执行失败: {e}")
        if e.stdout:
            print(f"标准输出: {e.stdout}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        return False

def check_dependencies():
    """检查必要的依赖"""
    print("检查依赖...")
    
    # 检查 PyInstaller
    try:
        import PyInstaller
        print("✅ PyInstaller 已安装")
    except ImportError:
        print("❌ PyInstaller 未安装，正在安装...")
        if not run_command("pip install pyinstaller", "安装 PyInstaller"):
            return False
    
    # 检查项目依赖
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        print("✅ 找到 requirements.txt")
        if not run_command("pip install -r requirements.txt", "安装项目依赖"):
            return False
    else:
        print("⚠️  未找到 requirements.txt，跳过依赖安装")
    
    return True

def clean_build_dirs():
    """清理之前的构建目录"""
    print("\n清理构建目录...")
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"✅ 已删除 {dir_name}")
    
    # 删除 .spec 文件
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"✅ 已删除 {spec_file}")

def build_for_current_platform():
    """为当前平台构建"""
    current_platform = platform.system().lower()
    print(f"\n当前平台: {current_platform}")
    
    # 基础命令
    base_cmd = "pyinstaller --onefile --windowed --name=小宝工具集之点击器"
    
    # 添加隐藏导入
    hidden_imports = [
        "--hidden-import=pynput",
        "--hidden-import=pyautogui", 
        "--hidden-import=PIL",
        "--hidden-import=tkinter",
        "--hidden-import=threading",
        "--hidden-import=json",
        "--hidden-import=time"
    ]
    
    # 平台特定配置
    if current_platform == "darwin":  # macOS
        platform_cmd = f"{base_cmd} {' '.join(hidden_imports)} mouse_clicker_macos.py"
        output_dir = "dist/macos"
    elif current_platform == "windows":  # Windows
        platform_cmd = f"{base_cmd} --icon=icon.ico {' '.join(hidden_imports)} mouse_clicker_macos.py"
        output_dir = "dist/windows"
    else:  # Linux
        platform_cmd = f"{base_cmd} {' '.join(hidden_imports)} mouse_clicker_macos.py"
        output_dir = "dist/linux"
    
    # 执行构建
    if run_command(platform_cmd, f"构建 {current_platform} 版本"):
        # 创建平台特定目录并移动文件
        os.makedirs(output_dir, exist_ok=True)
        
        # 查找生成的可执行文件
        dist_files = list(Path('dist').glob('*'))
        for file in dist_files:
            if file.is_file() and file.name != output_dir.split('/')[-1]:
                target = Path(output_dir) / file.name
                shutil.move(str(file), str(target))
                print(f"✅ 已移动到 {target}")
        
        return True
    return False

def create_cross_platform_spec():
    """创建跨平台的 spec 文件模板"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['mouse_clicker_macos.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[
        'pynput',
        'pyautogui',
        'PIL',
        'tkinter',
        'threading',
        'json',
        'time'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='小宝工具集之点击器',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

# macOS 特定配置
app = BUNDLE(
    exe,
    name='小宝工具集之点击器.app',
    icon=None,
    bundle_identifier='com.zmhtools.mouseclicker',
)
'''
    
    with open('mouse_clicker_cross_platform.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("✅ 已创建跨平台 spec 文件")

def create_build_scripts():
    """创建各平台的构建脚本"""
    
    # macOS 构建脚本
    macos_script = '''
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
pyinstaller --onefile --windowed --name="小宝工具集之点击器" \
    --hidden-import=pynput \
    --hidden-import=pyautogui \
    --hidden-import=PIL \
    --hidden-import=tkinter \
    mouse_clicker_macos.py

# 创建输出目录
mkdir -p dist/macos
mv dist/小宝工具集之点击器 dist/macos/

echo "✅ macOS 版本构建完成: dist/macos/小宝工具集之点击器"
'''
    
    # Windows 构建脚本
    windows_script = '''
@echo off
REM Windows 构建脚本

echo 开始构建 Windows 版本...

REM 激活虚拟环境（如果存在）
if exist "venv" (
    call venv\\Scripts\\activate.bat
    echo ✅ 已激活虚拟环境
)

REM 安装依赖
pip install pyinstaller
pip install -r requirements.txt

REM 构建
pyinstaller --onefile --windowed --name="小宝工具集之点击器" ^
    --hidden-import=pynput ^
    --hidden-import=pyautogui ^
    --hidden-import=PIL ^
    --hidden-import=tkinter ^
    mouse_clicker_macos.py

REM 创建输出目录
mkdir dist\\windows 2>nul
move dist\\小宝工具集之点击器.exe dist\\windows\\

echo ✅ Windows 版本构建完成: dist\\windows\\小宝工具集之点击器.exe
pause
'''
    
    # Linux 构建脚本
    linux_script = '''
#!/bin/bash
# Linux 构建脚本

echo "开始构建 Linux 版本..."

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ 已激活虚拟环境"
fi

# 安装依赖
pip install pyinstaller
pip install -r requirements.txt

# 构建
pyinstaller --onefile --name="小宝工具集之点击器" \
    --hidden-import=pynput \
    --hidden-import=pyautogui \
    --hidden-import=PIL \
    --hidden-import=tkinter \
    mouse_clicker_macos.py

# 创建输出目录
mkdir -p dist/linux
mv dist/小宝工具集之点击器 dist/linux/

echo "✅ Linux 版本构建完成: dist/linux/小宝工具集之点击器"
'''
    
    # 写入文件
    scripts = {
        'build_macos.sh': macos_script,
        'build_windows.bat': windows_script,
        'build_linux.sh': linux_script
    }
    
    for filename, content in scripts.items():
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 为 shell 脚本添加执行权限
        if filename.endswith('.sh'):
            os.chmod(filename, 0o755)
        
        print(f"✅ 已创建 {filename}")

def create_readme():
    """创建构建说明文档"""
    readme_content = '''
# 多平台打包说明

## 自动构建（推荐）

运行主构建脚本：
```bash
python build_all_platforms.py
```

## 手动构建

### macOS
```bash
./build_macos.sh
```

### Windows
```cmd
build_windows.bat
```

### Linux
```bash
./build_linux.sh
```

## 输出目录

构建完成后，可执行文件将位于：
- macOS: `dist/macos/小宝工具集之点击器`
- Windows: `dist/windows/小宝工具集之点击器.exe`
- Linux: `dist/linux/小宝工具集之点击器`

## 注意事项

1. **跨平台构建**：每个平台的可执行文件需要在对应的操作系统上构建
2. **依赖安装**：确保已安装所有必要的依赖包
3. **权限设置**：
   - macOS: 需要在"系统偏好设置 > 安全性与隐私 > 隐私"中授予辅助功能权限
   - Windows: 可能需要管理员权限运行
   - Linux: 可能需要安装额外的系统依赖

## 故障排除

如果构建失败，请检查：
1. Python 版本（推荐 3.8+）
2. 依赖包是否完整安装
3. 系统权限设置
4. 防病毒软件是否阻止

## 文件大小优化

如果生成的文件过大，可以尝试：
1. 使用 `--exclude-module` 排除不必要的模块
2. 使用 UPX 压缩（`--upx-dir`）
3. 分析依赖并精简（`pyi-archive_viewer`）
'''
    
    with open('BUILD_README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✅ 已创建构建说明文档")

def main():
    """主函数"""
    print("🚀 多平台打包脚本")
    print("=" * 50)
    
    # 检查当前目录是否包含主程序文件
    if not os.path.exists('mouse_clicker_macos.py'):
        print("❌ 未找到 mouse_clicker_macos.py 文件")
        print("请在包含主程序文件的目录中运行此脚本")
        return False
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 依赖检查失败")
        return False
    
    # 清理构建目录
    clean_build_dirs()
    
    # 为当前平台构建
    if build_for_current_platform():
        print("\n✅ 当前平台构建成功")
    else:
        print("\n❌ 当前平台构建失败")
    
    # 创建跨平台构建资源
    create_cross_platform_spec()
    create_build_scripts()
    create_readme()
    
    print("\n" + "=" * 50)
    print("🎉 多平台打包资源创建完成！")
    print("\n📁 生成的文件：")
    print("  - build_macos.sh      (macOS 构建脚本)")
    print("  - build_windows.bat   (Windows 构建脚本)")
    print("  - build_linux.sh      (Linux 构建脚本)")
    print("  - mouse_clicker_cross_platform.spec (跨平台配置)")
    print("  - BUILD_README.md     (构建说明文档)")
    print("\n📋 下一步：")
    print("  1. 在对应平台上运行相应的构建脚本")
    print("  2. 查看 BUILD_README.md 了解详细说明")
    print("  3. 在 dist/ 目录中找到生成的可执行文件")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        sys.exit(1)