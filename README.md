# LCH Markdown Code Runner

源码：https://github.com/Q1143316492/LCHMarkdownCodeRunner

LCH Markdown Code Runner 是一个用于在 VS Code 中直接运行 Markdown 文件中代码块的扩展。支持多种编程语言，适用于文档、教程和代码示例的快速验证。

## 功能与示例

```python
#GM[port=8080, debug=true]
eval(print("Hello, World!"))
```
插件支持配置了GM对应某个python脚本gm.py。markdown代码块上方会多一个运行按钮。点击运行会把参数port,debug,markdown文本内容传递给该脚本，并运行。这样就能够做很多事情。

初衷是我有一个游戏，他支持以http的形式接收一段GM指令。那我就能用这个插件打通文档到指令的一键执行。

## 安装
1. 在 VS Code 扩展市场搜索并安装 `LCH Markdown Code Runner`
2. 或下载 `.vsix` 文件手动安装

## 使用方法
1. 打开包含代码块的 Markdown 文件
2. 选中代码块或将光标放在代码块内
3. 右键选择“运行代码块”或使用命令面板执行相关命令

## 许可协议
MIT License

