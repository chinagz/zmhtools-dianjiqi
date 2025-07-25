#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鼠标模拟点击工具
功能：
1. 单击指定坐标
2. 双击指定坐标
3. 右键点击指定坐标
4. 连续点击（可设置间隔时间）
5. 获取当前鼠标位置
6. 拖拽操作
"""

import pyautogui
import time
import sys
import argparse
from typing import Tuple, Optional

class MouseClicker:
    def __init__(self):
        # 设置pyautogui的安全设置
        pyautogui.FAILSAFE = True  # 鼠标移动到屏幕左上角时停止
        pyautogui.PAUSE = 0.1  # 每次操作后暂停0.1秒
        
    def get_screen_size(self) -> Tuple[int, int]:
        """获取屏幕尺寸"""
        return pyautogui.size()
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """获取当前鼠标位置"""
        return pyautogui.position()
    
    def click(self, x: int, y: int, button: str = 'left', clicks: int = 1, interval: float = 0.0) -> bool:
        """
        点击指定坐标
        
        Args:
            x: X坐标
            y: Y坐标
            button: 鼠标按钮 ('left', 'right', 'middle')
            clicks: 点击次数
            interval: 点击间隔时间（秒）
        
        Returns:
            bool: 操作是否成功
        """
        try:
            screen_width, screen_height = self.get_screen_size()
            
            # 检查坐标是否在屏幕范围内
            if not (0 <= x <= screen_width and 0 <= y <= screen_height):
                print(f"错误：坐标 ({x}, {y}) 超出屏幕范围 ({screen_width}x{screen_height})")
                return False
            
            print(f"点击坐标: ({x}, {y}), 按钮: {button}, 次数: {clicks}")
            
            if clicks == 1:
                pyautogui.click(x, y, button=button)
            else:
                pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
            
            return True
            
        except Exception as e:
            print(f"点击操作失败: {e}")
            return False
    
    def double_click(self, x: int, y: int) -> bool:
        """双击指定坐标"""
        return self.click(x, y, clicks=2, interval=0.1)
    
    def right_click(self, x: int, y: int) -> bool:
        """右键点击指定坐标"""
        return self.click(x, y, button='right')
    
    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, duration: float = 1.0) -> bool:
        """
        拖拽操作
        
        Args:
            start_x: 起始X坐标
            start_y: 起始Y坐标
            end_x: 结束X坐标
            end_y: 结束Y坐标
            duration: 拖拽持续时间（秒）
        
        Returns:
            bool: 操作是否成功
        """
        try:
            print(f"拖拽: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
            pyautogui.drag(end_x - start_x, end_y - start_y, duration, button='left')
            return True
        except Exception as e:
            print(f"拖拽操作失败: {e}")
            return False
    
    def continuous_click(self, x: int, y: int, count: int, interval: float = 1.0, button: str = 'left') -> bool:
        """
        连续点击
        
        Args:
            x: X坐标
            y: Y坐标
            count: 点击次数
            interval: 点击间隔时间（秒）
            button: 鼠标按钮
        
        Returns:
            bool: 操作是否成功
        """
        try:
            print(f"连续点击 {count} 次，间隔 {interval} 秒")
            for i in range(count):
                if not self.click(x, y, button=button):
                    return False
                if i < count - 1:  # 最后一次点击后不需要等待
                    time.sleep(interval)
                print(f"完成第 {i + 1} 次点击")
            return True
        except KeyboardInterrupt:
            print("\n用户中断操作")
            return False
        except Exception as e:
            print(f"连续点击操作失败: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='鼠标模拟点击工具')
    parser.add_argument('--position', '-p', action='store_true', help='获取当前鼠标位置')
    parser.add_argument('--click', '-c', nargs=2, type=int, metavar=('X', 'Y'), help='单击指定坐标')
    parser.add_argument('--double-click', '-d', nargs=2, type=int, metavar=('X', 'Y'), help='双击指定坐标')
    parser.add_argument('--right-click', '-r', nargs=2, type=int, metavar=('X', 'Y'), help='右键点击指定坐标')
    parser.add_argument('--continuous', '-cont', nargs=4, type=float, metavar=('X', 'Y', 'COUNT', 'INTERVAL'), help='连续点击：X Y 次数 间隔时间')
    parser.add_argument('--drag', nargs=4, type=int, metavar=('START_X', 'START_Y', 'END_X', 'END_Y'), help='拖拽操作')
    parser.add_argument('--delay', type=float, default=0, help='操作前延迟时间（秒）')
    
    args = parser.parse_args()
    
    clicker = MouseClicker()
    
    # 显示屏幕信息
    screen_width, screen_height = clicker.get_screen_size()
    print(f"屏幕尺寸: {screen_width}x{screen_height}")
    
    # 操作前延迟
    if args.delay > 0:
        print(f"等待 {args.delay} 秒...")
        time.sleep(args.delay)
    
    # 执行相应操作
    if args.position:
        x, y = clicker.get_mouse_position()
        print(f"当前鼠标位置: ({x}, {y})")
    
    elif args.click:
        x, y = args.click
        clicker.click(x, y)
    
    elif args.double_click:
        x, y = args.double_click
        clicker.double_click(x, y)
    
    elif args.right_click:
        x, y = args.right_click
        clicker.right_click(x, y)
    
    elif args.continuous:
        x, y, count, interval = args.continuous
        clicker.continuous_click(int(x), int(y), int(count), interval)
    
    elif args.drag:
        start_x, start_y, end_x, end_y = args.drag
        clicker.drag(start_x, start_y, end_x, end_y)
    
    else:
        # 交互模式
        print("\n=== 鼠标模拟点击工具 ===")
        print("1. 单击")
        print("2. 双击")
        print("3. 右键点击")
        print("4. 连续点击")
        print("5. 拖拽")
        print("6. 获取鼠标位置")
        print("0. 退出")
        
        while True:
            try:
                choice = input("\n请选择操作 (0-6): ").strip()
                
                if choice == '0':
                    print("退出程序")
                    break
                
                elif choice == '1':
                    x = int(input("请输入X坐标: "))
                    y = int(input("请输入Y坐标: "))
                    clicker.click(x, y)
                
                elif choice == '2':
                    x = int(input("请输入X坐标: "))
                    y = int(input("请输入Y坐标: "))
                    clicker.double_click(x, y)
                
                elif choice == '3':
                    x = int(input("请输入X坐标: "))
                    y = int(input("请输入Y坐标: "))
                    clicker.right_click(x, y)
                
                elif choice == '4':
                    x = int(input("请输入X坐标: "))
                    y = int(input("请输入Y坐标: "))
                    count = int(input("请输入点击次数: "))
                    interval = float(input("请输入间隔时间(秒): "))
                    clicker.continuous_click(x, y, count, interval)
                
                elif choice == '5':
                    start_x = int(input("请输入起始X坐标: "))
                    start_y = int(input("请输入起始Y坐标: "))
                    end_x = int(input("请输入结束X坐标: "))
                    end_y = int(input("请输入结束Y坐标: "))
                    clicker.drag(start_x, start_y, end_x, end_y)
                
                elif choice == '6':
                    x, y = clicker.get_mouse_position()
                    print(f"当前鼠标位置: ({x}, {y})")
                
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