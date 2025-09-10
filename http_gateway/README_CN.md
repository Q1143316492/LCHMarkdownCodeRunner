# http_gateway

## 1. 说明

我们有一个示例系统，例如example_system，它通常位于一个循环中

```python
def main():
    global g_System
    g_System = ExampleSystem()
    g_System.start()
    try:
        while True:
            g_System.loop()
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        g_System.stop()
```

这个系统通常会提供一个指令入口，提供一个函数，输入一个字符串，最后执行这个字符串

```python
    def on_debug_input(self, input_str):
        print(f"Debug input received: [{input_str}]")
        eval(input_str)
```

而如何调用到这个函数呢，通常系统会提供某些指令输入框，或者是某些web页面。但是受限于实现方式，我认为大多数指令输入框，都不如vscode的markdown代码块方便编辑，直观, 好看。

最终效果是从markdown中的代码块直接发起一个指令调用

我希望预先通过一个系统自带的“指令系统”执行一个命令，就像这样，开启一个异步线程的监听。

注意，你需要用自己的tick调用 lch_http.tick_queue 函数，他会线程安全的在主线程把结果字符串交给 on_debug_input 函数

```python
def start_http_gateway(self):
    base_dir = os.path.dirname(__file__)
    py_gateway = os.path.normpath(os.path.join(base_dir, "..", "python_gateway"))
    if py_gateway not in sys.path:
        sys.path.append(py_gateway)

    import lch_http  # type: ignore
    self.http_server, _ = lch_http.start_server(host="127.0.0.1", port=9090)
    lch_http.tick_id = self.register_tick(0.5, lch_http.tick_queue, self.on_debug_input)
```

它会不断的接受 /lch_call 的post请求，内容是一个字符串，放到一个线程安全的队列中。

然后主线程要不断的去拿这个，通常是通过example_system注册一个全局的tick，拿到以后调用系统的on_debug_input函数。

一些测试
```cmd
# 正常调用OK
curl.exe -X POST "http://127.0.0.1:8000/lch_call" -H "Content-Type: application/json" -d "{\"message\":\"print('111')\"}"
{"status": "ok"}

# 获取调用结果，没有结果
curl.exe -X GET  "http://127.0.0.1:8000/lch_get_ret"
{"status": "no_result"}

# 设置调用结果
curl.exe -X POST "http://127.0.0.1:8000/lch_set_ret" -H "Content-Type: application/json" -d "{\"result\":\"done\"}"
{"status": "ok"}

# 获取调用结果，有结果，再次获取没有结果
curl.exe -X GET  "http://127.0.0.1:8000/lch_get_ret"
{"status": "ok", "result": "done"}
curl.exe -X GET  "http://127.0.0.1:8000/lch_get_ret"
{"status": "no_result"}
```

```python
#GM3[9090, gcc]
a = 1
b = 2
print(a + b)
print("Hello, World!")
1 / 0
```

运行后vscode的终端输出
```output
==================================================
Running Python code from e:\Epic\WorkspaceByRelease\LCHMarkdownCodeRunner\http_gateway\README.md
{
  "scriptPath": "http_gateway/python_gateway/lch_gateway_cli.py",
  "commandTemplate": "python {scriptPath} {args}",
  "passCodeAsStdin": true,
  "passCodeAsFile": false,
  "timeout": 3000
}
GM Identifier: GM3
Script Path: http_gateway/python_gateway/lch_gateway_cli.py
Command Template: python {scriptPath} {args}
Pass Code As Stdin: true
Pass Code As File: false
Timeout: 3000
```
