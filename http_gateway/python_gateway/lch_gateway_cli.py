#encoding=utf-8
import sys
import argparse
import os
import json
import time
import base64
from urllib import request, error
import re

def package_code(code: str, port: int) -> str:
    """Wrap user code to capture prints/exceptions and POST result to /lch_set_ret.

    The returned string is a single Python expression suitable for eval(),
    which internally uses exec() to run a multi-line block that:
        - redirects stdout to capture print output
        - executes the user's code
        - on exception, captures traceback
        - POSTs {"result": captured_text_or_traceback} to the local gateway
    """
    # 1) Rewrite print(...) to __lch_p(...) using a conservative regex.
    # Avoid matching attribute access like obj.print( ... )
    rewritten = re.sub(r"(?<![\w\.])print\s*\(", "__lch_p(", code)

    # 2) Build the executable block as a Python source string.
    # Define __lch_p to collect printed text into _out respecting sep/end.
    block = (
        "import json, io, traceback as _tb\n"
        "from urllib import request as _ur\n"
        "_out = []\n"
        "def __lch_p(*args, _out=_out, **kwargs):\n"
        "    sep = kwargs.pop('sep', ' ')\n"
        "    end = kwargs.pop('end', chr(10))\n"
        "    kwargs.pop('file', None); kwargs.pop('flush', None)\n"
        "    s = sep.join(str(a) for a in args) + end\n"
        "    _out.append(s)\n"
        "_res = ''\n"
        "try:\n"
        f"    exec({repr(rewritten)}, {{'__lch_p': __lch_p}})\n"
        "    _res = ''.join(_out)\n"
        "except Exception:\n"
        "    _res = _tb.format_exc()\n"
        "try:\n"
        "    _data = json.dumps({'result': _res}).encode('utf-8')\n"
        f"    _ur.urlopen(_ur.Request('http://127.0.0.1:{port}/lch_set_ret', data=_data, headers={{'Content-Type':'application/json; charset=utf-8'}}, method='POST'), timeout=0.5)\n"
        "except Exception:\n"
        "    pass\n"
    )
    # Build an eval-safe expression by base64-encoding the block to avoid
    # JSON decoding turning '\n' into real newlines inside quoted strings.
    b64 = base64.b64encode(block.encode('utf-8')).decode('ascii')
    return (
        "(__import__('builtins').exec)"
        "((__import__('base64').b64decode)('" + b64 + "').decode('utf-8'))"
    )


def lch_echo(port:int, process:str, code: str):
    base_url = f"http://127.0.0.1:{port}"
    code = package_code(code, port)

    # 1) Send code via /lch_call
    try:
        payload = json.dumps({"message": code}).encode("utf-8")
        req = request.Request(
            url=f"{base_url}/lch_call",
            data=payload,
            method="POST",
            headers={"Content-Type": "application/json; charset=utf-8"},
        )
        with request.urlopen(req, timeout=1.0) as resp:
            _ = resp.read()  # not used; expect {"status":"ok"}
    except Exception as exc:
        print(f"[gateway] Failed to POST /lch_call: {exc}")
        return

    # 2) Poll /lch_get_ret until result or timeout (2s)
    deadline = time.monotonic() + 2.0
    result = None
    while time.monotonic() < deadline:
        try:
            req = request.Request(url=f"{base_url}/lch_get_ret", method="GET")
            with request.urlopen(req, timeout=0.5) as resp:
                status = resp.getcode()
                data = resp.read().decode("utf-8", errors="replace")
            try:
                obj = json.loads(data) if data else {}
            except Exception:
                obj = {}

            if status == 200 and isinstance(obj, dict) and obj.get("status") == "ok":
                result = obj.get("result")
                break
            # For 401/no_result, just retry
        except error.HTTPError as he:
            # 401 is expected when no result yet; other codes are errors
            if he.code != 401:
                print(f"[gateway] HTTP error on /lch_get_ret: {he}")
                break
        except Exception:
            # Transient errors: wait and retry until deadline
            pass

        time.sleep(0.1)

    if result is not None:
        print("\n⭐ Result:")
        print(result)
    else:
        print("⏰ Timeout (2s) waiting for result.")

def main():
    print("\n🟦🟦🟦 BEGIN {} 🟦🟦🟦\n".format(os.path.basename(__file__)))
    print("🚩  Python Markdown Runner")
    print("🟢 Args:")
    print("   ", sys.argv)

    file_path, port, process = sys.argv
    port = int(port)

    if not sys.stdin.isatty():
        code = sys.stdin.read()
        if code.strip():
            print("\n⭐ Markdown Code Content:")
            print(code)
            lch_echo(port, process, code)
    print("\n🟦🟦🟦 END 🟦🟦🟦\n")

if __name__ == "__main__":
    main()
