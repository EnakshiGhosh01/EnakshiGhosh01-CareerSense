import pandas as pd


FILE_PATH = "data/raw/indian-job-market-dataset-2025.xlsx"


def main():
    # ==================================================
    # LOAD DATASET
    # ==================================================

    df = pd.read_excel(FILE_PATH)

    print("\n===== DATASET OVERVIEW =====")
    print(f"Rows: {df.shape[0]}")
    print(f"Columns: {df.shape[1]}")

    # ==================================================
    # COLUMN INFORMATION
    # ==================================================

    print("\n===== COLUMN NAMES =====")
    for column in df.columns:
        print(column)

    print("\n===== DATA TYPES =====")
    print(df.dtypes)

    # ==================================================
    # MISSING VALUES
    # ==================================================

    print("\n===== MISSING VALUES =====")

    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)

    if missing.empty:
        print("No missing values found.")
    else:
        print(missing)

    # ==================================================
    # DUPLICATES
    # ==================================================

    print("\n===== DUPLICATE ROWS =====")
    print(f"Duplicate rows: {df.duplicated().sum()}")

    # ==================================================
    # SALARY ANALYSIS
    # ==================================================

    print("\n===== SALARY VALUE COUNTS =====")
    print(df["salary"].value_counts().head(20))

    print("\n===== SALARY COLUMN MISSING VALUES =====")
    print(f"Missing salary values: {df['salary'].isna().sum()}")

    print("\n===== SALARY STATUS =====")

    not_disclosed = (df["salary"] == "Not disclosed").sum()
    unpaid = (df["salary"] == "Unpaid").sum()

    valid_salary = df[
        (df["minimumSalary"] > 0) &
        (df["maximumSalary"] > 0)
    ]

    print(f"Not disclosed: {not_disclosed}")
    print(f"Unpaid: {unpaid}")
    print(f"Valid salary ranges: {len(valid_salary)}")

    # ==================================================
    # SALARY STATISTICS
    # ==================================================

    print("\n===== SALARY STATISTICS =====")

    if not valid_salary.empty:
        print(
            valid_salary[
                ["minimumSalary", "maximumSalary"]
            ].describe()
        )

    # ==================================================
    # HIGHEST SALARY RECORDS
    # ==================================================

    print("\n===== HIGHEST SALARY RECORDS =====")

    highest_salary = valid_salary.sort_values(
        "maximumSalary",
        ascending=False
    )

    print(
        highest_salary[
            [
                "title",
                "companyName",
                "location",
                "salary",
                "minimumSalary",
                "maximumSalary",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    # ==================================================
    # LOWEST SALARY RECORDS
    # ==================================================

    print("\n===== LOWEST SALARY RECORDS =====")

    lowest_salary = valid_salary.sort_values(
        "minimumSalary"
    )

    print(
        lowest_salary[
            [
                "title",
                "companyName",
                "location",
                "salary",
                "minimumSalary",
                "maximumSalary",
            ]
        ]
        .head(20)
        .to_string(index=False)
    )

    # ==================================================
    # JOB TITLE ANALYSIS
    # ==================================================

    print("\n===== TOP 20 JOB TITLES =====")
    print(df["title"].value_counts().head(20))

    print("\n===== UNIQUE JOB TITLES =====")
    print(f"Unique job titles: {df['title'].nunique()}")

    # ==================================================
    # LOCATION ANALYSIS
    # ==================================================

    print("\n===== TOP 20 LOCATIONS =====")
    print(df["location"].value_counts().head(20))

    print("\n===== UNIQUE LOCATIONS =====")
    print(f"Unique locations: {df['location'].nunique()}")

    # ==================================================
    # COMPANY ANALYSIS
    # ==================================================

    print("\n===== TOP 20 COMPANIES =====")
    print(df["companyName"].value_counts().head(20))

    print("\n===== UNIQUE COMPANIES =====")
    print(f"Unique companies: {df['companyName'].nunique()}")

    # ==================================================
    # EXPERIENCE ANALYSIS
    # ==================================================

    print("\n===== EXPERIENCE RANGE =====")
    print(f"Minimum experience: {df['minimumExperience'].min()}")
    print(f"Maximum experience: {df['maximumExperience'].max()}")

    print("\n===== EXPERIENCE VALUE COUNTS =====")
    print(df["experience"].value_counts().head(20))

    # ==================================================
    # END
    # ==================================================

    print("\n===== ANALYSIS COMPLETED =====")


if __name__ == "__main__":
    main()