import utilities as ut
import graphutilities as gu


def fetchStockPrice() -> float:
    stockname="ril"
    """Adapter for your existing utilities.getStockPrice('ril').

    utilities.getStockPrice appears to return either:
      - (price, filename) tuple
      - an Exception object
    """
    res = ut.getStockPrice(stockname)

    if isinstance(res, tuple) and len(res) >= 1:
        return float(res[0])

    # If utilities returned an Exception instance, raise it; else raise generic.
    if isinstance(res, Exception):
        raise res

    raise RuntimeError(f"Unexpected getStockPrice return: {res!r}")


if __name__ == "__main__":
    
    stockname=input("Enter stockname\n").strip().lower()
    gu.run_live_price_chart(
        fetchStockPrice,
        symbol="RIL",
        fetch_interval=60,
        ui_interval_ms=250,
        window_points=180,
    )
