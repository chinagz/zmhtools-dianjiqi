#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化的构建脚本
自动检测平台并执行相应的构建流程
包含错误恢复和重试机制
"""

import os
import sys
import subprocess
import platform
import time
from pathlib import Path

def get_platform():
    """检测当前平台"""
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'darwin':
        return 'macos'
    elif system == 'linux':
        return 'linux'
    else:
        return 'unknown'

def run_command(cmd, timeout=600, retries=2):
    """执行命令，支持重试机制"""
    for attempt in range(retries + 1):
        try:
            print(f"🔄 执行命令 (尝试 {attempt + 1}/{retries + 1}): {cmd}")
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode == 0:
                print(f"✅ 命令执行成功")
                if result.stdout:
                    print(f"输出: {result.stdout}")
                return True
            else:
                print(f"❌ 命令执行失败 (退出码: {result.returncode})")
                if result.stderr:
                    print(f"错误: {result.stderr}")
                if attempt < retries:
                    print(f"⏳ 等待5秒后重试...")
                    time.sleep(5)
                    
        except subprocess.TimeoutExpired:
            print(f"⏰ 命令执行超时 ({timeout}秒)")
            if attempt < retries:
                print(f"⏳ 等待10秒后重试...")
                time.sleep(10)
        except Exception as e:
            print(f"💥 命令执行异常: {e}")
            if attempt < retries:
                print(f"⏳ 等待5秒后重试...")
                time.sleep(5)
    
    return False

def setup_virtual_env():
    """设置虚拟环境"""
    print("🔧 检查虚拟环境...")
    
    if not os.path.exists('venv'):
        print("📦 创建虚拟环境...")
        if not run_command(f"{sys.executable} -m venv venv"):
            print("❌ 虚拟环境创建失败")
            return False
    
    # 激活虚拟环境的命令
    current_platform = get_platform()
    if current_platform == 'windows':
        activate_cmd = 'venv\\Scripts\\activate'
    else:
        activate_cmd = 'source venv/bin/activate'
    
    print(f"✅ 虚拟环境就绪: {activate_cmd}")
    return activate_cmd

def install_dependencies(activate_cmd):
    """安装依赖"""
    print("📦 安装依赖包...")
    
    commands = [
        f"{activate_cmd} && python -m pip install --upgrade pip --no-warn-script-location",
        f"{activate_cmd} && pip install --timeout=300 --no-warn-script-location -r requirements.txt",
        f"{activate_cmd} && pip install --timeout=300 --no-warn-script-location pyinstaller"
    ]
    
    for cmd in commands:
        if not run_command(cmd, timeout=900):
            print(f"❌ 依赖安装失败: {cmd}")
            return False
    
    print("✅ 依赖安装完成")
    return True

def build_executable(activate_cmd):
    """构建可执行文件"""
    print("🔨 开始构建可执行文件...")
    
    current_platform = get_platform()
    
    # 使用优化的spec文件构建
    if os.path.exists('pyinstaller.spec'):
        build_cmd = f"{activate_cmd} && pyinstaller pyinstaller.spec"
    else:
        # 回退到传统构建方式
        if current_platform == 'windows':
            build_cmd = f"{activate_cmd} && python build_windows.bat"
        elif current_platform == 'macos':
            build_cmd = f"{activate_cmd} && bash build_macos.sh"
        elif current_platform == 'linux':
            build_cmd = f"{activate_cmd} && bash build_linux.sh"
        else:
            print(f"❌ 不支持的平台: {current_platform}")
            return False
    
    if not run_command(build_cmd, timeout=1200):
        print("❌ 构建失败")
        return False
    
    print("✅ 构建完成")
    return True

def organize_output():
    """整理输出文件"""
    print("📁 整理输出文件...")
    
    current_platform = get_platform()
    dist_dir = Path('dist')
    platform_dir = dist_dir / current_platform
    
    if not platform_dir.exists():
        platform_dir.mkdir(parents=True, exist_ok=True)
    
    # 查找生成的可执行文件
    executable_name = '小宝工具集之点击器'
    if current_platform == 'windows':
        executable_name += '.exe'
    elif current_platform == 'macos':
        executable_name += '.app'
    
    # 移动文件到平台目录
    source_path = dist_dir / executable_name
    target_path = platform_dir / executable_name
    
    if source_path.exists():
        if target_path.exists():
            if target_path.is_dir():
                import shutil
                shutil.rmtree(target_path)
            else:
                target_path.unlink()
        
        source_path.rename(target_path)
        print(f"✅ 可执行文件已移动到: {target_path}")
        return True
    else:
        print(f"❌ 找不到可执行文件: {source_path}")
        return False

def main():
    """主函数"""
    print("🚀 开始优化构建流程...")
    print(f"📋 平台信息: {get_platform()} ({platform.machine()})")
    print(f"🐍 Python版本: {sys.version}")
    
    # 检查必要文件
    required_files = ['requirements.txt', 'mouse_clicker_gui.py']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ 缺少必要文件: {file}")
            return False
    
    # 设置虚拟环境
    activate_cmd = setup_virtual_env()
    if not activate_cmd:
        return False
    
    # 安装依赖
    if not install_dependencies(activate_cmd):
        return False
    
    # 构建可执行文件
    if not build_executable(activate_cmd):
        return False
    
    # 整理输出文件
    if not organize_output():
        return False
    
    print("🎉 构建流程完成！")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)