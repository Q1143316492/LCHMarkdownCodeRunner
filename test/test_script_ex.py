#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 支持接收代码内容的测试脚本

import sys
import argparse
import os

def main():
    print("\n🟦🟦🟦 BEGIN {} 🟦🟦🟦\n".format(os.path.basename(__file__)))
    print("🚩  Python Markdown Runner")
    print("🟢 Args:")
    print("   ", sys.argv)

    # Parse arguments to check for --code-file
    parser = argparse.ArgumentParser()
    parser.add_argument('--code-file', help='Path to the code file')
    parser.add_argument('--port', help='Port number')
    parser.add_argument('--debug', help='Debug mode')
    args, unknown = parser.parse_known_args()

    code = None
    
    # Check if code file is provided
    if args.code_file and os.path.exists(args.code_file):
        print(f"\n📁 Reading code from file: {args.code_file}")
        with open(args.code_file, 'r', encoding='utf-8') as f:
            code = f.read()
    # Otherwise check stdin
    elif not sys.stdin.isatty():
        code = sys.stdin.read()

    if code and code.strip():
        print("\n⭐ Markdown Code Content:")
        print(code)
        print("\n⭐ Exec:")
        exec(code)
    else:
        print("\n❌ No code to execute")
    
    print("\n🟦🟦🟦 END 🟦🟦🟦\n")

if __name__ == "__main__":
    main()
