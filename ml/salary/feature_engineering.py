import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder


INPUT_FILE = "data/processed/jobs_cleaned.csv"


def main():

    # ==================================================
    # 1. LOAD CLEANED DATASET
    # ==================================================

    print("Loading cleaned dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Original rows: {len(df)}")

    # ==================================================
    # 2. KEEP ONLY DISCLOSED SALARIES
    # ==================================================

    salary_df = df[
        df["salary_status"] == "disclosed"
    ].copy()

    print(
        f"Rows with disclosed salary: "
        f"{len(salary_df)}"
    )

    # ==================================================
    # 3. SELECT FEATURES AND TARGET
    # ==================================================

    features = [
        "title",
        "location",
        "tagsAndSkills",
        "experience_midpoint"
    ]

    target = "salary_midpoint"

    salary_df = salary_df[
        features + [target]
    ].copy()

    # ==================================================
    # 4. REMOVE MISSING VALUES
    # ==================================================

    salary_df = salary_df.dropna(
        subset=[
            "title",
            "location",
            "tagsAndSkills",
            "experience_midpoint",
            target
        ]
    )

    print(
        f"Rows after removing missing values: "
        f"{len(salary_df)}"
    )

    # ==================================================
    # 5. CLEAN TEXT FEATURES
    # ==================================================

    text_columns = [
        "title",
        "location",
        "tagsAndSkills"
    ]

    for column in text_columns:

        salary_df[column] = (
            salary_df[column]
            .fillna("")
            .astype(str)
            .str.strip()
            .str.lower()
        )

    # ==================================================
    # 6. SEPARATE FEATURES AND TARGET
    # ==================================================

    X = salary_df[features]

    y = salary_df[target]

    print("\nFeature columns:")
    print(X.columns.tolist())

    print("\nTarget:")
    print(target)

    # ==================================================
    # 7. TRAIN / TEST SPLIT
    # ==================================================

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=42
    )

    print("\n===== TRAIN / TEST SPLIT =====")

    print(f"Training rows: {len(X_train)}")
    print(f"Testing rows: {len(X_test)}")

    # ==================================================
    # 8. CREATE PREPROCESSING PIPELINE
    # ==================================================

    preprocessor = ColumnTransformer(
        transformers=[

            # Job title → TF-IDF
            (
                "title_tfidf",
                TfidfVectorizer(
                    max_features=10000,
                    ngram_range=(1, 2),
                    min_df=2
                ),
                "title"
            ),

            # Skills → TF-IDF
            (
                "skills_tfidf",
                TfidfVectorizer(
                    max_features=20000,
                    ngram_range=(1, 2),
                    min_df=2
                ),
                "tagsAndSkills"
            ),

            # Location → One-hot encoding
            (
                "location_encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    min_frequency=5
                ),
                ["location"]
            ),

            # Experience → keep numeric
            (
                "experience",
                "passthrough",
                ["experience_midpoint"]
            )
        ]
    )

    # ==================================================
    # 9. FIT ONLY ON TRAINING DATA
    # ==================================================

    print("\nFitting preprocessing pipeline...")

    X_train_transformed = preprocessor.fit_transform(
        X_train
    )

    # Transform test data using
    # the already-fitted preprocessing
    X_test_transformed = preprocessor.transform(
        X_test
    )

    # ==================================================
    # 10. DISPLAY TRANSFORMED DATA
    # ==================================================

    print("\n===== TRANSFORMATION COMPLETED =====")

    print(
        f"Training matrix shape: "
        f"{X_train_transformed.shape}"
    )

    print(
        f"Testing matrix shape: "
        f"{X_test_transformed.shape}"
    )

    print(
        f"Training target shape: "
        f"{y_train.shape}"
    )

    print(
        f"Testing target shape: "
        f"{y_test.shape}"
    )

    # ==================================================
    # 11. FEATURE COUNT
    # ==================================================

    print("\n===== FEATURE INFORMATION =====")

    print(
        "Total transformed features:",
        X_train_transformed.shape[1]
    )

    # ==================================================
    # 12. END
    # ==================================================

    print("\n===== FEATURE ENGINEERING COMPLETED =====")


if __name__ == "__main__":
    main()