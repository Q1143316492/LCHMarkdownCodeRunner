# http_gateway

## 1. Description

We have a sample system, for example, `example_system`, which usually runs in a loop.

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

This system typically provides a command entry point, a function that takes a string as input and executes it.

```python
    def on_debug_input(self, input_str):
        print(f"Debug input received: [{input_str}]")
        eval(input_str)
```

So how do we call this function? Usually, the system provides some command input boxes or web pages. However, limited by the implementation, I think most command input boxes are not as convenient, intuitive, or good-looking as VS Code's markdown code blocks for editing.

The final effect is to directly initiate a command call from a code block in markdown.

I hope to execute a command through a "command system" that comes with the system, like this, to start an asynchronous thread for listening.

Note that you need to call the `lch_http.tick_queue` function with your own tick. It will thread-safely pass the result string to the `on_debug_input` function in the main thread.

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

It will continuously accept POST requests to `/lch_call`, with the content being a string, and put it into a thread-safe queue.

Then the main thread needs to continuously fetch from this queue, usually by registering a global tick in `example_system`, and then call the system's `on_debug_input` function after getting it.

Some tests:
```cmd
# Normal call OK
curl.exe -X POST "http://127.0.0.1:8000/lch_call" -H "Content-Type: application/json" -d "{\"message\":\"print('111')\"}"
{"status": "ok"}

# Get call result, no result
curl.exe -X GET  "http://127.0.0.1:8000/lch_get_ret"
{"status": "no_result"}

# Set call result
curl.exe -X POST "http://127.0.0.1:8000/lch_set_ret" -H "Content-Type: application/json" -d "{\"result\":\"done\"}"
{"status": "ok"}

# Get call result, there is a result, getting it again results in no result
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

VS Code terminal output after running:
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
GM Directive args: ["9090","gcc"]
GM Directive params: {}
==================================================
Code to execute:
──────────────────────────────
a = 1
b = 2
print(a + b)
print("Hello, World!")
1 / 0
──────────────────────────────
Executing: python http_gateway/python_gateway/lch_gateway_cli.py 9090 gcc
```