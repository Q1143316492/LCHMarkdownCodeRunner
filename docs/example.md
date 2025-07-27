# 配置测试文档

测试不同的GM标识符对应不同的Python脚本。

## settings.json 配置示例

```json
{
  "lchMarkdownCodeRunner.gmConfigs": {
      "GM": {
          "scriptPath": "test/test_script.py",
          "commandTemplate": "python {scriptPath} {args}",
          "directMode": false,
          "passCodeAsStdin": true,
          "passCodeAsFile": false,
          "timeout": 15000
      },
      "GM2": {
          "scriptPath": "test/gm2_data_analysis.py",
          "commandTemplate": "python {scriptPath} {args}",
          "directMode": false,
          "passCodeAsStdin": true,
          "passCodeAsFile": false,
          "timeout": 20000
      },
      "GM3": {
          "scriptPath": "test/gm3_web_service.py", 
          "commandTemplate": "python {scriptPath} {args}",
          "directMode": false,
          "passCodeAsStdin": true,
          "passCodeAsFile": false,
          "timeout": 25000
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

- **directMode**
  - 作用：是否直接执行代码（跳过脚本）。
  - 当为 `true` 时：直接执行 Python 代码，不调用 `scriptPath` 脚本。
  - 当为 `false` 时：通过配置的脚本来处理代码。

> **注意**：`passCodeAsStdin` 和 `passCodeAsFile` 只需启用其中一个，一般推荐用 `passCodeAsStdin`。

## GM - 基础测试脚本

```python
#GM[port=8080, debug=true]
print("GM basic test")
print(f"Port: 8080")
print(f"Debug mode: True")
import sys
print(f"Args: {sys.argv}")
```

## GM2 - 数据分析脚本

```python
#GM2[dataset=sales, format=json, verbose=true]
print("Starting data analysis")
print(f"Dataset: {dataset}")
print(f"Output format: {output_format}")
print(f"Verbose mode: {verbose}")

# Simulate data analysis
data = [1, 2, 3, 4, 5]
result = sum(data) / len(data)
print(f"Average: {result}")
```

## GM3 - Web服务脚本

```python
#GM3[port=9000, host=0.0.0.0, env=production]
print("Web service configuration")
import sys
print(f"args: {sys.argv}")
# Simulate simple HTTP server setup
print("Setting up routes...")
print("Configuring middleware...")
print("Web service ready!")
```

## GM - 直接执行模式测试

```python
#GM[direct]
print("GM direct execution mode")
import datetime
print(f"Current time: {datetime.datetime.now()}")
for i in range(3):
    print(f"Count: {i + 1}")
```

## 无GM指令的代码块

```python
print("This code block has no GM directive, won't show run button")
print("Because there's no corresponding GM identifier configured")
```

## 配置说明

当前配置支持以下GM标识符：

- **GM**: 使用 `test/test_script.py`，适用于基础测试
- **GM2**: 使用 `test/gm2_data_analysis.py`，适用于数据分析
- **GM3**: 使用 `test/gm3_web_service.py`，适用于Web服务

每个GM配置都有独立的脚本路径、命令模板和超时设置。
