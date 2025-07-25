
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
- macOS: `dist/macos/鼠标点击器`
- Windows: `dist/windows/鼠标点击器.exe`
- Linux: `dist/linux/鼠标点击器`

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
