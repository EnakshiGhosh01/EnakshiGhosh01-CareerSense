import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.decomposition import TruncatedSVD
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


INPUT_FILE = "data/processed/jobs_cleaned.csv"


def main():

    # ==================================================
    # 1. LOAD DATA
    # ==================================================

    print("Loading cleaned dataset...")

    df = pd.read_csv(INPUT_FILE)

    print(f"Original rows: {len(df)}")

    # ==================================================
    # 2. KEEP DISCLOSED SALARIES
    # ==================================================

    salary_df = df[
        df["salary_status"] == "disclosed"
    ].copy()

    print(
        f"Rows with disclosed salary: "
        f"{len(salary_df)}"
    )

    # ==================================================
    # 3. SELECT FEATURES
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
    ].dropna().copy()

    # ==================================================
    # 4. CLEAN TEXT
    # ==================================================

    for column in [
        "title",
        "location",
        "tagsAndSkills"
    ]:

        salary_df[column] = (
            salary_df[column]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    X = salary_df[features]
    y = salary_df[target]

    # ==================================================
    # 5. TRAIN / TEST SPLIT
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
    # 6. TEXT + CATEGORICAL PREPROCESSING
    # ==================================================

    preprocessor = ColumnTransformer(
        transformers=[

            (
                "title_tfidf",
                TfidfVectorizer(
                    max_features=10000,
                    ngram_range=(1, 2),
                    min_df=2
                ),
                "title"
            ),

            (
                "skills_tfidf",
                TfidfVectorizer(
                    max_features=20000,
                    ngram_range=(1, 2),
                    min_df=2
                ),
                "tagsAndSkills"
            ),

            (
                "location_encoder",
                OneHotEncoder(
                    handle_unknown="ignore",
                    min_frequency=5
                ),
                ["location"]
            ),

            (
                "experience",
                "passthrough",
                ["experience_midpoint"]
            )
        ]
    )

    print("\nFitting preprocessing...")

    X_train_sparse = preprocessor.fit_transform(
        X_train
    )

    X_test_sparse = preprocessor.transform(
        X_test
    )

    print(
        f"Sparse training shape: "
        f"{X_train_sparse.shape}"
    )

    # ==================================================
    # 7. REDUCE DIMENSIONS
    # ==================================================

    print("\nApplying TruncatedSVD...")

    svd = TruncatedSVD(
        n_components=100,
        random_state=42
    )

    X_train_reduced = svd.fit_transform(
        X_train_sparse
    )

    X_test_reduced = svd.transform(
        X_test_sparse
    )

    print(
        f"Reduced training shape: "
        f"{X_train_reduced.shape}"
    )

    print(
        f"Reduced testing shape: "
        f"{X_test_reduced.shape}"
    )

    print(
        f"Explained variance: "
        f"{svd.explained_variance_ratio_.sum():.4f}"
    )

    # ==================================================
    # 8. RANDOM FOREST
    # ==================================================

    print("\n===== RANDOM FOREST =====")

    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=20,
        min_samples_leaf=3,
        random_state=42,
        n_jobs=-1
    )

    print("Training Random Forest...")

    model.fit(
        X_train_reduced,
        y_train
    )

    # ==================================================
    # 9. PREDICTIONS
    # ==================================================

    print("Generating predictions...")

    predictions = model.predict(
        X_test_reduced
    )

    # ==================================================
    # 10. EVALUATION
    # ==================================================

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = mean_squared_error(
        y_test,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y_test,
        predictions
    )

    print("\n===== RANDOM FOREST RESULTS =====")

    print(f"MAE:  ₹{mae:,.2f}")
    print(f"RMSE: ₹{rmse:,.2f}")
    print(f"R²:   {r2:.4f}")

    # ==================================================
    # 11. RIDGE REFERENCE
    # ==================================================

    print("\n===== RIDGE REFERENCE =====")

    print("Ridge MAE:  ₹305,285.76")
    print("Ridge RMSE: ₹628,526.42")
    print("Ridge R²:   0.5586")

    # ==================================================
    # 12. COMPARISON
    # ==================================================

    print("\n===== MODEL COMPARISON =====")

    print(
        f"Ridge MAE:         ₹305,285.76"
    )

    print(
        f"Random Forest MAE: ₹{mae:,.2f}"
    )

    if mae < 305285.76:

        improvement = (
            (305285.76 - mae)
            / 305285.76
        ) * 100

        print(
            f"Random Forest improves MAE by "
            f"{improvement:.2f}% over Ridge."
        )

    else:

        print(
            "Random Forest does not improve "
            "MAE over Ridge."
        )

    print("\n===== MODEL COMPARISON COMPLETED =====")


if __name__ == "__main__":
    main()