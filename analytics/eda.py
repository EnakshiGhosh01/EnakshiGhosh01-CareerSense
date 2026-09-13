import pandas as pd


INPUT_FILE = "data/processed/jobs_cleaned.csv"


def main():

    # ==================================================
    # LOAD CLEANED DATASET
    # ==================================================

    print("Loading cleaned dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    # ==================================================
    # 1. BASIC DATASET INFORMATION
    # ==================================================

    print("\n===== DATASET INFORMATION =====")

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    # ==================================================
    # 2. JOB TITLE ANALYSIS
    # ==================================================

    print("\n===== TOP 20 JOB TITLES =====")

    print(
        df["title"]
        .value_counts()
        .head(20)
    )

    # ==================================================
    # 3. LOCATION ANALYSIS
    # ==================================================

    print("\n===== TOP 20 LOCATIONS =====")

    print(
        df["location"]
        .value_counts()
        .head(20)
    )

    # ==================================================
    # 4. COMPANY ANALYSIS
    # ==================================================

    print("\n===== TOP 20 COMPANIES =====")

    print(
        df["companyName"]
        .value_counts()
        .head(20)
    )

    # ==================================================
    # 5. SALARY ANALYSIS
    # ==================================================

    print("\n===== SALARY STATUS =====")

    print(
        df["salary_status"]
        .value_counts()
    )

    print("\n===== SALARY MIDPOINT STATISTICS =====")

    salary = df.loc[
        df["salary_status"] == "disclosed",
        "salary_midpoint"
    ]

    print(salary.describe())

    # ==================================================
    # 6. SALARY BY EXPERIENCE
    # ==================================================

    print("\n===== SALARY BY EXPERIENCE =====")

    salary_experience = (
        df[df["salary_status"] == "disclosed"]
        .groupby("experience_midpoint")["salary_midpoint"]
        .agg(["count", "mean", "median"])
        .sort_index()
    )

    print(salary_experience.head(20))

    # ==================================================
    # 7. TOP SALARY JOB TITLES
    # ==================================================

    print("\n===== TOP 20 JOB TITLES BY MEDIAN SALARY =====")

    title_salary = (
        df[df["salary_status"] == "disclosed"]
        .groupby("title")["salary_midpoint"]
        .agg(["count", "mean", "median"])
    )

    # Only consider titles with at least 10 salary records.
    title_salary = title_salary[
        title_salary["count"] >= 10
    ]

    title_salary = title_salary.sort_values(
        "median",
        ascending=False
    )

    print(title_salary.head(20))

    # ==================================================
    # 8. REMOTE JOB ANALYSIS
    # ==================================================

    print("\n===== REMOTE JOB ANALYSIS =====")

    print(
        df["is_remote"]
        .value_counts()
    )

    remote_percentage = (
        df["is_remote"].mean() * 100
    )

    print(
        f"Remote job percentage: "
        f"{remote_percentage:.2f}%"
    )

    # ==================================================
    # 9. EXPERIENCE ANALYSIS
    # ==================================================

    print("\n===== EXPERIENCE DISTRIBUTION =====")

    print(
        df["experience_midpoint"]
        .describe()
    )

    # ==================================================
    # 10. DATA QUALITY CHECK
    # ==================================================

    print("\n===== DATA QUALITY CHECK =====")

    print(
        f"Duplicate rows: {df.duplicated().sum()}"
    )

    print("\nMissing values:")

    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(
        ascending=False
    )

    if missing.empty:
        print("No missing values found.")

    else:
        print(missing)

    # ==================================================
    # END
    # ==================================================

    print("\n===== EDA COMPLETED =====")


if __name__ == "__main__":
    main()