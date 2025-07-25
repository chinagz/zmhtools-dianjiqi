#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鼠标模拟点击工具 - GUI版本
提供图形界面的鼠标自动化操作工具
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pyautogui
import time
import threading
import platform
from typing import Tuple
try:
    from pynput import mouse, keyboard
    PYNPUT_AVAILABLE = True
    KEYBOARD_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    KEYBOARD_AVAILABLE = False
    print("警告: pynput未安装，将使用简化的录制功能")
    print("要使用完整的全局录制功能，请运行: pip install pynput")

class MouseClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("鼠标模拟点击工具")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # 设置pyautogui - 根据平台优化
        current_platform = platform.system()
        if current_platform == 'Windows':
            # Windows平台优化设置
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
            # 确保在Windows上正确处理DPI缩放
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except:
                pass  # 如果设置失败，继续使用默认设置
        elif current_platform == 'Darwin':  # macOS
            pyautogui.FAILSAFE = False  # macOS上可能导致问题
            pyautogui.PAUSE = 0.2
        else:  # Linux和其他平台
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
        
        # 变量
        self.is_running = False
        self.current_position = tk.StringVar(value="(0, 0)")
        
        # 录制和回放相关变量
        self.is_recording = False
        self.recorded_actions = []
        self.recording_start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None
        
        self.setup_ui()
        self.update_position()
        
    def setup_ui(self):
        """设置用户界面"""
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
        
        # 基本点击操作
        click_frame = ttk.LabelFrame(main_frame, text="基本点击操作", padding="5")
        click_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(click_frame, text="单击", command=self.single_click).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(click_frame, text="双击", command=self.double_click).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(click_frame, text="右键点击", command=self.right_click).grid(row=0, column=2, padx=(0, 5))
        
        # 连续点击设置
        continuous_frame = ttk.LabelFrame(main_frame, text="连续点击设置", padding="5")
        continuous_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
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
        drag_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
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
        delay_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(delay_frame, text="操作前延迟(秒):").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.delay_entry = ttk.Entry(delay_frame, width=10)
        self.delay_entry.insert(0, "3")
        self.delay_entry.grid(row=0, column=1, sticky=tk.W)
        
        # 录制回放功能
        record_frame = ttk.LabelFrame(main_frame, text="录制回放功能 (支持鼠标+键盘)", padding="5")
        record_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 录制控制按钮
        record_control_frame = ttk.Frame(record_frame)
        record_control_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.start_record_button = ttk.Button(record_control_frame, text="开始录制", command=self.start_recording)
        self.start_record_button.grid(row=0, column=0, padx=(0, 5))
        
        self.stop_record_button = ttk.Button(record_control_frame, text="停止录制", command=self.stop_recording, state="disabled")
        self.stop_record_button.grid(row=0, column=1, padx=(0, 5))
        
        # 回放控制
        replay_frame = ttk.Frame(record_frame)
        replay_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Label(replay_frame, text="回放次数:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.replay_count_entry = ttk.Entry(replay_frame, width=8)
        self.replay_count_entry.insert(0, "1")
        self.replay_count_entry.grid(row=0, column=1, padx=(0, 10))
        
        self.replay_button = ttk.Button(replay_frame, text="回放操作", command=self.replay_actions)
        self.replay_button.grid(row=0, column=2, padx=(0, 5))
        
        ttk.Button(replay_frame, text="清空录制", command=self.clear_recording).grid(row=0, column=3, padx=(5, 0))
        
        # 日志输出
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="5")
        log_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=70)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Button(log_frame, text="清空日志", command=self.clear_log).grid(row=1, column=0, pady=(5, 0))
        
    def log_message(self, message):
        """添加日志消息"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        
    def update_position(self):
        """更新鼠标位置显示"""
        try:
            x, y = pyautogui.position()
            self.current_position.set(f"({x}, {y})")
        except:
            pass
        self.root.after(100, self.update_position)
        
    def get_current_position(self):
        """获取当前鼠标位置并填入坐标框"""
        x, y = pyautogui.position()
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, str(x))
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, str(y))
        self.log_message(f"获取当前鼠标位置: ({x}, {y})")
        
    def get_coordinates(self) -> Tuple[int, int]:
        """获取输入的坐标"""
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            return x, y
        except ValueError:
            raise ValueError("请输入有效的坐标数字")
            
    def apply_delay(self):
        """应用延迟"""
        try:
            delay = float(self.delay_entry.get())
            if delay > 0:
                self.log_message(f"等待 {delay} 秒...")
                time.sleep(delay)
        except ValueError:
            pass
            
    def single_click(self):
        """单击"""
        try:
            x, y = self.get_coordinates()
            self.apply_delay()
            pyautogui.click(x, y)
            self.log_message(f"单击坐标: ({x}, {y})")
        except Exception as e:
            messagebox.showerror("错误", str(e))
            
    def double_click(self):
        """双击"""
        try:
            x, y = self.get_coordinates()
            self.apply_delay()
            pyautogui.doubleClick(x, y)
            self.log_message(f"双击坐标: ({x}, {y})")
        except Exception as e:
            messagebox.showerror("错误", str(e))
            
    def right_click(self):
        """右键点击"""
        try:
            x, y = self.get_coordinates()
            self.apply_delay()
            pyautogui.rightClick(x, y)
            self.log_message(f"右键点击坐标: ({x}, {y})")
        except Exception as e:
            messagebox.showerror("错误", str(e))
            
    def start_continuous_click(self):
        """开始连续点击"""
        try:
            x, y = self.get_coordinates()
            count = int(self.count_entry.get())
            interval = float(self.interval_entry.get())
            
            if count <= 0:
                raise ValueError("点击次数必须大于0")
            if interval < 0:
                raise ValueError("间隔时间不能为负数")
                
            self.is_running = True
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            
            # 在新线程中执行连续点击
            thread = threading.Thread(target=self._continuous_click_worker, args=(x, y, count, interval))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", str(e))
            
    def _continuous_click_worker(self, x, y, count, interval):
        """连续点击工作线程"""
        try:
            self.apply_delay()
            self.log_message(f"开始连续点击: ({x}, {y}), 次数: {count}, 间隔: {interval}秒")
            
            for i in range(count):
                if not self.is_running:
                    break
                    
                pyautogui.click(x, y)
                self.log_message(f"完成第 {i + 1} 次点击")
                
                if i < count - 1 and self.is_running:
                    time.sleep(interval)
                    
            if self.is_running:
                self.log_message("连续点击完成")
            else:
                self.log_message("连续点击已停止")
                
        except Exception as e:
            self.log_message(f"连续点击出错: {e}")
        finally:
            self.is_running = False
            self.root.after(0, self._reset_buttons)
            
    def _reset_buttons(self):
        """重置按钮状态"""
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
    def stop_continuous_click(self):
        """停止连续点击"""
        self.is_running = False
        self.log_message("正在停止连续点击...")
        
    def perform_drag(self):
        """执行拖拽操作"""
        try:
            start_x = int(self.drag_start_x.get())
            start_y = int(self.drag_start_y.get())
            end_x = int(self.drag_end_x.get())
            end_y = int(self.drag_end_y.get())
            
            self.apply_delay()
            
            # 移动到起始位置
            pyautogui.moveTo(start_x, start_y)
            # 执行拖拽
            pyautogui.drag(end_x - start_x, end_y - start_y, duration=1.0)
            
            self.log_message(f"拖拽操作: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
            
        except Exception as e:
            messagebox.showerror("错误", str(e))
    
    def start_recording(self):
        """开始录制鼠标操作"""
        if not PYNPUT_AVAILABLE:
            messagebox.showwarning("警告", "pynput库未安装，无法使用录制功能。\n请运行: pip install pynput")
            return
            
        if self.is_recording:
            return
            
        self.is_recording = True
        self.recorded_actions = []
        self.recording_start_time = time.time()
        
        # 更新按钮状态
        self.start_record_button.config(state="disabled")
        self.stop_record_button.config(state="normal")
        
        # 启动鼠标监听器
        try:
            self.mouse_listener = mouse.Listener(
                on_click=self.record_mouse_click,
                on_scroll=self.record_mouse_scroll
            )
            self.mouse_listener.start()
            
            # 启动键盘监听器
            if KEYBOARD_AVAILABLE:
                try:
                    self.keyboard_listener = keyboard.Listener(
                        on_press=self.record_key_press,
                        on_release=self.record_key_release
                    )
                    self.keyboard_listener.start()
                    self.log_message("开始录制鼠标和键盘操作...")
                except Exception as kb_e:
                    self.log_message(f"键盘监听器启动失败: {kb_e}")
                    self.log_message("仅录制鼠标操作")
                    self.keyboard_listener = None
            else:
                self.log_message("开始录制鼠标操作...")
                
            self.log_message("提示: 录制期间请避免点击应用程序窗口")
            
        except Exception as e:
            self.log_message(f"启动录制失败: {e}")
            self.stop_recording()
    
    def stop_recording(self):
        """停止录制"""
        if not self.is_recording:
            return
            
        self.is_recording = False
        
        # 停止监听器
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
            
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
        
        # 更新按钮状态
        self.start_record_button.config(state="normal")
        self.stop_record_button.config(state="disabled")
        
        self.log_message(f"录制停止，共录制 {len(self.recorded_actions)} 个操作")
    
    def record_mouse_click(self, x, y, button, pressed):
        """记录鼠标点击事件"""
        if not self.is_recording:
            return
            
        if pressed:  # 只记录按下事件
            current_time = time.time()
            delay = current_time - self.recording_start_time if self.recorded_actions else 0
            
            action = {
                'type': 'click',
                'x': x,
                'y': y,
                'button': str(button),
                'delay': delay
            }
            
            self.recorded_actions.append(action)
            self.recording_start_time = current_time
            
            button_name = str(button).split('.')[-1] if '.' in str(button) else str(button)
            self.log_message(f"录制: {button_name}点击 ({x}, {y})")
    
    def record_mouse_scroll(self, x, y, dx, dy):
        """记录鼠标滚轮事件"""
        if not self.is_recording:
            return
            
        current_time = time.time()
        delay = current_time - self.recording_start_time if self.recorded_actions else 0
        
        action = {
            'type': 'scroll',
            'x': x,
            'y': y,
            'dx': dx,
            'dy': dy,
            'delay': delay
        }
        
        self.recorded_actions.append(action)
        self.recording_start_time = current_time
        
        direction = "上" if dy > 0 else "下" if dy < 0 else "左" if dx < 0 else "右"
        self.log_message(f"录制: 滚轮{direction} ({x}, {y})")
    
    def record_key_press(self, key):
        """记录键盘按下事件"""
        if not self.is_recording:
            return
            
        current_time = time.time()
        delay = current_time - self.recording_start_time if self.recorded_actions else 0
        
        # 获取按键名称
        try:
            if hasattr(key, 'char') and key.char is not None:
                key_name = key.char
            else:
                key_name = str(key).replace('Key.', '')
        except:
            key_name = str(key)
        
        action = {
            'type': 'key_press',
            'key': key_name,
            'delay': delay
        }
        
        self.recorded_actions.append(action)
        self.recording_start_time = current_time
        
        self.log_message(f"录制: 按键按下 [{key_name}]")
    
    def record_key_release(self, key):
        """记录键盘释放事件"""
        if not self.is_recording:
            return
            
        current_time = time.time()
        delay = current_time - self.recording_start_time if self.recorded_actions else 0
        
        # 获取按键名称
        try:
            if hasattr(key, 'char') and key.char is not None:
                key_name = key.char
            else:
                key_name = str(key).replace('Key.', '')
        except:
            key_name = str(key)
        
        action = {
            'type': 'key_release',
            'key': key_name,
            'delay': delay
        }
        
        self.recorded_actions.append(action)
        self.recording_start_time = current_time
        
        self.log_message(f"录制: 按键释放 [{key_name}]")
    
    def replay_actions(self):
        """回放录制的操作"""
        if not self.recorded_actions:
            messagebox.showwarning("警告", "没有录制的操作可以回放")
            return
            
        try:
            replay_count = int(self.replay_count_entry.get())
            if replay_count <= 0:
                raise ValueError("回放次数必须大于0")
        except ValueError as e:
            messagebox.showerror("错误", f"无效的回放次数: {e}")
            return
        
        # 在新线程中执行回放
        thread = threading.Thread(target=self._replay_worker, args=(replay_count,))
        thread.daemon = True
        thread.start()
    
    def _replay_worker(self, replay_count):
        """回放工作线程"""
        try:
            self.log_message(f"开始回放 {len(self.recorded_actions)} 个操作，重复 {replay_count} 次")
            
            for round_num in range(replay_count):
                if replay_count > 1:
                    self.log_message(f"第 {round_num + 1} 轮回放开始")
                
                for i, action in enumerate(self.recorded_actions):
                    # 等待延迟
                    if action['delay'] > 0:
                        time.sleep(min(action['delay'], 5.0))  # 限制最大延迟为5秒
                    
                    try:
                        if action['type'] == 'click':
                            # 执行点击
                            button_map = {
                                'Button.left': 'left',
                                'Button.right': 'right',
                                'Button.middle': 'middle',
                                'left': 'left',
                                'right': 'right',
                                'middle': 'middle'
                            }
                            
                            button = button_map.get(action['button'], 'left')
                            
                            if button == 'left':
                                pyautogui.click(action['x'], action['y'])
                            elif button == 'right':
                                pyautogui.rightClick(action['x'], action['y'])
                            elif button == 'middle':
                                pyautogui.middleClick(action['x'], action['y'])
                            
                            self.log_message(f"回放: {button}点击 ({action['x']}, {action['y']})")
                            
                        elif action['type'] == 'scroll':
                            # 执行滚轮操作
                            pyautogui.scroll(int(action['dy']), x=action['x'], y=action['y'])
                            direction = "上" if action['dy'] > 0 else "下"
                            self.log_message(f"回放: 滚轮{direction} ({action['x']}, {action['y']})")
                            
                        elif action['type'] == 'key_press':
                            # 执行按键按下
                            key_name = action['key']
                            try:
                                # 按键名称映射
                                key_mapping = {
                                    'space': 'space',
                                    'enter': 'enter',
                                    'tab': 'tab',
                                    'shift': 'shift',
                                    'shift_l': 'shiftleft',
                                    'shift_r': 'shiftright',
                                    'ctrl': 'ctrl',
                                    'ctrl_l': 'ctrlleft',
                                    'ctrl_r': 'ctrlright',
                                    'alt': 'alt',
                                    'alt_l': 'altleft',
                                    'alt_r': 'altright',
                                    'cmd': 'cmd',
                                    'win': 'win',
                                    'esc': 'esc',
                                    'escape': 'esc',
                                    'backspace': 'backspace',
                                    'delete': 'delete',
                                    'up': 'up',
                                    'down': 'down',
                                    'left': 'left',
                                    'right': 'right'
                                }
                                
                                mapped_key = key_mapping.get(key_name.lower(), key_name)
                                pyautogui.keyDown(mapped_key)
                                self.log_message(f"回放: 按键按下 [{key_name}]")
                            except Exception as key_e:
                                self.log_message(f"回放按键失败 [{key_name}]: {key_e}")
                                
                        elif action['type'] == 'key_release':
                            # 执行按键释放
                            key_name = action['key']
                            try:
                                # 按键名称映射
                                key_mapping = {
                                    'space': 'space',
                                    'enter': 'enter',
                                    'tab': 'tab',
                                    'shift': 'shift',
                                    'shift_l': 'shiftleft',
                                    'shift_r': 'shiftright',
                                    'ctrl': 'ctrl',
                                    'ctrl_l': 'ctrlleft',
                                    'ctrl_r': 'ctrlright',
                                    'alt': 'alt',
                                    'alt_l': 'altleft',
                                    'alt_r': 'altright',
                                    'cmd': 'cmd',
                                    'win': 'win',
                                    'esc': 'esc',
                                    'escape': 'esc',
                                    'backspace': 'backspace',
                                    'delete': 'delete',
                                    'up': 'up',
                                    'down': 'down',
                                    'left': 'left',
                                    'right': 'right'
                                }
                                
                                mapped_key = key_mapping.get(key_name.lower(), key_name)
                                pyautogui.keyUp(mapped_key)
                                self.log_message(f"回放: 按键释放 [{key_name}]")
                            except Exception as key_e:
                                self.log_message(f"回放按键失败 [{key_name}]: {key_e}")
                            
                    except Exception as e:
                        self.log_message(f"回放操作 {i+1} 失败: {e}")
                        continue
                
                if replay_count > 1 and round_num < replay_count - 1:
                    self.log_message(f"第 {round_num + 1} 轮回放完成，等待1秒后开始下一轮")
                    time.sleep(1)
            
            self.log_message("回放完成")
            
        except Exception as e:
            self.log_message(f"回放过程出错: {e}")
    
    def clear_recording(self):
        """清空录制的操作"""
        if self.is_recording:
            self.stop_recording()
        
        self.recorded_actions = []
        self.log_message("已清空录制的操作")

def main():
    root = tk.Tk()
    
    # Windows平台特定设置
    if platform.system() == 'Windows':
        try:
            # 设置Windows任务栏图标
            import ctypes
            myappid = 'xiaobao.tools.clicker.1.0.0'  # 应用程序ID
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            
            # 确保窗口在前台显示
            root.lift()
            root.attributes('-topmost', True)
            root.after_idle(lambda: root.attributes('-topmost', False))
        except:
            pass  # 如果设置失败，继续正常启动
    
    app = MouseClickerGUI(root)
    
    # 设置窗口图标（如果有的话）
    try:
        # root.iconbitmap('icon.ico')  # 如果有图标文件
        pass
    except:
        pass
        
    root.mainloop()

if __name__ == '__main__':
    main()