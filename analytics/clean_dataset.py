import pandas as pd


INPUT_FILE = "data/raw/indian-job-market-dataset-2025.xlsx"
OUTPUT_FILE = "data/processed/jobs_cleaned.csv"


def main():

    print("Loading dataset...")

    df = pd.read_excel(INPUT_FILE)

    print(f"Original rows: {len(df)}")

    # ==================================================
    # 1. REMOVE EXACT DUPLICATES
    # ==================================================

    duplicates = df.duplicated().sum()

    df = df.drop_duplicates().copy()

    print(f"Duplicates removed: {duplicates}")
    print(f"Rows after duplicate removal: {len(df)}")

    # ==================================================
    # 2. CLEAN TEXT COLUMNS
    # ==================================================

    text_columns = [
        "title",
        "companyName",
        "tagsAndSkills",
        "experience",
        "salary",
        "location",
        "jobDescription"
    ]

    for column in text_columns:
        df[column] = df[column].fillna("").astype(str).str.strip()

    # ==================================================
    # 3. CLEAN NUMERIC COLUMNS
    # ==================================================

    numeric_columns = [
        "minimumSalary",
        "maximumSalary",
        "minimumExperience",
        "maximumExperience",
        "ReviewsCount",
        "AggregateRating"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # ==================================================
    # 4. FIX INVALID SALARY VALUES
    # ==================================================

    # Negative salaries cannot be valid.
    df.loc[df["minimumSalary"] < 0, "minimumSalary"] = pd.NA
    df.loc[df["maximumSalary"] < 0, "maximumSalary"] = pd.NA

    # A maximum salary smaller than minimum salary is invalid.
    invalid_range = (
        df["minimumSalary"].notna()
        & df["maximumSalary"].notna()
        & (df["maximumSalary"] < df["minimumSalary"])
    )

    print(f"Invalid salary ranges: {invalid_range.sum()}")

    df.loc[invalid_range, "minimumSalary"] = pd.NA
    df.loc[invalid_range, "maximumSalary"] = pd.NA

    # ==================================================
    # 5. CREATE SALARY STATUS
    # ==================================================

    df["salary_status"] = "not_disclosed"

    df.loc[
        df["salary"].str.lower().eq("unpaid"),
        "salary_status"
    ] = "unpaid"

    valid_salary = (
        df["minimumSalary"].notna()
        & df["maximumSalary"].notna()
        & (df["minimumSalary"] > 0)
        & (df["maximumSalary"] > 0)
    )

    df.loc[valid_salary, "salary_status"] = "disclosed"

    # ==================================================
    # 6. CREATE A SINGLE SALARY TARGET
    # ==================================================

    df["salary_midpoint"] = pd.NA

    df.loc[valid_salary, "salary_midpoint"] = (
        df.loc[valid_salary, "minimumSalary"]
        + df.loc[valid_salary, "maximumSalary"]
    ) / 2

    # ==================================================
    # 7. CREATE EXPERIENCE MIDPOINT
    # ==================================================

    valid_experience = (
        df["minimumExperience"].notna()
        & df["maximumExperience"].notna()
        & (df["minimumExperience"] >= 0)
        & (df["maximumExperience"] >= df["minimumExperience"])
    )

    df["experience_midpoint"] = pd.NA

    df.loc[valid_experience, "experience_midpoint"] = (
        df.loc[valid_experience, "minimumExperience"]
        + df.loc[valid_experience, "maximumExperience"]
    ) / 2

    # ==================================================
    # 8. CREATE REMOTE FLAG
    # ==================================================

    df["is_remote"] = (
        df["location"]
        .str.lower()
        .str.contains("remote", na=False)
    )

    # ==================================================
    # 9. SAVE CLEAN DATASET
    # ==================================================

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ==================================================
    # 10. FINAL REPORT
    # ==================================================

    print("\n===== CLEANING COMPLETED =====")

    print(f"Final rows: {len(df)}")
    print(f"Final columns: {len(df.columns)}")

    print("\n===== SALARY STATUS =====")
    print(df["salary_status"].value_counts())

    print("\n===== SALARY MIDPOINT =====")

    salary_data = df.loc[
        df["salary_status"] == "disclosed",
        "salary_midpoint"
    ]

    print(salary_data.describe())

    print("\n===== EXPERIENCE MIDPOINT =====")

    print(
        df["experience_midpoint"]
        .dropna()
        .describe()
    )

    print("\n===== OUTPUT =====")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()