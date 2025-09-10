#encoding=utf-8
import sys
import os
import time

g_System = None

class TickScheduler:
    """A tiny repeating tick scheduler.

    - register(interval_seconds: float, func, *args, **kwargs) -> tick_id
    - unregister(tick_id) -> bool
    - run_due(now: float | None = None): run all due ticks and reschedule them

    For demo purposes only; single-threaded, driven by caller's loop.
    """

    def __init__(self):
        self._ticks = {}  # id -> {"interval": float, "next": float, "func": callable, "args": tuple, "kwargs": dict}
        self._next_tick_id = 1

    def register(self, interval_seconds: float, func, *args, **kwargs) -> int:
        if not isinstance(interval_seconds, (int, float)) or interval_seconds <= 0:
            raise ValueError("interval_seconds must be a positive number")
        tick_id = self._next_tick_id
        self._next_tick_id += 1
        self._ticks[tick_id] = {
            "interval": float(interval_seconds),
            "next": time.time() + float(interval_seconds),
            "func": func,
            "args": args,
            "kwargs": kwargs or {},
        }
        return tick_id

    def unregister(self, tick_id: int) -> bool:
        return self._ticks.pop(tick_id, None) is not None

    def run_due(self, now: float | None = None):
        if now is None:
            now = time.time()
        for tick_id, tick in list(self._ticks.items()):
            if now >= tick["next"]:
                try:
                    tick["func"](*tick["args"], **tick["kwargs"])  # type: ignore[misc]
                except Exception as e:
                    print(f"Tick {tick_id} handler error: {e}")
                tick["next"] += tick["interval"]

class ExampleSystem:
    def __init__(self):
        # Minimal repeating tick scheduler
        self._scheduler = TickScheduler()
        # Optional resource used by HTTP gateway starter
        self.http_server = None

    def start(self):
        print("Example system started")
        self.on_debug_input("print('Hello from debug input!')")
        self.start_http_gateway()

    def loop(self):
        # Drive the simple tick scheduler
        self._scheduler.run_due()
        print("Example system is running")

    def stop(self):
        print("Example system stopped")
        self.stop_http_gateway()

    def on_debug_input(self, input_str):
        print(f"Debug input received: [{input_str}]")
        eval(input_str)

    # --- Simple repeating tick API (pass-through to scheduler) ---
    def register_tick(self, interval_seconds: float, func, *args, **kwargs) -> int:
        return self._scheduler.register(interval_seconds, func, *args, **kwargs)

    def unregister_tick(self, tick_id: int) -> bool:
        return self._scheduler.unregister(tick_id)

    # --- HTTP gateway helpers ---

    def start_http_gateway(self):
        base_dir = os.path.dirname(__file__)
        py_gateway = os.path.normpath(os.path.join(base_dir, "..", "python_gateway"))
        if py_gateway not in sys.path:
            sys.path.append(py_gateway)

        import lch_http  # type: ignore
        self.http_server, _ = lch_http.start_server(host="127.0.0.1", port=9090)
        lch_http.tick_id = self.register_tick(0.5, lch_http.tick_queue, self.on_debug_input)

    def stop_http_gateway(self):
        base_dir = os.path.dirname(__file__)
        py_gateway = os.path.normpath(os.path.join(base_dir, "..", "python_gateway"))
        if py_gateway not in sys.path:
            sys.path.append(py_gateway)

        import lch_http  # type: ignore
        if self.http_server:
            lch_http.stop_server(self.http_server)
            self.http_server = None

        if lch_http.tick_id != -1:
            self.unregister_tick(lch_http.tick_id)
            lch_http.tick_id = -1


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


if __name__ == "__main__":
    main()
