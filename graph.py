import random
import time
from collections import deque

import matplotlib.pyplot as plt


def simulate_next_price(price: float, drift: float = 0.0002, vol: float = 0.01) -> float:
    """
    Simple stock price simulator (random walk on returns).
    drift: expected return per step (small)
    vol: volatility per step
    """
    r = random.gauss(drift, vol)          # return this step
    new_price = price * (1.0 + r)
    return max(new_price, 0.01)           # avoid zero/negative


def main():
    # --- Settings ---
    symbol = "DEMO"
    start_price = 100.0
    interval_sec = 0.5          # how often to "tick"
    total_seconds = 30          # how long to run
    window_points = 120         # rolling window (set None to keep all)

    # --- Data containers ---
    if window_points is None:
        x = []
        y = []
    else:
        x = deque(maxlen=window_points)
        y = deque(maxlen=window_points)

    # --- Matplotlib setup ---
    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot([], [], marker="o", markersize=3, linewidth=1)

    ax.set_title(f"Stock Price Simulation — {symbol}")
    ax.set_xlabel("Tick")
    ax.set_ylabel("Price")

    plt.show()

    # --- Simulation loop ---
    price = start_price
    tick = 0
    end_time = time.time() + total_seconds

    while time.time() < end_time:
        tick += 1
        price = simulate_next_price(price)

        x.append(tick)
        y.append(price)

        # Update plot (the exact pattern you asked for)
        line.set_data(list(x), list(y))
        ax.relim()
        ax.autoscale_view()

        ax.set_title(f"Stock Price Simulation — {symbol} | Last: {price:.2f}")

        plt.draw()
        plt.pause(0.01)         # refresh GUI
        time.sleep(interval_sec)

    # Keep window open at the end
    plt.ioff()
    plt.show()


if __name__ == "__main__":
    main()
