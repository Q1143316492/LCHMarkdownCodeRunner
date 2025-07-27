# LCH Markdown Code Runner

**专业的 Markdown 代码执行器，将文档中的 Python 代码块转化为强大的自动化工具**

LCH Markdown Code Runner 是一个 VS Code 扩展，允许你在 Markdown 文档中通过简单的 `#GM` 注解，将 Python 代码块与自定义脚本关联，实现远程服务调用、自动化测试、数据处理等企业级应用场景。

## 核心功能

### 🎯 智能代码路由
- 通过 `#GM`、`#GM2`、`#GM3` 等标识符，将代码块路由到不同的处理脚本
- 支持参数传递，实现动态配置和环境切换
- 灵活的命令模板系统，适配各种执行环境

### 🚀 企业级应用场景
- **自动化测试**: 将测试代码发送到远程测试服务器执行
- **API 调用**: 快速测试和验证 REST API 接口
- **数据分析**: 连接数据库或数据服务进行实时分析
- **DevOps 集成**: 与 CI/CD 流水线和监控系统集成
- **微服务测试**: 跨服务的集成测试和验证

### 🔧 灵活的执行模式
- **脚本代理模式**: 通过自定义脚本处理代码，支持复杂的前后处理逻辑
- **直接执行模式**: 本地直接执行，适合快速原型验证
- **多种传输方式**: 支持 stdin 管道传输和临时文件传输

## 快速开始

### 安装
```bash
# 方式1: VS Code 扩展市场安装
# 搜索 "LCH Markdown Code Runner"

# 方式2: 手动安装
code --install-extension lch-markdown-code-runner-0.0.3.vsix
```

### 配置

在项目的 `.vscode/settings.json` 中配置 GM 处理器：

```jsonc
{
  "lchMarkdownCodeRunner.gmConfigs": {
    "GM": {
      "scriptPath": "scripts/test_runner.py",
      "commandTemplate": "python {scriptPath} {args}",
      "directMode": false,
      "passCodeAsStdin": true,
      "passCodeAsFile": false,
      "timeout": 30000
    },
    "GM_API": {
      "scriptPath": "scripts/api_tester.py", 
      "commandTemplate": "python {scriptPath} --endpoint {endpoint} --env {env}",
      "directMode": false,
      "passCodeAsStdin": true,
      "passCodeAsFile": false,
      "timeout": 15000
    },
    "GM_DATA": {
      "scriptPath": "scripts/data_processor.py",
      "commandTemplate": "python {scriptPath} --source {source} --format {format}",
      "directMode": false,
      "passCodeAsStdin": true,
      "passCodeAsFile": false,
      "timeout": 60000
    }
  }
}
```

## 使用示例

### 自动化测试场景
```python
#GM[suite=integration, env=staging, parallel=true]
# 这段代码将被发送到远程测试服务器执行
import requests

def test_user_api():
    response = requests.get("https://api.example.com/users")
    assert response.status_code == 200
    assert len(response.json()) > 0
    print("User API test passed")

test_user_api()
```

### API 接口测试
```python
#GM_API[endpoint=users, env=production]
# 通过 API 测试脚本验证接口
payload = {
    "name": "John Doe",
    "email": "john@example.com"
}

print("Testing user creation endpoint...")
# 代码会被传递给 api_tester.py 处理
```

### 数据分析处理
```python
#GM_DATA[source=database, format=json]
# 连接数据库进行实时分析
import pandas as pd

# 数据查询和处理逻辑
query = "SELECT * FROM users WHERE created_at > '2024-01-01'"
print(f"Executing query: {query}")

# 结果会通过 data_processor.py 处理和格式化
```

## 高级配置

### 参数说明

- **scriptPath**: 处理脚本的路径，支持相对路径和绝对路径
- **commandTemplate**: 命令执行模板，支持变量替换
  - `{scriptPath}`: 脚本路径
  - `{args}`: 从 GM 注解解析的参数
- **directMode**: 
  - `false`: 通过脚本处理（推荐）
  - `true`: 直接执行代码
- **passCodeAsStdin**: 通过标准输入传递代码（推荐）
- **passCodeAsFile**: 通过临时文件传递代码
- **timeout**: 执行超时时间（毫秒）

### 自定义处理脚本示例

创建 `scripts/api_tester.py`:
```python
#!/usr/bin/env python3
import sys
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--endpoint', required=True)
    parser.add_argument('--env', default='dev')
    args, _ = parser.parse_known_args()
    
    # 读取来自 stdin 的代码
    code = sys.stdin.read()
    
    # 设置执行环境
    globals_dict = {
        'ENDPOINT': args.endpoint,
        'ENV': args.env,
        # 添加其他环境变量和工具函数
    }
    
    # 执行代码
    exec(code, globals_dict)

if __name__ == '__main__':
    main()
```

## 应用场景

### 📋 文档驱动开发
- 将技术文档中的代码示例变为可执行的验证
- 确保文档与实际代码保持同步

### 🔬 探索性数据分析
- 在 Markdown 笔记中直接进行数据查询和可视化
- 连接不同的数据源进行对比分析

### 🌐 微服务集成测试
- 跨服务的端到端测试
- 环境隔离和配置管理

### 📊 报告自动化
- 动态生成包含实时数据的技术报告
- 定期执行数据更新和验证

## 故障排除

### 编码问题
如果遇到 Unicode 字符错误，请确保：
1. Python 脚本使用 UTF-8 编码
2. 在脚本开头添加：`# -*- coding: utf-8 -*-`
3. 避免在字符串中使用特殊 Unicode 字符，或使用转义序列

### 权限问题
- 确保脚本文件具有执行权限
- 检查网络访问权限（如果涉及远程调用）

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**让你的 Markdown 文档成为强大的自动化工具** 🚀

