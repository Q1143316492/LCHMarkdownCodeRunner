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

    if not sys.stdin.isatty():
        code = sys.stdin.read()
        if code.strip():
            print("\n⭐ Markdown Code Content:")
            print(code)
            print("\n⭐ Exec:")
            exec(code)
    print("\n🟦🟦🟦 END 🟦🟦🟦\n")

if __name__ == "__main__":
    main()
