# functionsuse.py

from function import analyze_share, analyze_two_shares


def main():
    print("Choose an option:")
    print("1. Analyze one share")
    print("2. Compare two shares")

    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        share = input("Enter share ticker (example: RELIANCE.NS): ").strip()
        period = input("Enter time period (example: 1mo, 3mo, 6mo, 1y) [default=1mo]: ").strip() or "1mo"
        interval = input("Enter interval (example: 1d, 1wk, 1mo) [default=1d]: ").strip() or "1d"
        output_dir = input("Enter output folder [default=stock_output]: ").strip() or "stock_output"

        result = analyze_share(
            share_name=share,
            period=period,
            interval=interval,
            output_dir=output_dir
        )

        if result is not None:
            print("\nDone.")
            print("Raw CSV:", result["raw_csv"])
            print("Statistics CSV:", result["stats_csv"])
            print("Charts:")
            for file_path in result["chart_files"]:
                print(file_path)

    elif choice == "2":
        share1 = input("Enter first share ticker (example: RELIANCE.NS): ").strip()
        share2 = input("Enter second share ticker (example: TCS.NS): ").strip()
        period = input("Enter time period (example: 1mo, 3mo, 6mo, 1y) [default=1mo]: ").strip() or "1mo"
        interval = input("Enter interval (example: 1d, 1wk, 1mo) [default=1d]: ").strip() or "1d"
        output_dir = input("Enter output folder [default=stock_compare_output]: ").strip() or "stock_compare_output"

        result = analyze_two_shares(
            share1=share1,
            share2=share2,
            period=period,
            interval=interval,
            output_dir=output_dir
        )

        if result is not None:
            print("\nDone.")
            print("Statistics CSV:", result["statistics_csv"])
            print("Comparison CSV:", result["comparison_csv"])
            print("Charts:")
            for file_path in result["chart_files"]:
                print(file_path)

    else:
        print("Invalid choice. Please run the program again and enter 1 or 2.")


if __name__ == "__main__":
    main()