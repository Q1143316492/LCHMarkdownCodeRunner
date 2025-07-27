# 配置测试文档

测试不同的GM标识符对应不同的Python脚本。

## settings.json 配置示例

```json
{
  "lchMarkdownCodeRunner.gmConfigs": {
      "GM": {
          "scriptPath": "test/test_script.py",
          "commandTemplate": "python {scriptPath} {args}",
          "passCodeAsStdin": true,
          "passCodeAsFile": false,
          "timeout": 15000
      },
      "GM2": {
          "scriptPath": "test/test_script_ex.py",
          "commandTemplate": "python {scriptPath} {args}",
          "passCodeAsStdin": false,
          "passCodeAsFile": true,
          "timeout": 20000
      }
  },
}
```



### 配置参数说明

- **commandTemplate**
  - 作用：定义执行命令的模板。
  - 示例：`python {scriptPath} {args}`
  - 说明：`{scriptPath}` 会被替换为实际脚本路径，`{args}` 会被替换为从GM指令解析出的参数。
  - 最终生成类似：`python test/test_script.py --port 8080 --debug true`

- **passCodeAsStdin**
  - 作用：是否通过标准输入（stdin）传递代码。
  - 当为 `true` 时：Markdown 中的 Python 代码通过管道传递给脚本，脚本用 `sys.stdin.read()` 接收并用 `exec()` 执行。
  - 优点：无需创建临时文件，简单高效。

- **passCodeAsFile**
  - 作用：是否将代码保存为临时文件传递。
  - 当为 `true` 时：代码会保存到临时文件，文件路径通过 `--code-file` 参数传递给脚本，脚本读取并执行。
  - 优点：适合需要文件路径的场景。

> **注意**：`passCodeAsStdin` 和 `passCodeAsFile` 只需启用其中一个，一般推荐用 `passCodeAsStdin`。

## GM - 基础测试脚本

```python
#GM[port=8080, debug=true]
import sys
print(f"Test #GM Args: {sys.argv}")
```

```python
#GM2[port=8080, debug=true]
import sys
print(f"Test #GM2 Args: {sys.argv}")
```

## GM - 直接执行模式测试

```python
#GM[direct]
import sys
print("aaa sys.argv:", sys.argv)
```

## 无GM指令的代码块

```python
print("This code block has no GM directive, won't show run button")
print("Because there's no corresponding GM identifier configured")
```

## 配置说明

当前配置支持以下GM标识符：

- **GM**: 使用 `test/test_script.py`，适用于基础测试
- **GM2**: 使用 `test/test_script_ex.py`，适用于扩展测试

每个GM配置都有独立的脚本路径、命令模板和超时设置。
