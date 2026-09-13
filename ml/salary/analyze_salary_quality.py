import pandas as pd

INPUT_FILE = "data/processed/jobs_cleaned.csv"


def main():

    print("Loading cleaned dataset...")
    df = pd.read_csv(INPUT_FILE)

    salary_df = df[
        df["salary_status"] == "disclosed"
    ].copy()

    salary_df = salary_df.dropna(
        subset=[
            "minimumSalary",
            "maximumSalary",
            "salary_midpoint"
        ]
    )

    print(f"\nTotal disclosed salary records: {len(salary_df)}")

    # ==================================================
    # SALARY DISTRIBUTION
    # ==================================================

    print("\n===== SALARY MIDPOINT PERCENTILES =====")

    percentiles = [
        0.001,
        0.005,
        0.01,
        0.02,
        0.05,
        0.10,
        0.25,
        0.50,
        0.75,
        0.90,
        0.95,
        0.99,
        0.995,
        0.999
    ]

    print(
        salary_df["salary_midpoint"]
        .quantile(percentiles)
    )

    # ==================================================
    # VERY LOW SALARIES
    # ==================================================

    print("\n===== SALARIES BELOW ₹50,000 =====")

    low_50k = salary_df[
        salary_df["salary_midpoint"] < 50000
    ].sort_values("salary_midpoint")

    print(
        f"Count: {len(low_50k)}"
    )

    print(
        low_50k[
            [
                "title",
                "companyName",
                "location",
                "minimumSalary",
                "maximumSalary",
                "salary_midpoint"
            ]
        ].head(30).to_string(index=False)
    )

    # ==================================================
    # SALARIES BELOW ₹1 LAKH
    # ==================================================

    print("\n===== SALARIES BELOW ₹1 LAKH =====")

    low_1l = salary_df[
        salary_df["salary_midpoint"] < 100000
    ]

    print(
        f"Count: {len(low_1l)}"
    )

    # ==================================================
    # SALARIES BELOW ₹2 LAKH
    # ==================================================

    print("\n===== SALARIES BELOW ₹2 LAKH =====")

    low_2l = salary_df[
        salary_df["salary_midpoint"] < 200000
    ]

    print(
        f"Count: {len(low_2l)}"
    )

    # ==================================================
    # SALARY RANGES
    # ==================================================

    print("\n===== SALARY RANGE COUNTS =====")

    ranges = {
        "Below ₹50K": (
            salary_df["salary_midpoint"] < 50000
        ),

        "₹50K - ₹1L": (
            (salary_df["salary_midpoint"] >= 50000)
            & (salary_df["salary_midpoint"] < 100000)
        ),

        "₹1L - ₹2L": (
            (salary_df["salary_midpoint"] >= 100000)
            & (salary_df["salary_midpoint"] < 200000)
        ),

        "₹2L - ₹3L": (
            (salary_df["salary_midpoint"] >= 200000)
            & (salary_df["salary_midpoint"] < 300000)
        ),

        "₹3L - ₹5L": (
            (salary_df["salary_midpoint"] >= 300000)
            & (salary_df["salary_midpoint"] < 500000)
        ),

        "₹5L - ₹10L": (
            (salary_df["salary_midpoint"] >= 500000)
            & (salary_df["salary_midpoint"] < 1000000)
        ),

        "₹10L - ₹25L": (
            (salary_df["salary_midpoint"] >= 1000000)
            & (salary_df["salary_midpoint"] < 2500000)
        ),

        "Above ₹25L": (
            salary_df["salary_midpoint"] >= 2500000
        )
    }

    for name, condition in ranges.items():

        count = condition.sum()

        percentage = (
            count / len(salary_df) * 100
        )

        print(
            f"{name:<15} "
            f"{count:>6} "
            f"({percentage:.2f}%)"
        )

    # ==================================================
    # LOW SALARY BY JOB TITLE
    # ==================================================

    print("\n===== JOB TITLES WITH VERY LOW SALARIES =====")

    low_title = (
        salary_df[
            salary_df["salary_midpoint"] < 100000
        ]
        .groupby("title")
        .size()
        .sort_values(ascending=False)
        .head(30)
    )

    print(low_title)

    # ==================================================
    # EXTREME HIGH SALARIES
    # ==================================================

    print("\n===== EXTREME HIGH SALARIES =====")

    high = salary_df[
        salary_df["salary_midpoint"] > 10000000
    ].sort_values(
        "salary_midpoint",
        ascending=False
    )

    print(
        f"Count above ₹1 Crore: {len(high)}"
    )

    print(
        high[
            [
                "title",
                "companyName",
                "location",
                "minimumSalary",
                "maximumSalary",
                "salary_midpoint"
            ]
        ].head(30).to_string(index=False)
    )

    print(
        "\n===== SALARY QUALITY ANALYSIS COMPLETED ====="
    )


if __name__ == "__main__":
    main()