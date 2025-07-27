#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 支持接收代码内容的测试脚本

import sys
import argparse
import os

def main():
    parser = argparse.ArgumentParser(description='Test script for LCH Markdown Code Runner')
    parser.add_argument('--port', type=int, default=8080, help='Port number')
    parser.add_argument('--debug', type=str, default='false', help='Debug mode')
    parser.add_argument('--name', type=str, default='default', help='Name parameter')
    parser.add_argument('--code-file', type=str, help='Path to code file')
    
    args, unknown = parser.parse_known_args()
    
    print(f"=== Test Script Execution ===")
    print(f"Port: {args.port}")
    print(f"Debug: {args.debug}")
    print(f"Name: {args.name}")
    print(f"Unknown args: {unknown}")
    print(f"All sys.argv: {sys.argv}")
    
    # Check if code is provided via stdin
    if not sys.stdin.isatty():
        print("\n=== Code from STDIN ===")
        code = sys.stdin.read()
        if code.strip():
            print("Received code from stdin:")
            print("─" * 30)
            print(code)
            print("─" * 30)
            print("Executing code...")
            try:
                exec(code)
            except Exception as e:
                print(f"Error executing code: {e}")
    
    # Check if code file is provided
    if args.code_file and os.path.exists(args.code_file):
        print(f"\n=== Code from file: {args.code_file} ===")
        with open(args.code_file, 'r', encoding='utf-8') as f:
            code = f.read()
        print("Code content:")
        print("─" * 30)
        print(code)
        print("─" * 30)
        print("Executing code...")
        try:
            exec(code)
        except Exception as e:
            print(f"Error executing code: {e}")
    
    print("\n✅ Script completed successfully!")

if __name__ == "__main__":
    main()
