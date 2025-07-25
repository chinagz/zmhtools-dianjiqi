# GitHub Actions 自动化构建指南

## 📋 概述

本项目已配置GitHub Actions自动化构建系统，可以在推送代码时自动为三个平台（Windows、macOS、Linux）构建可执行文件。

## 🚀 如何使用

### 1. 推送代码触发构建

```bash
# 将代码推送到GitHub仓库
git add .
git commit -m "更新代码"
git push origin main  # 或 master
```

### 2. 查看构建状态

1. 访问你的GitHub仓库
2. 点击 **Actions** 标签页
3. 查看最新的工作流运行状态

### 3. 下载构建产物

构建完成后，可以通过以下方式获取可执行文件：

#### 方法一：从Actions页面下载
1. 进入 **Actions** → 选择完成的工作流
2. 在 **Artifacts** 部分下载对应平台的文件：
   - `windows-executable` - Windows版本
   - `macos-executable` - macOS版本  
   - `linux-executable` - Linux版本

#### 方法二：通过Release发布
1. 创建新的Release标签：
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```
2. 在GitHub上创建Release，构建的可执行文件会自动附加到Release中

## 🔧 构建配置说明

### 触发条件
- 推送到 `main` 或 `master` 分支
- 创建Pull Request
- 发布Release

### 构建矩阵
| 平台 | 运行环境 | 输出文件名 | 构建脚本 |
|------|----------|------------|----------|
| Windows | windows-latest | mouse_clicker_windows.exe | build_windows.bat |
| macOS | macos-latest | 小宝工具集之点击器 | build_macos.sh |
| Linux | ubuntu-latest | mouse_clicker_linux | build_linux.sh |

### Python版本
- 使用Python 3.9（稳定且兼容性好）

## 📁 文件结构

```
.github/
└── workflows/
    └── build.yml          # GitHub Actions配置文件

build_windows.bat          # Windows构建脚本
build_macos.sh            # macOS构建脚本  
build_linux.sh            # Linux构建脚本
requirements.txt          # Python依赖
mouse_clicker_macos.py    # 主程序文件
```

## 🛠️ 自定义配置

### 修改Python版本
在 `.github/workflows/build.yml` 中修改：
```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.10'  # 改为你需要的版本
```

### 修改触发分支
```yaml
on:
  push:
    branches: [ main, develop ]  # 添加其他分支
```

### 添加构建选项
在对应的构建脚本中添加PyInstaller参数：
```bash
# 例如在build_windows.bat中
pyinstaller --onefile --windowed --icon=icon.ico mouse_clicker_macos.py
```

## 🔍 故障排除

### 常见问题

1. **构建失败 - 依赖问题**
   - 检查 `requirements.txt` 是否包含所有必要依赖
   - 确保依赖版本兼容

2. **构建失败 - 脚本权限**
   - Linux/macOS脚本需要执行权限：
     ```bash
     chmod +x build_macos.sh build_linux.sh
     git add . && git commit -m "添加执行权限" && git push
     ```

3. **找不到可执行文件**
   - 检查构建脚本是否正确生成到 `dist/` 目录
   - 确认文件名与配置中的 `executable_name` 匹配

4. **macOS权限问题**
   - 用户下载后可能需要在"系统偏好设置" → "安全性与隐私"中允许运行

### 查看构建日志
1. 进入Actions页面
2. 点击失败的工作流
3. 展开对应步骤查看详细日志

## 📊 构建状态徽章

在README.md中添加构建状态徽章：

```markdown
![Build Status](https://github.com/你的用户名/你的仓库名/workflows/Build%20Multi-Platform%20Executables/badge.svg)
```

## 🎯 最佳实践

1. **版本管理**
   - 使用语义化版本号（如v1.0.0）
   - 为重要版本创建Release

2. **测试**
   - 在本地测试构建脚本
   - 确保所有平台的脚本都能正常工作

3. **文档**
   - 及时更新README和构建说明
   - 记录重要的配置变更

4. **安全**
   - 不要在代码中包含敏感信息
   - 使用GitHub Secrets存储密钥

## 💡 高级功能

### 条件构建
只在特定条件下构建：
```yaml
- name: Build only on tag
  if: startsWith(github.ref, 'refs/tags/')
```

### 缓存依赖
加速构建过程：
```yaml
- name: Cache pip dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
```

### 通知
构建完成后发送通知：
```yaml
- name: Notify on success
  if: success()
  run: echo "构建成功！"
```

---

**提示**：首次设置后，每次推送代码都会自动触发构建，无需手动操作！