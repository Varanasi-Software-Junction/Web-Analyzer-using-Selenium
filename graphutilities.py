from __future__ import annotations

import time
import threading
from queue import Queue, Empty
from collections import deque
from typing import Callable, Optional, Tuple

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

PriceFetcher = Callable[[], float]


def run_live_price_chart(
    fetch_price: PriceFetcher,
    *,
    symbol: str = "DEMO",
    fetch_interval: float = 1.0,
    ui_interval_ms: int = 200,
    window_points: int = 200,
    start_immediately: bool = True,
    show_markers: bool = True,
) -> None:
    q: Queue[Tuple[float, float]] = Queue()

    def worker() -> None:
        if start_immediately:
            _fetch_once(q, fetch_price)
        while True:
            time.sleep(fetch_interval)
            _fetch_once(q, fetch_price)

    threading.Thread(target=worker, daemon=True).start()

    x = deque(maxlen=window_points)
    y = deque(maxlen=window_points)
    tick = 0

    plt.ion()
    fig, ax = plt.subplots()
    marker = "o" if show_markers else None
    (line,) = ax.plot([], [], marker=marker, markersize=3, linewidth=1)

    ax.set_title(f"Live Stock Price — {symbol}")
    ax.set_xlabel("Tick")
    ax.set_ylabel("Price")

    status = ax.text(
        0.02,
        0.95,
        "Waiting for first price...",
        transform=ax.transAxes,
        va="top",
    )

    def animate(_frame):
        nonlocal tick

        latest: Optional[Tuple[float, float]] = None
        while True:
            try:
                latest = q.get_nowait()
            except Empty:
                break

        if latest is not None:
            _ts, price = latest
            tick += 1
            x.append(tick)
            y.append(price)

            line.set_data(list(x), list(y))
            ax.relim()
            ax.autoscale_view()
            status.set_text(f"Last: {price:.2f}   (points: {len(y)})")

        return line, status

    # ✅ IMPORTANT: keep reference alive + disable cache warning
    anim = FuncAnimation(
        fig,
        animate,
        interval=ui_interval_ms,
        blit=False,
        cache_frame_data=False,
        save_count=500,
    )
    fig._anim = anim  # extra-safe: prevents garbage collection in some environments

    plt.show(block=True)


def _fetch_once(q: Queue, fetch_price: PriceFetcher) -> None:
    try:
        price = float(fetch_price())
        q.put((time.time(), price))
        print("Fetched:", price)
    except Exception as e:
        print("Fetch error:", repr(e))
