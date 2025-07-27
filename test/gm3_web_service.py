#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# GM3 测试脚本 - 专门处理Web服务任务

import sys
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='GM3 Web Service Script')
    parser.add_argument('--port', type=int, default=8000, help='Server port')
    parser.add_argument('--host', type=str, default='localhost', help='Server host')
    parser.add_argument('--env', type=str, default='dev', help='Environment')
    parser.add_argument('--code-file', type=str, help='Path to code file')
    
    args, unknown = parser.parse_known_args()
    
    print(f"🌐 === GM3 Web Service Script ===")
    print(f"🔌 Port: {args.port}")
    print(f"🏠 Host: {args.host}")
    print(f"🏷️  Environment: {args.env}")
    print(f"❓ Unknown args: {unknown}")
    print(f"📋 All sys.argv: {sys.argv}")
    
    # Check if code is provided via stdin
    if not sys.stdin.isatty():
        print("\n📥 === Web Service Code from STDIN ===")
        code = sys.stdin.read()
        if code.strip():
            print("接收到Web服务代码:")
            print("─" * 40)
            print(code)
            print("─" * 40)
            print("🚀 启动Web服务...")
            try:
                # 创建Web服务环境
                service_globals = {
                    '__builtins__': __builtins__,
                    'PORT': args.port,
                    'HOST': args.host,
                    'ENV': args.env
                }
                exec(code, service_globals)
            except Exception as e:
                print(f"❌ Web服务启动错误: {e}")
    
    # Check if code file is provided
    if args.code_file and os.path.exists(args.code_file):
        print(f"\n📁 === Web Service Code from file: {args.code_file} ===")
        with open(args.code_file, 'r', encoding='utf-8') as f:
            code = f.read()
        print("Web服务代码内容:")
        print("─" * 40)
        print(code)
        print("─" * 40)
        print("🚀 启动Web服务...")
        try:
            service_globals = {
                '__builtins__': __builtins__,
                'PORT': args.port,
                'HOST': args.host,
                'ENV': args.env
            }
            exec(code, service_globals)
        except Exception as e:
            print(f"❌ Web服务启动错误: {e}")
    
    print("\n✅ GM3 Web服务处理完成!")

if __name__ == "__main__":
    main()
