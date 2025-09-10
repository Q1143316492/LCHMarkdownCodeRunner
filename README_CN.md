# LCH Markdown 代码运行器

## 简介

源代码: [LCHMarkdownCodeRunner](https://github.com/Q1143316492/LCHMarkdownCodeRunner)

LCH Markdown Code Runner 是一个 VS Code 扩展，允许您直接从 Markdown 文件运行代码块。

例如，在 Markdown 文件中有以下内容：

```python
#GM[port=8080, debug=true]
eval('print("Hello, World!")')
```

以及 `settings.json` 中的以下内容：

```json
"lchMarkdownCodeRunner.gmConfigs": {
    "GM": {
        "scriptPath": "test/test_script.py",
        "commandTemplate": "python {scriptPath} {args}",
        "passCodeAsStdin": true,
        "passCodeAsFile": false,
        "timeout": 15000
    }
}
```

这将调用 `test/test_script.py` 脚本，传递 `--port=8080 --debug=true` 作为参数，并通过 stdin 传递代码块内容。

匹配规则是 `#GM[...]`，其中 `GM` 是配置名称，`[...]` 被解析为参数。它支持 `[port=8080, debug=true]` 和 `[8080, true]` 两种格式。

匹配的代码块上方会显示一个“Run”按钮。点击它会执行代码块，使您的文档具有高度的交互性。

示例 `test/test_script.py`:

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# test_script.py

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
```

示例输出:

```
==================================================
Running Python code from e:\LCHMarkdownCodeRunner\README.md
{
  "scriptPath": "test/test_script.py",
  "commandTemplate": "python {scriptPath} {args}",
  "passCodeAsStdin": true,
  "passCodeAsFile": false,
  "timeout": 15000
}
GM Identifier: GM
Script Path: test/test_script.py
Command Template: python {scriptPath} {args}
Pass Code As Stdin: true
Pass Code As File: false
Timeout: 15000
GM Directive args: []
GM Directive params: {"port":"8080","debug":"true"}
==================================================
Code to execute:
──────────────────────────────
eval('print("Hello, World!")')
──────────────────────────────
Executing: python test/test_script.py --port=8080 --debug=true

🟦🟦🟦 BEGIN test_script.py 🟦🟦🟦

🚩  Python Markdown Runner
🟢 Args:
    ['test/test_script.py', '--port=8080', '--debug=true']

⭐ Markdown Code Content:
eval('print("Hello, World!")')

⭐ Exec:
Hello, World!

🟦🟦🟦 END 🟦🟦🟦

──────────────────────────────────────────────────
Process exited with code: 0
✅ Execution completed successfully
```

## 配置

### GM 配置

在您的 VS Code 设置中配置不同的 GM 标识符：

```json
"lchMarkdownCodeRunner.gmConfigs": {
    "GM": {
        "scriptPath": "test/test_script.py",
        "commandTemplate": "python {scriptPath} {args}",
        "passCodeAsStdin": true,
        "passCodeAsFile": false,
        "timeout": 15000
    },
    "GM2": {
        "scriptPath": "another_script.py",
        "commandTemplate": "python {scriptPath} {args}",
        "passCodeAsStdin": false,
        "passCodeAsFile": true,
        "timeout": 30000
    },
    "GM3": {
        "scriptPath": "http_gateway/python_gateway/lch_gateway_cli.py",
        "commandTemplate": "python {scriptPath} {args}",
        "passCodeAsStdin": true,
        "passCodeAsFile": false,
        "timeout": 3000
    }
}
```

### 运行按钮自定义

您可以自定义运行按钮的外观：

#### 运行按钮文本
为运行按钮设置自定义文本：
```json
"lchMarkdownCodeRunner.runButtonText": "🚀 执行代码"
```

#### 运行按钮图标
为运行按钮选择各种图标：
```json
"lchMarkdownCodeRunner.runButtonIcon": "🚀"
```

可用图标: `▶️`, `🚀`, `⚡`, `🔥`, `💫`, `🎯`, `⭐`, `🌟`, `✨`, `🎪`, `🎨`, `🎭`, `🎲`, `🎊`, `🎉`

**注意**: 如果您设置了自定义的 `runButtonText`，它将覆盖图标设置。如果您只设置了 `runButtonIcon`，它将与默认文本 "Run Code" 结合使用。

### 配置优先级

- 如果 `runButtonText` 已自定义：完全按照指定使用自定义文本
- 如果只设置了 `runButtonIcon`：使用所选图标 + "Run Code"
- 如果两者都未设置：使用默认的 "▶️ Run Code"

## 安装

1. 在 VS Code 扩展市场中搜索 `LCH Markdown Code Runner` 并安装。
2. 或者下载 `.vsix` 文件并手动安装。

## 更多示例

有关如何设置HTTP网关以向正在运行的应用程序发送命令的高级示例，请参阅[HTTP网关示例](./http_gateway/README.md)。

## 许可证

MIT 许可证
