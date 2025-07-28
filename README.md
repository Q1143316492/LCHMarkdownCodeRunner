
# LCH Markdown Code Runner

## Introduction

Source code: [https://github.com/Q1143316492/LCHMarkdownCodeRunner](https://github.com/Q1143316492/LCHMarkdownCodeRunner)

LCH Markdown Code Runner is a VS Code extension that allows you to run code blocks directly from Markdown files.

For example, given the following content in a Markdown file:

```python
#GM[port=8080, debug=true]
eval('print("Hello, World!")')
```

And the following in your `settings.json`:

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

This will call the `test/test_script.py` script, passing `--port=8080 --debug=true` as arguments, and the code block content via stdin.

The matching rule is `#GM[...]`, where `GM` is the config name and `[...]` is parsed as arguments. It supports both `[port=8080, debug=true]` and `[8080, true]` formats.

Matching code blocks will display a "Run" button above them. Clicking it executes the code block, making your documentation highly interactive.

Example `test/test_script.py`:

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

Sample output:

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

## Installation

1. Search for `LCH Markdown Code Runner` in the VS Code Extensions Marketplace and install it.
2. Or download the `.vsix` file and install manually.

## License

MIT License

