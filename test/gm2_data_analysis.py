#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# GM2 测试脚本 - 专门处理数据分析任务

import sys
import argparse
import os
import json

def main():
    parser = argparse.ArgumentParser(description='GM2 Data Analysis Script')
    parser.add_argument('--dataset', type=str, default='sample', help='Dataset name')
    parser.add_argument('--format', type=str, default='json', help='Output format')
    parser.add_argument('--verbose', type=str, default='false', help='Verbose mode')
    parser.add_argument('--code-file', type=str, help='Path to code file')
    
    args, unknown = parser.parse_known_args()
    
    print(f"🔬 === GM2 Data Analysis Script ===")
    print(f"📊 Dataset: {args.dataset}")
    print(f"📄 Format: {args.format}")
    print(f"🔍 Verbose: {args.verbose}")
    print(f"❓ Unknown args: {unknown}")
    print(f"📋 All sys.argv: {sys.argv}")
    
    # Check if code is provided via stdin
    if not sys.stdin.isatty():
        print("\n📥 === Code from STDIN ===")
        code = sys.stdin.read()
        if code.strip():
            print("接收到分析代码:")
            print("─" * 40)
            print(code)
            print("─" * 40)
            print("🚀 执行数据分析...")
            try:
                # 创建一个简单的分析环境
                analysis_globals = {
                    '__builtins__': __builtins__,
                    'dataset': args.dataset,
                    'output_format': args.format,
                    'verbose': args.verbose == 'true'
                }
                exec(code, analysis_globals)
            except Exception as e:
                print(f"❌ 分析执行错误: {e}")
    
    # Check if code file is provided
    if args.code_file and os.path.exists(args.code_file):
        print(f"\n📁 === Code from file: {args.code_file} ===")
        with open(args.code_file, 'r', encoding='utf-8') as f:
            code = f.read()
        print("分析代码内容:")
        print("─" * 40)
        print(code)
        print("─" * 40)
        print("🚀 执行数据分析...")
        try:
            analysis_globals = {
                '__builtins__': __builtins__,
                'dataset': args.dataset,
                'output_format': args.format,
                'verbose': args.verbose == 'true'
            }
            exec(code, analysis_globals)
        except Exception as e:
            print(f"❌ 分析执行错误: {e}")
    
    print("\n✅ GM2 数据分析完成!")

if __name__ == "__main__":
    main()
