import utilities as ut
import graphutilities as gu


def make_fetchStockPrice(stockname: str):
    """
    Returns a no-argument function that fetches price for the given stockname.
    """

    stockname = stockname.lower().strip()

    def fetchStockPrice() -> float:
        """
        Adapter for utilities.getStockPrice(stockname)

        utilities.getStockPrice returns either:
          - (price, filename) tuple
          - an Exception object
        """
        res = ut.getStockPrice(stockname)

        if isinstance(res, tuple) and len(res) >= 1:
            return float(res[0])

        if isinstance(res, Exception):
            raise res

        raise RuntimeError(f"Unexpected getStockPrice return: {res!r}")

    return fetchStockPrice


if __name__ == "__main__":

    stockname = input("Enter stockname\n").strip().lower()

    gu.run_live_price_chart(
        make_fetchStockPrice(stockname),
        symbol=stockname.upper(),
        fetch_interval=60,
        ui_interval_ms=250,
        window_points=180,
    )
