import pandas as pd
import matplotlib.pyplot as plt


INPUT_FILE = "data/processed/jobs_cleaned.csv"


def main():

    # ==================================================
    # LOAD DATASET
    # ==================================================

    print("Loading cleaned dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Rows: {len(df)}")

    # ==================================================
    # 1. TOP 10 JOB TITLES
    # ==================================================

    top_titles = df["title"].value_counts().head(10)

    plt.figure(figsize=(10, 6))

    top_titles.sort_values().plot(
        kind="barh"
    )

    plt.title("Top 10 Job Titles")
    plt.xlabel("Number of Job Postings")
    plt.ylabel("Job Title")

    plt.tight_layout()
    plt.show()

    # ==================================================
    # 2. TOP 10 LOCATIONS
    # ==================================================

    top_locations = df["location"].value_counts().head(10)

    plt.figure(figsize=(10, 6))

    top_locations.sort_values().plot(
        kind="barh"
    )

    plt.title("Top 10 Job Locations")
    plt.xlabel("Number of Job Postings")
    plt.ylabel("Location")

    plt.tight_layout()
    plt.show()

    # ==================================================
    # 3. SALARY DISTRIBUTION
    # ==================================================

    salary = df.loc[
        df["salary_status"] == "disclosed",
        "salary_midpoint"
    ].dropna()

    plt.figure(figsize=(10, 6))

    plt.hist(
        salary,
        bins=50
    )

    plt.title("Salary Distribution")
    plt.xlabel("Annual Salary (₹)")
    plt.ylabel("Number of Jobs")

    plt.tight_layout()
    plt.show()

    # ==================================================
    # 4. SALARY VS EXPERIENCE
    # ==================================================

    salary_experience = (
        df[df["salary_status"] == "disclosed"]
        .dropna(
            subset=[
                "experience_midpoint",
                "salary_midpoint"
            ]
        )
        .groupby("experience_midpoint")["salary_midpoint"]
        .median()
        .sort_index()
    )

    plt.figure(figsize=(10, 6))

    plt.plot(
        salary_experience.index,
        salary_experience.values,
        marker="o"
    )

    plt.title("Median Salary vs Experience")
    plt.xlabel("Experience (Years)")
    plt.ylabel("Median Annual Salary (₹)")

    plt.tight_layout()
    plt.show()

    # ==================================================
    # 5. TOP-PAYING JOB TITLES
    # ==================================================

    title_salary = (
        df[df["salary_status"] == "disclosed"]
        .groupby("title")["salary_midpoint"]
        .agg(["count", "median"])
    )

    # Avoid titles with too few salary records.
    title_salary = title_salary[
        title_salary["count"] >= 10
    ]

    top_paying_titles = (
        title_salary
        .sort_values("median", ascending=False)
        .head(10)
    )

    plt.figure(figsize=(10, 6))

    top_paying_titles["median"].sort_values().plot(
        kind="barh"
    )

    plt.title("Top 10 Job Titles by Median Salary")
    plt.xlabel("Median Annual Salary (₹)")
    plt.ylabel("Job Title")

    plt.tight_layout()
    plt.show()

    # ==================================================
    # 6. REMOTE VS NON-REMOTE
    # ==================================================

    remote_counts = df["is_remote"].map({
        True: "Remote",
        False: "Non-Remote"
    }).value_counts()

    plt.figure(figsize=(7, 7))

    plt.pie(
        remote_counts.values,
        labels=remote_counts.index,
        autopct="%1.1f%%"
    )

    plt.title("Remote vs Non-Remote Jobs")

    plt.show()

    # ==================================================
    # END
    # ==================================================

    print("\n===== VISUALIZATION COMPLETED =====")


if __name__ == "__main__":
    main()