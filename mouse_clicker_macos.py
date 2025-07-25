#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
macOS优化版鼠标模拟点击工具
专门针对macOS系统的权限和兼容性问题进行优化
"""

import pyautogui
import time
import sys
import platform
import subprocess
import argparse
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
from typing import Tuple, Optional
try:
    from pynput import mouse
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("警告: pynput未安装，将使用简化的录制功能")
    print("要使用完整的全局录制功能，请运行: pip install pynput")

class MacOSMouseClicker:
    def __init__(self):
        # macOS特殊设置
        if platform.system() == 'Darwin':
            # 禁用fail-safe，在macOS上可能导致问题
            pyautogui.FAILSAFE = False
            # 增加操作间隔，提高稳定性
            pyautogui.PAUSE = 0.2
            
            print("macOS优化模式已启用")
            self.check_permissions()
        else:
            # 非macOS系统使用默认设置
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
    
    def check_permissions(self):
        """检查macOS权限"""
        print("正在检查macOS权限...")
        try:
            # 尝试获取鼠标位置来测试权限
            pos = pyautogui.position()
            print(f"✅ 权限检查通过，当前鼠标位置: {pos}")
            
            # 尝试截屏测试屏幕录制权限
            screenshot = pyautogui.screenshot(region=(0, 0, 10, 10))
            print("✅ 屏幕录制权限正常")
            
        except Exception as e:
            print(f"❌ 权限检查失败: {e}")
            print("\n请按以下步骤授予权限：")
            print("1. 打开 系统偏好设置 > 安全性与隐私 > 隐私")
            print("2. 选择 '辅助功能'，添加终端或Python")
            print("3. 选择 '屏幕录制'，添加终端或Python")
            print("4. 重启终端后重试")
    
    def get_screen_info(self):
        """获取屏幕信息，包括缩放比例"""
        try:
            # 获取逻辑屏幕尺寸
            logical_size = pyautogui.size()
            
            # 获取物理屏幕尺寸
            screenshot = pyautogui.screenshot()
            physical_size = screenshot.size
            
            scale_x = physical_size[0] / logical_size[0]
            scale_y = physical_size[1] / logical_size[1]
            
            return {
                'logical_size': logical_size,
                'physical_size': physical_size,
                'scale_x': scale_x,
                'scale_y': scale_y,
                'is_retina': scale_x > 1 or scale_y > 1
            }
        except Exception as e:
            print(f"获取屏幕信息失败: {e}")
            return None
    
    def click_with_applescript(self, x: int, y: int) -> bool:
        """使用AppleScript进行点击（备用方案）"""
        script = f'''
        tell application "System Events"
            -- 获取当前前台应用
            set frontApp to name of first application process whose frontmost is true
            
            -- 激活应用
            tell application frontApp to activate
            delay 0.1
            
            -- 执行点击
            click at {{{x}, {y}}}
        end tell
        '''
        
        try:
            print(f"使用AppleScript点击: ({x}, {y})")
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, check=True)
            print("✅ AppleScript点击成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ AppleScript点击失败: {e}")
            if e.stderr:
                print(f"错误详情: {e.stderr}")
            return False
    
    def safe_click(self, x: int, y: int, button: str = 'left', use_applescript: bool = False) -> bool:
        """安全点击方法"""
        try:
            if use_applescript and platform.system() == 'Darwin':
                return self.click_with_applescript(x, y)
            
            print(f"点击坐标: ({x}, {y}), 按钮: {button}")
            
            # 先移动鼠标到目标位置
            pyautogui.moveTo(x, y, duration=0.1)
            time.sleep(0.1)
            
            # 执行点击
            pyautogui.click(x, y, button=button)
            time.sleep(0.1)
            
            print("✅ 点击成功")
            return True
            
        except Exception as e:
            print(f"❌ pyautogui点击失败: {e}")
            
            # 在macOS上尝试AppleScript备用方案
            if platform.system() == 'Darwin' and not use_applescript:
                print("尝试AppleScript备用方案...")
                return self.click_with_applescript(x, y)
            
            return False
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """获取当前鼠标位置"""
        try:
            pos = pyautogui.position()
            return (pos.x, pos.y)
        except Exception as e:
            print(f"获取鼠标位置失败: {e}")
            return (0, 0)
    
    def double_click(self, x: int, y: int, use_applescript: bool = False) -> bool:
        """双击"""
        if use_applescript and platform.system() == 'Darwin':
            # AppleScript双击
            script = f'''
            tell application "System Events"
                set frontApp to name of first application process whose frontmost is true
                tell application frontApp to activate
                delay 0.1
                double click at {{{x}, {y}}}
            end tell
            '''
            try:
                subprocess.run(['osascript', '-e', script], check=True)
                return True
            except:
                return False
        else:
            try:
                pyautogui.doubleClick(x, y)
                return True
            except Exception as e:
                print(f"双击失败: {e}")
                return False
    
    def right_click(self, x: int, y: int, use_applescript: bool = False) -> bool:
        """右键点击"""
        return self.safe_click(x, y, button='right', use_applescript=use_applescript)
    
    def test_click_methods(self):
        """测试不同的点击方法"""
        print("\n=== 测试点击方法 ===")
        
        # 获取当前鼠标位置作为测试点
        current_x, current_y = self.get_mouse_position()
        test_x, test_y = current_x + 50, current_y + 50
        
        print(f"测试坐标: ({test_x}, {test_y})")
        
        # 测试pyautogui方法
        print("\n1. 测试pyautogui方法:")
        success1 = self.safe_click(test_x, test_y)
        
        time.sleep(1)
        
        # 测试AppleScript方法（仅macOS）
        if platform.system() == 'Darwin':
            print("\n2. 测试AppleScript方法:")
            success2 = self.safe_click(test_x, test_y, use_applescript=True)
        else:
            success2 = True
            print("\n2. 跳过AppleScript测试（非macOS系统）")
        
        if success1 or success2:
            print("\n✅ 至少一种点击方法可用")
        else:
            print("\n❌ 所有点击方法都失败")
            print("请检查系统权限设置")

class MacOSMouseClickerGUI:
    """macOS优化版鼠标点击器GUI界面"""
    
    def __init__(self):
        self.clicker = MacOSMouseClicker()
        self.root = tk.Tk()
        self.root.title("macOS优化版鼠标点击器")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # 运行状态
        self.is_running = False
        self.current_position = tk.StringVar(value="(0, 0)")
        
        # 录制和回放相关变量
        self.is_recording = False
        self.recorded_actions = []
        self.recording_start_time = None
        self.mouse_listener = None
        
        # 创建界面
        self.create_widgets()
        self.update_position()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def create_widgets(self):
        """创建GUI组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 屏幕信息
        info_frame = ttk.LabelFrame(main_frame, text="屏幕信息", padding="5")
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        screen_size = pyautogui.size()
        ttk.Label(info_frame, text=f"屏幕尺寸: {screen_size[0]} x {screen_size[1]}").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(info_frame, text="当前鼠标位置:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(info_frame, textvariable=self.current_position).grid(row=1, column=1, sticky=tk.W)
        
        # 坐标输入框架
        coord_frame = ttk.LabelFrame(main_frame, text="坐标设置", padding="5")
        coord_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(coord_frame, text="X坐标:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.x_entry = ttk.Entry(coord_frame, width=10)
        self.x_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(coord_frame, text="Y坐标:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.y_entry = ttk.Entry(coord_frame, width=10)
        self.y_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        ttk.Button(coord_frame, text="获取当前位置", command=self.get_current_position).grid(row=0, column=4, sticky=tk.W)
        
        # 点击方法选择
        method_frame = ttk.LabelFrame(main_frame, text="点击方法", padding="5")
        method_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.method_var = tk.StringVar(value="pyautogui")
        ttk.Radiobutton(method_frame, text="PyAutoGUI (推荐)", variable=self.method_var, value="pyautogui").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(method_frame, text="AppleScript (备用)", variable=self.method_var, value="applescript").grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        
        # 基本点击操作
        click_frame = ttk.LabelFrame(main_frame, text="基本点击操作", padding="5")
        click_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(click_frame, text="单击", command=self.single_click).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(click_frame, text="双击", command=self.double_click).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(click_frame, text="右键点击", command=self.right_click).grid(row=0, column=2, padx=(0, 5))
        
        # 连续点击设置
        continuous_frame = ttk.LabelFrame(main_frame, text="连续点击设置", padding="5")
        continuous_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(continuous_frame, text="点击次数:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.count_entry = ttk.Entry(continuous_frame, width=10)
        self.count_entry.insert(0, "10")
        self.count_entry.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(continuous_frame, text="间隔时间(秒):").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.interval_entry = ttk.Entry(continuous_frame, width=10)
        self.interval_entry.insert(0, "1.0")
        self.interval_entry.grid(row=0, column=3, sticky=tk.W, padx=(0, 20))
        
        self.start_button = ttk.Button(continuous_frame, text="开始连续点击", command=self.start_continuous_click)
        self.start_button.grid(row=1, column=0, pady=(10, 0))
        
        self.stop_button = ttk.Button(continuous_frame, text="停止", command=self.stop_continuous_click, state="disabled")
        self.stop_button.grid(row=1, column=1, pady=(10, 0), padx=(10, 0))
        
        # 拖拽操作
        drag_frame = ttk.LabelFrame(main_frame, text="拖拽操作", padding="5")
        drag_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(drag_frame, text="起始坐标:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(drag_frame, text="X:").grid(row=0, column=1, sticky=tk.W, padx=(10, 5))
        self.drag_start_x = ttk.Entry(drag_frame, width=8)
        self.drag_start_x.grid(row=0, column=2, padx=(0, 10))
        ttk.Label(drag_frame, text="Y:").grid(row=0, column=3, sticky=tk.W, padx=(0, 5))
        self.drag_start_y = ttk.Entry(drag_frame, width=8)
        self.drag_start_y.grid(row=0, column=4, padx=(0, 20))
        
        ttk.Label(drag_frame, text="结束坐标:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(drag_frame, text="X:").grid(row=1, column=1, sticky=tk.W, padx=(10, 5))
        self.drag_end_x = ttk.Entry(drag_frame, width=8)
        self.drag_end_x.grid(row=1, column=2, padx=(0, 10))
        ttk.Label(drag_frame, text="Y:").grid(row=1, column=3, sticky=tk.W, padx=(0, 5))
        self.drag_end_y = ttk.Entry(drag_frame, width=8)
        self.drag_end_y.grid(row=1, column=4, padx=(0, 20))
        
        ttk.Button(drag_frame, text="执行拖拽", command=self.perform_drag).grid(row=2, column=0, pady=(10, 0))
        
        # 延迟设置
        delay_frame = ttk.LabelFrame(main_frame, text="延迟设置", padding="5")
        delay_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(delay_frame, text="操作前延迟(秒):").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.delay_entry = ttk.Entry(delay_frame, width=10)
        self.delay_entry.insert(0, "3")
        self.delay_entry.grid(row=0, column=1, sticky=tk.W)
        
        # 录制回放功能
        record_frame = ttk.LabelFrame(main_frame, text="录制回放功能", padding="5")
        record_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.record_button = ttk.Button(record_frame, text="开始录制", command=self.start_recording)
        self.record_button.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_record_button = ttk.Button(record_frame, text="停止录制", command=self.stop_recording, state="disabled")
        self.stop_record_button.grid(row=0, column=1, padx=(0, 5))
        
        self.replay_button = ttk.Button(record_frame, text="回放操作", command=self.replay_actions, state="disabled")
        self.replay_button.grid(row=0, column=2, padx=(0, 5))
        
        ttk.Label(record_frame, text="回放次数:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5), pady=(10, 0))
        self.replay_count_entry = ttk.Entry(record_frame, width=10)
        self.replay_count_entry.insert(0, "1")
        self.replay_count_entry.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # 测试功能
        test_frame = ttk.LabelFrame(main_frame, text="测试功能", padding="5")
        test_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(test_frame, text="测试点击方法", command=self.test_methods).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(test_frame, text="显示屏幕信息", command=self.show_screen_info).grid(row=0, column=1, padx=5)
        
        # 日志输出
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="5")
        log_frame.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(9, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Button(log_frame, text="清空日志", command=self.clear_log).grid(row=1, column=0, pady=(5, 0))
        
    def log_message(self, message):
        """添加日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def get_current_position(self):
        """获取当前鼠标位置"""
        try:
            x, y = pyautogui.position()
            self.x_entry.delete(0, tk.END)
            self.x_entry.insert(0, str(x))
            self.y_entry.delete(0, tk.END)
            self.y_entry.insert(0, str(y))
            self.log_message(f"获取当前鼠标位置: ({x}, {y})")
        except Exception as e:
            self.log_message(f"获取鼠标位置失败: {e}")
    
    def update_position(self):
        """更新当前鼠标位置显示"""
        try:
            x, y = pyautogui.position()
            self.current_position.set(f"({x}, {y})")
        except:
            pass
        self.root.after(100, self.update_position)
    
    def apply_delay(self):
        """应用延迟设置"""
        try:
            delay = float(self.delay_entry.get())
            if delay > 0:
                self.log_message(f"等待 {delay} 秒...")
                time.sleep(delay)
        except ValueError:
            self.log_message("延迟时间格式错误，跳过延迟")
    
    def start_continuous_click(self):
        """开始连续点击"""
        if self.is_running:
            return
        
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            count = int(self.count_entry.get())
            interval = float(self.interval_entry.get())
        except ValueError:
            self.log_message("请输入有效的数值")
            return
        
        self.is_running = True
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        # 在新线程中执行连续点击
        thread = threading.Thread(target=self.continuous_click_worker, args=(x, y, count, interval))
        thread.daemon = True
        thread.start()
    
    def continuous_click_worker(self, x, y, count, interval):
        """连续点击工作线程"""
        self.apply_delay()
        
        for i in range(count):
            if not self.is_running:
                break
            
            try:
                if self.method_var.get() == "pyautogui":
                    pyautogui.click(x, y)
                else:
                    self.clicker.click_with_applescript(x, y)
                
                self.log_message(f"第 {i+1} 次点击完成: ({x}, {y})")
                
                if i < count - 1 and self.is_running:
                    time.sleep(interval)
            except Exception as e:
                self.log_message(f"点击失败: {e}")
                break
        
        # 重置按钮状态
        self.root.after(0, self.reset_continuous_buttons)
    
    def stop_continuous_click(self):
        """停止连续点击"""
        self.is_running = False
        self.log_message("停止连续点击")
    
    def reset_continuous_buttons(self):
        """重置连续点击按钮状态"""
        self.is_running = False
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
    
    def perform_drag(self):
        """执行拖拽操作"""
        try:
            start_x = int(self.drag_start_x.get())
            start_y = int(self.drag_start_y.get())
            end_x = int(self.drag_end_x.get())
            end_y = int(self.drag_end_y.get())
        except ValueError:
            self.log_message("请输入有效的拖拽坐标")
            return
        
        self.apply_delay()
        
        try:
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=1, button='left')
            self.log_message(f"拖拽操作完成: 从 ({start_x}, {start_y}) 到 ({end_x}, {end_y})")
        except Exception as e:
            self.log_message(f"拖拽操作失败: {e}")
            
    def get_coordinates(self):
        """获取输入的坐标"""
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            return x, y
        except ValueError:
            raise ValueError("请输入有效的坐标数字")
            
    def single_click(self):
        """执行单击"""
        try:
            x, y = self.get_coordinates()
            use_applescript = self.method_var.get() == "applescript"
            
            # 记录操作（如果正在录制）
            self.record_action("单击", x, y)
            
            self.log_message(f"开始单击坐标 ({x}, {y})，方法: {self.method_var.get()}")
            
            # 在新线程中执行点击，避免阻塞GUI
            threading.Thread(target=self._perform_click, args=(x, y, "single", use_applescript), daemon=True).start()
            
        except ValueError as e:
            self.log_message(f"坐标输入错误: {e}")
            messagebox.showerror("输入错误", str(e))
        except Exception as e:
            self.log_message(f"单击操作失败: {e}")
            messagebox.showerror("操作失败", str(e))
            
    def double_click(self):
        """执行双击"""
        try:
            x, y = self.get_coordinates()
            use_applescript = self.method_var.get() == "applescript"
            
            # 记录操作（如果正在录制）
            self.record_action("双击", x, y)
            
            self.log_message(f"开始双击坐标 ({x}, {y})，方法: {self.method_var.get()}")
            
            threading.Thread(target=self._perform_click, args=(x, y, "double", use_applescript), daemon=True).start()
            
        except ValueError as e:
            self.log_message(f"坐标输入错误: {e}")
            messagebox.showerror("输入错误", str(e))
        except Exception as e:
            self.log_message(f"双击操作失败: {e}")
            messagebox.showerror("操作失败", str(e))
            
    def right_click(self):
        """执行右键点击"""
        try:
            x, y = self.get_coordinates()
            use_applescript = self.method_var.get() == "applescript"
            
            # 记录操作（如果正在录制）
            self.record_action("右键点击", x, y)
            
            self.log_message(f"开始右键点击坐标 ({x}, {y})，方法: {self.method_var.get()}")
            
            threading.Thread(target=self._perform_click, args=(x, y, "right", use_applescript), daemon=True).start()
            
        except ValueError as e:
            self.log_message(f"坐标输入错误: {e}")
            messagebox.showerror("输入错误", str(e))
        except Exception as e:
            self.log_message(f"右键点击操作失败: {e}")
            messagebox.showerror("操作失败", str(e))
            
    def _perform_click(self, x, y, click_type, use_applescript):
        """在后台线程中执行点击操作"""
        try:
            if click_type == "single":
                success = self.clicker.safe_click(x, y, use_applescript=use_applescript)
            elif click_type == "double":
                success = self.clicker.double_click(x, y, use_applescript=use_applescript)
            elif click_type == "right":
                success = self.clicker.right_click(x, y, use_applescript=use_applescript)
            else:
                success = False
                
            if success:
                self.log_message(f"{click_type}点击成功")
            else:
                self.log_message(f"{click_type}点击失败")
                
        except Exception as e:
            self.log_message(f"{click_type}点击异常: {e}")
            
    def test_methods(self):
        """测试点击方法"""
        self.log_message("开始测试点击方法...")
        threading.Thread(target=self._test_methods_thread, daemon=True).start()
        
    def _test_methods_thread(self):
        """在后台线程中测试点击方法"""
        try:
            # 重定向输出到GUI
            import io
            import contextlib
            
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.clicker.test_click_methods()
                
            result = output.getvalue()
            self.log_message("测试结果:")
            for line in result.split('\n'):
                if line.strip():
                    self.log_message(line)
                    
        except Exception as e:
            self.log_message(f"测试失败: {e}")
            
    def show_screen_info(self):
        """显示屏幕信息"""
        try:
            screen_info = self.clicker.get_screen_info()
            if screen_info:
                self.log_message("=== 屏幕信息 ===")
                self.log_message(f"逻辑尺寸: {screen_info['logical_size']}")
                self.log_message(f"物理尺寸: {screen_info['physical_size']}")
                self.log_message(f"缩放比例: {screen_info['scale_x']:.2f}x{screen_info['scale_y']:.2f}")
                self.log_message(f"Retina显示屏: {'是' if screen_info['is_retina'] else '否'}")
            else:
                self.log_message("获取屏幕信息失败")
        except Exception as e:
            self.log_message(f"显示屏幕信息失败: {e}")
    
    def start_recording(self):
        """开始录制操作"""
        if self.is_recording:
            messagebox.showwarning("警告", "已经在录制中")
            return
        
        if not PYNPUT_AVAILABLE:
            # 使用简化的录制功能
            self.is_recording = True
            self.recorded_actions = []
            self.recording_start_time = time.time()
            self.record_button.config(state='disabled')
            self.stop_record_button.config(state='normal')
            self.replay_button.config(state="disabled")
            self.log_message("开始录制操作（仅GUI操作）...")
            self.log_message("提示: 使用GUI界面进行点击操作，系统会自动记录")
            return
        
        # 使用全局鼠标监听
        self.is_recording = True
        self.recorded_actions = []
        self.recording_start_time = time.time()
        
        # 启动鼠标监听器
        self.mouse_listener = mouse.Listener(
            on_click=self.on_mouse_click
        )
        self.mouse_listener.start()
        
        self.record_button.config(state='disabled')
        self.stop_record_button.config(state='normal')
        self.replay_button.config(state="disabled")
        self.log_message("开始录制全局鼠标操作...")
    
    def stop_recording(self):
        """停止录制操作"""
        if not self.is_recording:
            messagebox.showwarning("警告", "当前没有在录制")
            return
        
        self.is_recording = False
        
        # 停止鼠标监听器
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
        
        # 更新按钮状态
        self.record_button.config(state="normal")
        self.stop_record_button.config(state="disabled")
        if self.recorded_actions:
            self.replay_button.config(state="normal")
        
        if self.recorded_actions:
            self.log_message(f"录制完成，共录制了 {len(self.recorded_actions)} 个操作:")
            for i, action in enumerate(self.recorded_actions, 1):
                self.log_message(f"  {i}. {action['type']} 在 ({action['x']}, {action['y']}) - 延迟: {action['delay']:.2f}秒")
        else:
            self.log_message("录制完成，但没有录制到任何操作")
    
    def on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件处理"""
        if not self.is_recording or not pressed:
            return
        
        # 确定点击类型
        if button == mouse.Button.left:
            action_type = "左键单击"
        elif button == mouse.Button.right:
            action_type = "右键单击"
        elif button == mouse.Button.middle:
            action_type = "中键单击"
        else:
            action_type = "其他点击"
        
        self.record_action(action_type, x, y)
    
    def record_action(self, action_type, x, y):
        """记录一个操作"""
        if not self.is_recording:
            return
        
        current_time = time.time()
        delay = current_time - self.recording_start_time if self.recorded_actions else 0
        
        action = {
            'type': action_type,
            'x': x,
            'y': y,
            'delay': delay,
            'timestamp': current_time
        }
        
        self.recorded_actions.append(action)
        self.recording_start_time = current_time
        
        self.log_message(f"录制操作: {action_type} 位置:({x},{y})")
    
    def replay_actions(self):
        """回放录制的操作"""
        if not self.recorded_actions:
            self.log_message("没有录制的操作可以回放")
            return
        
        try:
            replay_count = int(self.replay_count_entry.get())
        except ValueError:
            self.log_message("请输入有效的回放次数")
            return
        
        if replay_count <= 0:
            self.log_message("回放次数必须大于0")
            return
        
        # 在新线程中执行回放
        thread = threading.Thread(target=self.replay_worker, args=(replay_count,))
        thread.daemon = True
        thread.start()
    
    def replay_worker(self, replay_count):
        """回放工作线程"""
        self.log_message(f"开始回放操作，共 {replay_count} 次")
        
        # 给用户准备时间
        initial_delay = float(self.delay_entry.get())
        if initial_delay > 0:
            self.log_message(f"准备时间 {initial_delay} 秒...")
            time.sleep(initial_delay)
        
        for round_num in range(replay_count):
            self.log_message(f"第 {round_num + 1} 轮回放开始")
            
            for i, action in enumerate(self.recorded_actions):
                # 等待延迟时间
                if action['delay'] > 0:
                    time.sleep(action['delay'])
                
                # 执行操作
                try:
                    x, y = action['x'], action['y']
                    action_type = action['type']
                    
                    if self.method_var.get() == "pyautogui":
                        if action_type in ["单击", "左键单击"]:
                            pyautogui.click(x, y)
                        elif action_type == "双击":
                            pyautogui.doubleClick(x, y)
                        elif action_type in ["右键点击", "右键单击"]:
                            pyautogui.rightClick(x, y)
                        elif action_type == "中键单击":
                            pyautogui.click(x, y, button='middle')
                        else:
                            # 其他类型的点击，默认使用左键
                            pyautogui.click(x, y)
                    else:
                        if action_type in ["单击", "左键单击"]:
                            self.clicker.click_with_applescript(x, y)
                        elif action_type == "双击":
                            self.clicker.double_click_with_applescript(x, y)
                        elif action_type in ["右键点击", "右键单击"]:
                            self.clicker.right_click_with_applescript(x, y)
                        else:
                            # 其他类型的点击，默认使用左键
                            self.clicker.click_with_applescript(x, y)
                    
                    self.log_message(f"  执行: {action_type} 位置:({x},{y})")
                    
                except Exception as e:
                    self.log_message(f"  执行失败: {action_type} - {e}")
            
            self.log_message(f"第 {round_num + 1} 轮回放完成")
            
            # 轮次间隔
            if round_num < replay_count - 1:
                time.sleep(1)
        
        self.log_message("所有回放操作完成")
            
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("日志已清空")
        
    def on_closing(self):
        """关闭窗口时的处理"""
        self.root.quit()
        self.root.destroy()
        
    def run(self):
        """运行GUI"""
        self.log_message("macOS优化版鼠标点击器已启动")
        self.log_message("请设置坐标并选择点击操作")
        self.root.mainloop()

def main():
    parser = argparse.ArgumentParser(description='macOS优化版鼠标模拟点击工具')
    parser.add_argument('--gui', '-g', action='store_true', help='启动图形界面')
    parser.add_argument('--position', '-p', action='store_true', help='获取当前鼠标位置')
    parser.add_argument('--click', '-c', nargs=2, type=int, metavar=('X', 'Y'), help='单击指定坐标')
    parser.add_argument('--double-click', '-d', nargs=2, type=int, metavar=('X', 'Y'), help='双击指定坐标')
    parser.add_argument('--right-click', '-r', nargs=2, type=int, metavar=('X', 'Y'), help='右键点击指定坐标')
    parser.add_argument('--applescript', '-a', action='store_true', help='使用AppleScript方法（仅macOS）')
    parser.add_argument('--test', '-t', action='store_true', help='测试点击方法')
    parser.add_argument('--info', '-i', action='store_true', help='显示屏幕信息')
    
    args = parser.parse_args()
    
    # 如果指定了GUI模式，启动图形界面
    if args.gui:
        try:
            gui = MacOSMouseClickerGUI()
            gui.run()
        except Exception as e:
            print(f"启动GUI失败: {e}")
            print("请确保已安装tkinter支持")
        return
    
    clicker = MacOSMouseClicker()
    
    if args.info:
        screen_info = clicker.get_screen_info()
        if screen_info:
            print(f"\n=== 屏幕信息 ===")
            print(f"逻辑尺寸: {screen_info['logical_size']}")
            print(f"物理尺寸: {screen_info['physical_size']}")
            print(f"缩放比例: {screen_info['scale_x']:.2f}x{screen_info['scale_y']:.2f}")
            print(f"Retina显示屏: {'是' if screen_info['is_retina'] else '否'}")
    
    elif args.test:
        clicker.test_click_methods()
    
    elif args.position:
        x, y = clicker.get_mouse_position()
        print(f"当前鼠标位置: ({x}, {y})")
    
    elif args.click:
        x, y = args.click
        clicker.safe_click(x, y, use_applescript=args.applescript)
    
    elif args.double_click:
        x, y = args.double_click
        clicker.double_click(x, y, use_applescript=args.applescript)
    
    elif args.right_click:
        x, y = args.right_click
        clicker.right_click(x, y, use_applescript=args.applescript)
    
    else:
        # 交互模式
        print("\n=== macOS优化版鼠标点击工具 ===")
        print("1. 获取鼠标位置")
        print("2. 单击")
        print("3. 双击")
        print("4. 右键点击")
        print("5. 测试点击方法")
        print("6. 显示屏幕信息")
        print("0. 退出")
        
        while True:
            try:
                choice = input("\n请选择操作 (0-6): ").strip()
                
                if choice == '0':
                    print("退出程序")
                    break
                
                elif choice == '1':
                    x, y = clicker.get_mouse_position()
                    print(f"当前鼠标位置: ({x}, {y})")
                
                elif choice == '2':
                    x = int(input("请输入X坐标: "))
                    y = int(input("请输入Y坐标: "))
                    use_as = input("使用AppleScript? (y/n): ").lower() == 'y'
                    clicker.safe_click(x, y, use_applescript=use_as)
                
                elif choice == '3':
                    x = int(input("请输入X坐标: "))
                    y = int(input("请输入Y坐标: "))
                    use_as = input("使用AppleScript? (y/n): ").lower() == 'y'
                    clicker.double_click(x, y, use_applescript=use_as)
                
                elif choice == '4':
                    x = int(input("请输入X坐标: "))
                    y = int(input("请输入Y坐标: "))
                    use_as = input("使用AppleScript? (y/n): ").lower() == 'y'
                    clicker.right_click(x, y, use_applescript=use_as)
                
                elif choice == '5':
                    clicker.test_click_methods()
                
                elif choice == '6':
                    screen_info = clicker.get_screen_info()
                    if screen_info:
                        print(f"\n=== 屏幕信息 ===")
                        print(f"逻辑尺寸: {screen_info['logical_size']}")
                        print(f"物理尺寸: {screen_info['physical_size']}")
                        print(f"缩放比例: {screen_info['scale_x']:.2f}x{screen_info['scale_y']:.2f}")
                        print(f"Retina显示屏: {'是' if screen_info['is_retina'] else '否'}")
                
                else:
                    print("无效选择，请重新输入")
                    
            except KeyboardInterrupt:
                print("\n用户中断，退出程序")
                break
            except ValueError:
                print("输入格式错误，请输入数字")
            except Exception as e:
                print(f"操作失败: {e}")

if __name__ == '__main__':
    main()