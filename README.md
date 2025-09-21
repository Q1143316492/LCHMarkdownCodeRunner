
# LCH Markdown Code Runner

## Introduction

Source code: [LCHMarkdownCodeRunner](https://github.com/Q1143316492/LCHMarkdownCodeRunner)

LCH Markdown Code Runner is a VS Code extension that allows you to run code blocks directly from Markdown files.

For example, given the following content in a Markdown file:

```python
#GM[port=8080, debug=true]
eval('print("Hello, World!")')
```

this has been rendered as python code block. you need to wrap it with \`\`\`python \`\`\` in your file like this:

\`\`\`python
#GM[port=8080, debug=true]
eval('print("Hello, World!")')
\`\`\`


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

## Configuration

### GM Configurations

Configure different GM identifiers in your VS Code settings:

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

### Run Button Customization

You can customize the appearance of the run button:

#### Run Button Text
Set custom text for the run button:
```json
"lchMarkdownCodeRunner.runButtonText": "🚀 Execute Code"
```

#### Run Button Icon
Choose from various icons for the run button:
```json
"lchMarkdownCodeRunner.runButtonIcon": "🚀"
```

Available icons: `▶️`, `🚀`, `⚡`, `🔥`, `💫`, `🎯`, `⭐`, `🌟`, `✨`, `🎪`, `🎨`, `🎭`, `🎲`, `🎊`, `🎉`

**Note**: If you set a custom `runButtonText`, it will override the icon setting. If you only set the `runButtonIcon`, it will be combined with the default text "Run Code".

### Configuration Priority

- If `runButtonText` is customized: Uses the custom text exactly as specified
- If only `runButtonIcon` is set: Uses the selected icon + "Run Code"
- If neither is set: Uses the default "▶️ Run Code"

## Installation

1. Search for `LCH Markdown Code Runner` in the VS Code Extensions Marketplace and install it.
2. Or download the `.vsix` file and install manually.

## more Examples

For an advanced example of how to set up an HTTP gateway to send commands to a running application, see the [HTTP Gateway Example](./http_gateway/README.md).

## License

MIT License

