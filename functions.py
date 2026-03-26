# function.py

import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf


def _sanitize_name(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", name)


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    return df


def _add_extra_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    if "Close" in df.columns:
        df["Daily Return %"] = df["Close"].pct_change() * 100

    if {"High", "Low"}.issubset(df.columns):
        df["High-Low Gap"] = df["High"] - df["Low"]

    if {"Open", "Close"}.issubset(df.columns):
        df["Open-Close Change"] = df["Close"] - df["Open"]

    return df


def _calculate_statistics(series: pd.Series, column_name: str, share_name: str) -> dict:
    x = series.dropna().to_numpy(dtype=float)

    if len(x) == 0:
        return {
            "Share": share_name,
            "Column": column_name,
            "Count": 0,
            "Sum": np.nan,
            "Mean": np.nan,
            "Median": np.nan,
            "Mode": [],
            "Min": np.nan,
            "Q1": np.nan,
            "Q2": np.nan,
            "Q3": np.nan,
            "IQR": np.nan,
            "Max": np.nan,
            "Range": np.nan,
            "Variance (Population)": np.nan,
            "Std Dev (Population)": np.nan,
            "Variance (Sample)": np.nan,
            "Std Dev (Sample)": np.nan,
            "Skewness": np.nan,
            "Kurtosis": np.nan,
        }

    values, counts = np.unique(x, return_counts=True)
    max_count = np.max(counts)
    modes = values[counts == max_count].tolist()

    q1 = np.percentile(x, 25)
    q2 = np.percentile(x, 50)
    q3 = np.percentile(x, 75)

    sample_variance = np.var(x, ddof=1) if len(x) > 1 else np.nan
    sample_std = np.std(x, ddof=1) if len(x) > 1 else np.nan

    return {
        "Share": share_name,
        "Column": column_name,
        "Count": len(x),
        "Sum": float(np.sum(x)),
        "Mean": float(np.mean(x)),
        "Median": float(np.median(x)),
        "Mode": modes,
        "Min": float(np.min(x)),
        "Q1": float(q1),
        "Q2": float(q2),
        "Q3": float(q3),
        "IQR": float(q3 - q1),
        "Max": float(np.max(x)),
        "Range": float(np.max(x) - np.min(x)),
        "Variance (Population)": float(np.var(x)),
        "Std Dev (Population)": float(np.std(x)),
        "Variance (Sample)": float(sample_variance) if not np.isnan(sample_variance) else np.nan,
        "Std Dev (Sample)": float(sample_std) if not np.isnan(sample_std) else np.nan,
        "Skewness": float(pd.Series(x).skew()),
        "Kurtosis": float(pd.Series(x).kurt()),
    }


def _collect_stats(df: pd.DataFrame, share_name: str) -> pd.DataFrame:
    numeric_columns = [col for col in df.columns if pd.api.types.is_numeric_dtype(df[col])]
    stats = [_calculate_statistics(df[col], col, share_name) for col in numeric_columns]
    return pd.DataFrame(stats)


def _print_stats(stats_df: pd.DataFrame, share_name: str) -> None:
    print("\n" + "=" * 100)
    print(f"FULL STATISTICS FOR {share_name}")
    print("=" * 100)

    for _, row in stats_df.iterrows():
        print(f"\n--- {row['Column']} ---")
        for col_name, value in row.items():
            print(f"{col_name}: {value}")


def _get_stat_value(stats_df: pd.DataFrame, col_name: str, stat_name: str):
    row = stats_df[stats_df["Column"] == col_name]
    if row.empty:
        return np.nan
    return row.iloc[0][stat_name]


def _save_single_share_charts(df: pd.DataFrame, share_name: str, prefix: str, output_dir: str) -> list:
    saved_files = []

    if "Close" in df.columns:
        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df["Close"], marker="o")
        plt.title(f"{share_name} Closing Price")
        plt.xlabel("Date")
        plt.ylabel("Close Price")
        plt.xticks(rotation=45)
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_close_line.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

    if "Volume" in df.columns:
        plt.figure(figsize=(10, 5))
        plt.bar(df.index, df["Volume"])
        plt.title(f"{share_name} Volume")
        plt.xlabel("Date")
        plt.ylabel("Volume")
        plt.xticks(rotation=45)
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_volume_bar.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

    ohlc_cols = [col for col in ["Open", "High", "Low", "Close"] if col in df.columns]
    if ohlc_cols:
        plt.figure(figsize=(8, 5))
        plt.boxplot([df[col].dropna() for col in ohlc_cols], tick_labels=ohlc_cols)
        plt.title(f"{share_name} OHLC Box Plot")
        plt.ylabel("Price")
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_ohlc_boxplot.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

    if "Close" in df.columns:
        plt.figure(figsize=(8, 5))
        plt.hist(df["Close"].dropna(), bins=10)
        plt.title(f"{share_name} Close Price Histogram")
        plt.xlabel("Close Price")
        plt.ylabel("Frequency")
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_close_histogram.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

    if "Daily Return %" in df.columns:
        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df["Daily Return %"], marker="o")
        plt.axhline(0, linewidth=1)
        plt.title(f"{share_name} Daily Return %")
        plt.xlabel("Date")
        plt.ylabel("Return %")
        plt.xticks(rotation=45)
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_daily_return_line.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

    if "High-Low Gap" in df.columns:
        plt.figure(figsize=(10, 5))
        plt.plot(df.index, df["High-Low Gap"], marker="o")
        plt.title(f"{share_name} High-Low Gap")
        plt.xlabel("Date")
        plt.ylabel("High - Low")
        plt.xticks(rotation=45)
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_high_low_gap.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

    if "Open-Close Change" in df.columns:
        plt.figure(figsize=(10, 5))
        plt.bar(df.index, df["Open-Close Change"])
        plt.axhline(0, linewidth=1)
        plt.title(f"{share_name} Open-Close Change")
        plt.xlabel("Date")
        plt.ylabel("Close - Open")
        plt.xticks(rotation=45)
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_open_close_change.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

    return saved_files


def analyze_share(
    share_name: str,
    period: str = "1mo",
    interval: str = "1d",
    output_dir: str = "stock_output"
):
    os.makedirs(output_dir, exist_ok=True)

    safe_name = _sanitize_name(share_name)
    prefix = f"{safe_name}_{period}_{interval}"

    print("=" * 100)
    print(f"Downloading data for: {share_name}")
    print(f"Period: {period} | Interval: {interval}")
    print("=" * 100)

    df = yf.download(
        share_name,
        period=period,
        interval=interval,
        auto_adjust=False,
        progress=False
    )

    if df.empty:
        print("No data found. Check the share name/ticker and try again.")
        return None

    df = _flatten_columns(df)
    df = df.dropna(how="all").copy()
    df = _add_extra_columns(df)

    raw_csv = os.path.join(output_dir, f"{prefix}_raw_data.csv")
    df.to_csv(raw_csv)

    print("\nDownloaded Data:")
    print(df.head())
    print(f"\nRaw data saved to: {raw_csv}")

    stats_df = _collect_stats(df, share_name)
    stats_csv = os.path.join(output_dir, f"{prefix}_statistics.csv")
    stats_df.to_csv(stats_csv, index=False)

    _print_stats(stats_df, share_name)
    print(f"\nStatistics saved to: {stats_csv}")

    chart_files = _save_single_share_charts(df, share_name, prefix, output_dir)

    print("\n" + "=" * 100)
    print("CHART FILES SAVED")
    print("=" * 100)
    for f in chart_files:
        print(f)

    return {
        "share": share_name,
        "data": df,
        "statistics": stats_df,
        "raw_csv": raw_csv,
        "stats_csv": stats_csv,
        "chart_files": chart_files,
    }


def analyze_two_shares(
    share1: str,
    share2: str,
    period: str = "1mo",
    interval: str = "1d",
    output_dir: str = "stock_compare_output"
):
    os.makedirs(output_dir, exist_ok=True)

    safe_share1 = _sanitize_name(share1)
    safe_share2 = _sanitize_name(share2)
    prefix = f"{safe_share1}_vs_{safe_share2}_{period}_{interval}"

    print("=" * 100)
    print(f"Downloading data for {share1} and {share2}")
    print(f"Period: {period} | Interval: {interval}")
    print("=" * 100)

    df1 = yf.download(share1, period=period, interval=interval, auto_adjust=False, progress=False)
    df2 = yf.download(share2, period=period, interval=interval, auto_adjust=False, progress=False)

    if df1.empty or df2.empty:
        print("One or both shares returned no data. Check the ticker names.")
        return None

    df1 = _flatten_columns(df1)
    df2 = _flatten_columns(df2)

    df1 = df1.dropna(how="all").copy()
    df2 = df2.dropna(how="all").copy()

    df1 = _add_extra_columns(df1)
    df2 = _add_extra_columns(df2)

    raw1_csv = os.path.join(output_dir, f"{safe_share1}_{period}_{interval}_raw.csv")
    raw2_csv = os.path.join(output_dir, f"{safe_share2}_{period}_{interval}_raw.csv")
    df1.to_csv(raw1_csv)
    df2.to_csv(raw2_csv)

    print("\nRaw data saved:")
    print(raw1_csv)
    print(raw2_csv)

    stats1 = _collect_stats(df1, share1)
    stats2 = _collect_stats(df2, share2)

    _print_stats(stats1, share1)
    _print_stats(stats2, share2)

    all_stats = pd.concat([stats1, stats2], ignore_index=True)
    stats_csv = os.path.join(output_dir, f"{prefix}_statistics.csv")
    all_stats.to_csv(stats_csv, index=False)
    print(f"\nCombined statistics saved to: {stats_csv}")

    comparison_rows = []
    for col_name in ["Close", "Volume", "Daily Return %", "High-Low Gap", "Open-Close Change"]:
        if col_name in df1.columns and col_name in df2.columns:
            comparison_rows.append({
                "Column": col_name,
                f"{share1} Mean": _get_stat_value(stats1, col_name, "Mean"),
                f"{share2} Mean": _get_stat_value(stats2, col_name, "Mean"),
                f"{share1} Std Dev": _get_stat_value(stats1, col_name, "Std Dev (Population)"),
                f"{share2} Std Dev": _get_stat_value(stats2, col_name, "Std Dev (Population)"),
                f"{share1} Min": _get_stat_value(stats1, col_name, "Min"),
                f"{share2} Min": _get_stat_value(stats2, col_name, "Min"),
                f"{share1} Max": _get_stat_value(stats1, col_name, "Max"),
                f"{share2} Max": _get_stat_value(stats2, col_name, "Max"),
            })

    comparison_df = pd.DataFrame(comparison_rows)
    comparison_csv = os.path.join(output_dir, f"{prefix}_comparison_summary.csv")
    comparison_df.to_csv(comparison_csv, index=False)

    print("\n" + "=" * 100)
    print("COMPARISON SUMMARY")
    print("=" * 100)
    if not comparison_df.empty:
        print(comparison_df.to_string(index=False))
    else:
        print("No common comparison columns found.")
    print(f"\nComparison summary saved to: {comparison_csv}")

    common_index = df1.index.intersection(df2.index)
    aligned1 = df1.loc[common_index].copy()
    aligned2 = df2.loc[common_index].copy()

    saved_files = []

    if "Close" in aligned1.columns and "Close" in aligned2.columns:
        plt.figure(figsize=(10, 5))
        plt.plot(aligned1.index, aligned1["Close"], marker="o", label=share1)
        plt.plot(aligned2.index, aligned2["Close"], marker="o", label=share2)
        plt.title(f"{share1} vs {share2} Close Price")
        plt.xlabel("Date")
        plt.ylabel("Close Price")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_close_comparison.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

        norm1 = aligned1["Close"] / aligned1["Close"].iloc[0] * 100
        norm2 = aligned2["Close"] / aligned2["Close"].iloc[0] * 100

        plt.figure(figsize=(10, 5))
        plt.plot(aligned1.index, norm1, marker="o", label=share1)
        plt.plot(aligned2.index, norm2, marker="o", label=share2)
        plt.title(f"{share1} vs {share2} Normalized Performance (Base = 100)")
        plt.xlabel("Date")
        plt.ylabel("Normalized Value")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_normalized_close.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

        plt.figure(figsize=(8, 5))
        plt.hist(df1["Close"].dropna(), bins=10, alpha=0.7, label=share1)
        plt.hist(df2["Close"].dropna(), bins=10, alpha=0.7, label=share2)
        plt.title(f"{share1} vs {share2} Close Price Distribution")
        plt.xlabel("Close Price")
        plt.ylabel("Frequency")
        plt.legend()
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_close_hist_comparison.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

        plt.figure(figsize=(8, 5))
        plt.boxplot(
            [df1["Close"].dropna(), df2["Close"].dropna()],
            tick_labels=[share1, share2]
        )
        plt.title(f"{share1} vs {share2} Close Price Box Plot")
        plt.ylabel("Close Price")
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_close_boxplot.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

        mean_close_1 = df1["Close"].mean()
        mean_close_2 = df2["Close"].mean()

        plt.figure(figsize=(7, 5))
        plt.bar([share1, share2], [mean_close_1, mean_close_2])
        plt.title("Mean Close Price Comparison")
        plt.ylabel("Mean Close Price")
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_mean_close_bar.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

        std_close_1 = df1["Close"].std(ddof=0)
        std_close_2 = df2["Close"].std(ddof=0)

        plt.figure(figsize=(7, 5))
        plt.bar([share1, share2], [std_close_1, std_close_2])
        plt.title("Close Price Standard Deviation Comparison")
        plt.ylabel("Std Dev")
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_std_close_bar.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

    if "Volume" in aligned1.columns and "Volume" in aligned2.columns:
        x = np.arange(len(common_index))
        width = 0.4

        plt.figure(figsize=(10, 5))
        plt.bar(x - width / 2, aligned1["Volume"], width=width, label=share1)
        plt.bar(x + width / 2, aligned2["Volume"], width=width, label=share2)
        plt.title(f"{share1} vs {share2} Volume")
        plt.xlabel("Date Index")
        plt.ylabel("Volume")
        plt.legend()
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_volume_comparison.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

    if "Daily Return %" in aligned1.columns and "Daily Return %" in aligned2.columns:
        plt.figure(figsize=(10, 5))
        plt.plot(aligned1.index, aligned1["Daily Return %"], marker="o", label=share1)
        plt.plot(aligned2.index, aligned2["Daily Return %"], marker="o", label=share2)
        plt.axhline(0, linewidth=1)
        plt.title(f"{share1} vs {share2} Daily Return %")
        plt.xlabel("Date")
        plt.ylabel("Daily Return %")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_daily_return_comparison.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

    if "High-Low Gap" in aligned1.columns and "High-Low Gap" in aligned2.columns:
        plt.figure(figsize=(10, 5))
        plt.plot(aligned1.index, aligned1["High-Low Gap"], marker="o", label=share1)
        plt.plot(aligned2.index, aligned2["High-Low Gap"], marker="o", label=share2)
        plt.title(f"{share1} vs {share2} High-Low Gap")
        plt.xlabel("Date")
        plt.ylabel("High - Low")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_high_low_gap_comparison.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

    if "Open-Close Change" in aligned1.columns and "Open-Close Change" in aligned2.columns:
        plt.figure(figsize=(10, 5))
        plt.plot(aligned1.index, aligned1["Open-Close Change"], marker="o", label=share1)
        plt.plot(aligned2.index, aligned2["Open-Close Change"], marker="o", label=share2)
        plt.axhline(0, linewidth=1)
        plt.title(f"{share1} vs {share2} Open-Close Change")
        plt.xlabel("Date")
        plt.ylabel("Close - Open")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        file_path = os.path.join(output_dir, f"{prefix}_open_close_change_comparison.png")
        plt.savefig(file_path, dpi=150, bbox_inches="tight")
        plt.close()
        saved_files.append(file_path)

    print("\n" + "=" * 100)
    print("CHART FILES SAVED")
    print("=" * 100)
    for file_name in saved_files:
        print(file_name)

    return {
        share1: {
            "data": df1,
            "raw_csv": raw1_csv,
            "stats": stats1,
        },
        share2: {
            "data": df2,
            "raw_csv": raw2_csv,
            "stats": stats2,
        },
        "all_statistics": all_stats,
        "statistics_csv": stats_csv,
        "comparison_summary": comparison_df,
        "comparison_csv": comparison_csv,
        "chart_files": saved_files,
    }