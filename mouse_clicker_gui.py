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
from typing import Tuple

class MouseClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("鼠标模拟点击工具")
        self.root.geometry("600x700")
        self.root.resizable(True, True)
        
        # 设置pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
        # 变量
        self.is_running = False
        self.current_position = tk.StringVar(value="(0, 0)")
        
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
        
        # 日志输出
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="5")
        log_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
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

def main():
    root = tk.Tk()
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