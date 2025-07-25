#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置文件执行器
根据JSON配置文件批量执行鼠标操作
"""

import json
import pyautogui
import time
import argparse
import sys
from pathlib import Path

class ConfigExecutor:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()
        
        # 设置pyautogui
        pyautogui.FAILSAFE = self.config.get('settings', {}).get('fail_safe', True)
        pyautogui.PAUSE = 0.1
        
    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"错误：配置文件 {self.config_file} 不存在")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"错误：配置文件格式错误 - {e}")
            sys.exit(1)
            
    def execute_action(self, action):
        """执行单个动作"""
        action_type = action.get('type')
        delay_before = action.get('delay_before', 0)
        
        if delay_before > 0:
            print(f"等待 {delay_before} 秒...")
            time.sleep(delay_before)
            
        try:
            if action_type == 'click':
                x = action['x']
                y = action['y']
                button = action.get('button', 'left')
                print(f"点击坐标: ({x}, {y}), 按钮: {button}")
                pyautogui.click(x, y, button=button)
                
            elif action_type == 'double_click':
                x = action['x']
                y = action['y']
                print(f"双击坐标: ({x}, {y})")
                pyautogui.doubleClick(x, y)
                
            elif action_type == 'right_click':
                x = action['x']
                y = action['y']
                print(f"右键点击坐标: ({x}, {y})")
                pyautogui.rightClick(x, y)
                
            elif action_type == 'continuous_click':
                x = action['x']
                y = action['y']
                count = action['count']
                interval = action.get('interval', 1.0)
                print(f"连续点击 {count} 次，坐标: ({x}, {y}), 间隔: {interval}秒")
                
                for i in range(count):
                    pyautogui.click(x, y)
                    print(f"完成第 {i + 1} 次点击")
                    if i < count - 1:
                        time.sleep(interval)
                        
            elif action_type == 'drag':
                start_x = action['start_x']
                start_y = action['start_y']
                end_x = action['end_x']
                end_y = action['end_y']
                duration = action.get('duration', 1.0)
                print(f"拖拽: ({start_x}, {start_y}) -> ({end_x}, {end_y}), 持续时间: {duration}秒")
                
                pyautogui.moveTo(start_x, start_y)
                pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration)
                
            elif action_type == 'wait':
                wait_time = action['time']
                print(f"等待 {wait_time} 秒")
                time.sleep(wait_time)
                
            elif action_type == 'move':
                x = action['x']
                y = action['y']
                duration = action.get('duration', 0.5)
                print(f"移动鼠标到: ({x}, {y})")
                pyautogui.moveTo(x, y, duration=duration)
                
            else:
                print(f"警告：未知的动作类型 '{action_type}'")
                
        except KeyError as e:
            print(f"错误：动作配置缺少必要参数 {e}")
        except Exception as e:
            print(f"错误：执行动作失败 - {e}")
            
    def execute_sequence(self, sequence_name=None):
        """执行指定序列或所有序列"""
        sequences = self.config.get('click_sequences', [])
        
        if not sequences:
            print("配置文件中没有找到点击序列")
            return
            
        # 安全延迟
        safety_delay = self.config.get('settings', {}).get('safety_delay', 3.0)
        if safety_delay > 0:
            print(f"安全延迟 {safety_delay} 秒，请准备...")
            time.sleep(safety_delay)
            
        executed_count = 0
        
        for sequence in sequences:
            seq_name = sequence.get('name', '未命名序列')
            
            # 如果指定了序列名称，只执行匹配的序列
            if sequence_name and seq_name != sequence_name:
                continue
                
            print(f"\n=== 执行序列: {seq_name} ===")
            
            actions = sequence.get('actions', [])
            for i, action in enumerate(actions, 1):
                print(f"\n动作 {i}/{len(actions)}:")
                self.execute_action(action)
                
                # 动作间默认延迟
                default_delay = self.config.get('settings', {}).get('default_delay', 0.5)
                if i < len(actions) and default_delay > 0:
                    time.sleep(default_delay)
                    
            print(f"序列 '{seq_name}' 执行完成")
            executed_count += 1
            
        if executed_count == 0 and sequence_name:
            print(f"错误：未找到名为 '{sequence_name}' 的序列")
        else:
            print(f"\n总共执行了 {executed_count} 个序列")
            
    def list_sequences(self):
        """列出所有可用的序列"""
        sequences = self.config.get('click_sequences', [])
        
        if not sequences:
            print("配置文件中没有找到点击序列")
            return
            
        print("可用的点击序列:")
        for i, sequence in enumerate(sequences, 1):
            name = sequence.get('name', '未命名序列')
            actions_count = len(sequence.get('actions', []))
            print(f"{i}. {name} ({actions_count} 个动作)")
            
    def validate_config(self):
        """验证配置文件格式"""
        errors = []
        
        # 检查必要的顶级字段
        if 'click_sequences' not in self.config:
            errors.append("缺少 'click_sequences' 字段")
            return errors
            
        sequences = self.config['click_sequences']
        if not isinstance(sequences, list):
            errors.append("'click_sequences' 必须是数组")
            return errors
            
        # 检查每个序列
        for i, sequence in enumerate(sequences):
            if not isinstance(sequence, dict):
                errors.append(f"序列 {i+1} 必须是对象")
                continue
                
            if 'actions' not in sequence:
                errors.append(f"序列 {i+1} 缺少 'actions' 字段")
                continue
                
            actions = sequence['actions']
            if not isinstance(actions, list):
                errors.append(f"序列 {i+1} 的 'actions' 必须是数组")
                continue
                
            # 检查每个动作
            for j, action in enumerate(actions):
                if not isinstance(action, dict):
                    errors.append(f"序列 {i+1} 动作 {j+1} 必须是对象")
                    continue
                    
                if 'type' not in action:
                    errors.append(f"序列 {i+1} 动作 {j+1} 缺少 'type' 字段")
                    continue
                    
                action_type = action['type']
                
                # 检查不同类型动作的必要字段
                if action_type in ['click', 'double_click', 'right_click', 'move']:
                    if 'x' not in action or 'y' not in action:
                        errors.append(f"序列 {i+1} 动作 {j+1} 缺少坐标字段 'x' 或 'y'")
                        
                elif action_type == 'continuous_click':
                    required_fields = ['x', 'y', 'count']
                    for field in required_fields:
                        if field not in action:
                            errors.append(f"序列 {i+1} 动作 {j+1} 缺少字段 '{field}'")
                            
                elif action_type == 'drag':
                    required_fields = ['start_x', 'start_y', 'end_x', 'end_y']
                    for field in required_fields:
                        if field not in action:
                            errors.append(f"序列 {i+1} 动作 {j+1} 缺少字段 '{field}'")
                            
                elif action_type == 'wait':
                    if 'time' not in action:
                        errors.append(f"序列 {i+1} 动作 {j+1} 缺少字段 'time'")
                        
        return errors

def main():
    parser = argparse.ArgumentParser(description='配置文件执行器 - 批量执行鼠标操作')
    parser.add_argument('config_file', nargs='?', default='click_config.json', help='配置文件路径')
    parser.add_argument('--sequence', '-s', help='执行指定名称的序列')
    parser.add_argument('--list', '-l', action='store_true', help='列出所有可用序列')
    parser.add_argument('--validate', '-v', action='store_true', help='验证配置文件格式')
    
    args = parser.parse_args()
    
    # 检查配置文件是否存在
    if not Path(args.config_file).exists():
        print(f"错误：配置文件 {args.config_file} 不存在")
        print("\n可以使用示例配置文件 click_config.json 作为模板")
        sys.exit(1)
        
    executor = ConfigExecutor(args.config_file)
    
    if args.validate:
        print("验证配置文件...")
        errors = executor.validate_config()
        if errors:
            print("配置文件存在以下错误:")
            for error in errors:
                print(f"- {error}")
            sys.exit(1)
        else:
            print("配置文件格式正确")
            
    elif args.list:
        executor.list_sequences()
        
    else:
        try:
            print(f"加载配置文件: {args.config_file}")
            print(f"描述: {executor.config.get('description', '无描述')}")
            
            # 验证配置
            errors = executor.validate_config()
            if errors:
                print("配置文件存在错误，无法执行:")
                for error in errors:
                    print(f"- {error}")
                sys.exit(1)
                
            executor.execute_sequence(args.sequence)
            
        except KeyboardInterrupt:
            print("\n用户中断操作")
        except Exception as e:
            print(f"执行失败: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()