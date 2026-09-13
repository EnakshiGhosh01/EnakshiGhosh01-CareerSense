import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


INPUT_FILE = "data/processed/jobs_cleaned.csv"


def main():

    # ==================================================
    # 1. LOAD DATA
    # ==================================================

    print("Loading cleaned dataset...")

    df = pd.read_csv(INPUT_FILE)

    # ==================================================
    # 2. KEEP VALID SALARY RANGES
    # ==================================================

    salary_df = df[
        df["salary_status"] == "disclosed"
    ].copy()

    salary_df = salary_df.dropna(
        subset=[
            "minimumSalary",
            "maximumSalary",
            "title",
            "location",
            "tagsAndSkills",
            "experience_midpoint"
        ]
    )

    salary_df = salary_df[
        (salary_df["minimumSalary"] > 0)
        & (salary_df["maximumSalary"] > 0)
        & (
            salary_df["maximumSalary"]
            >= salary_df["minimumSalary"]
        )
    ].copy()

    print(
        f"Rows available: {len(salary_df)}"
    )

    # ==================================================
    # 3. FEATURES AND TARGETS
    # ==================================================

    features = [
        "title",
        "location",
        "tagsAndSkills",
        "experience_midpoint"
    ]

    X = salary_df[features].copy()

    y_lower = salary_df["minimumSalary"]
    y_upper = salary_df["maximumSalary"]

    # ==================================================
    # 4. CLEAN TEXT
    # ==================================================

    for column in [
        "title",
        "location",
        "tagsAndSkills"
    ]:

        X[column] = (
            X[column]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    # ==================================================
    # 5. TRAIN / TEST SPLIT
    # ==================================================

    (
        X_train,
        X_test,
        y_lower_train,
        y_lower_test,
        y_upper_train,
        y_upper_test
    ) = train_test_split(
        X,
        y_lower,
        y_upper,
        test_size=0.20,
        random_state=42
    )

    # ==================================================
    # 6. PREPROCESSING
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

    X_train_transformed = preprocessor.fit_transform(
        X_train
    )

    X_test_transformed = preprocessor.transform(
        X_test
    )

    # ==================================================
    # 7. TRAIN LOWER MODEL
    # ==================================================

    print("Training lower salary model...")

    lower_model = Ridge(
        alpha=10.0
    )

    lower_model.fit(
        X_train_transformed,
        y_lower_train
    )

    lower_predictions = lower_model.predict(
        X_test_transformed
    )

    # ==================================================
    # 8. TRAIN UPPER MODEL
    # ==================================================

    print("Training upper salary model...")

    upper_model = Ridge(
        alpha=10.0
    )

    upper_model.fit(
        X_train_transformed,
        y_upper_train
    )

    upper_predictions = upper_model.predict(
        X_test_transformed
    )

    # ==================================================
    # 9. BASIC MODEL METRICS
    # ==================================================

    lower_mae = mean_absolute_error(
        y_lower_test,
        lower_predictions
    )

    lower_rmse = mean_squared_error(
        y_lower_test,
        lower_predictions
    ) ** 0.5

    lower_r2 = r2_score(
        y_lower_test,
        lower_predictions
    )

    upper_mae = mean_absolute_error(
        y_upper_test,
        upper_predictions
    )

    upper_rmse = mean_squared_error(
        y_upper_test,
        upper_predictions
    ) ** 0.5

    upper_r2 = r2_score(
        y_upper_test,
        upper_predictions
    )

    print("\n===== MODEL METRICS =====")

    print("\nLower salary:")
    print(f"MAE:  ₹{lower_mae:,.2f}")
    print(f"RMSE: ₹{lower_rmse:,.2f}")
    print(f"R²:   {lower_r2:.4f}")

    print("\nUpper salary:")
    print(f"MAE:  ₹{upper_mae:,.2f}")
    print(f"RMSE: ₹{upper_rmse:,.2f}")
    print(f"R²:   {upper_r2:.4f}")

    # ==================================================
    # 10. CORRECT INVALID RANGES
    # ==================================================

    predicted_lower = pd.Series(
        lower_predictions,
        index=X_test.index
    )

    predicted_upper = pd.Series(
        upper_predictions,
        index=X_test.index
    )

    invalid = (
        predicted_lower > predicted_upper
    )

    print("\n===== RANGE VALIDATION =====")

    print(
        f"Invalid ranges: {invalid.sum()}"
    )

    print(
        f"Invalid percentage: "
        f"{invalid.mean() * 100:.2f}%"
    )

    # Make every predicted range logically valid.
    final_lower = pd.concat(
        [predicted_lower, predicted_upper],
        axis=1
    ).min(axis=1)

    final_upper = pd.concat(
        [predicted_lower, predicted_upper],
        axis=1
    ).max(axis=1)

    # ==================================================
    # 11. RANGE OVERLAP
    # ==================================================

    actual_lower = y_lower_test
    actual_upper = y_upper_test

    # Amount of overlap between actual and predicted range.
    overlap_lower = pd.concat(
        [actual_lower, final_lower],
        axis=1
    ).max(axis=1)

    overlap_upper = pd.concat(
        [actual_upper, final_upper],
        axis=1
    ).min(axis=1)

    overlap = (
        overlap_upper - overlap_lower
    ).clip(lower=0)

    actual_width = (
        actual_upper - actual_lower
    )

    predicted_width = (
        final_upper - final_lower
    )

    # Percentage of actual range covered by
    # the predicted range.
    coverage = (
        overlap / actual_width
    )

    print("\n===== RANGE OVERLAP =====")

    print(
        f"Average actual-range coverage: "
        f"{coverage.mean() * 100:.2f}%"
    )

    print(
        f"Ranges with any overlap: "
        f"{(overlap > 0).mean() * 100:.2f}%"
    )

    # ==================================================
    # 12. CONTAINMENT
    # ==================================================

    # Does the predicted range completely contain
    # the actual range?

    contains_actual = (
        (final_lower <= actual_lower)
        & (final_upper >= actual_upper)
    )

    print("\n===== RANGE CONTAINMENT =====")

    print(
        f"Predicted range fully contains "
        f"actual range: "
        f"{contains_actual.mean() * 100:.2f}%"
    )

    # ==================================================
    # 13. RANGE WIDTH
    # ==================================================

    print("\n===== RANGE WIDTH =====")

    print(
        f"Average actual range width: "
        f"₹{actual_width.mean():,.2f}"
    )

    print(
        f"Average predicted range width: "
        f"₹{predicted_width.mean():,.2f}"
    )

    # ==================================================
    # 14. SAMPLE PREDICTIONS
    # ==================================================

    print("\n===== SAMPLE PREDICTIONS =====")

    sample = pd.DataFrame({
        "title": X_test["title"],
        "actual_lower": actual_lower,
        "actual_upper": actual_upper,
        "predicted_lower": final_lower,
        "predicted_upper": final_upper,
        "coverage": coverage
    }).head(10)

    for _, row in sample.iterrows():

        print(
            f"\nJob: {row['title']}"
        )

        print(
            f"Actual: "
            f"₹{row['actual_lower']:,.0f} - "
            f"₹{row['actual_upper']:,.0f}"
        )

        print(
            f"Predicted: "
            f"₹{row['predicted_lower']:,.0f} - "
            f"₹{row['predicted_upper']:,.0f}"
        )

        print(
            f"Actual range coverage: "
            f"{row['coverage'] * 100:.1f}%"
        )

    # ==================================================
    # END
    # ==================================================

    print(
        "\n===== RANGE EVALUATION COMPLETED ====="
    )


if __name__ == "__main__":
    main()