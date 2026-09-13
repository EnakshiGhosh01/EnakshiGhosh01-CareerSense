import numpy as np
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

    print(f"Original rows: {len(df)}")

    # ==================================================
    # 2. KEEP DISCLOSED SALARIES
    # ==================================================

    salary_df = df[
        df["salary_status"] == "disclosed"
    ].copy()

    salary_df = salary_df.dropna(
        subset=[
            "title",
            "location",
            "tagsAndSkills",
            "experience_midpoint",
            "salary_midpoint"
        ]
    )

    print(
        f"Rows available: {len(salary_df)}"
    )

    # ==================================================
    # 3. FEATURES AND TARGET
    # ==================================================

    features = [
        "title",
        "location",
        "tagsAndSkills",
        "experience_midpoint"
    ]

    X = salary_df[features].copy()

    y = salary_df["salary_midpoint"].copy()

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
    # 5. THREE-WAY SPLIT
    #
    # Training:
    # Used to train the model and fit TF-IDF.
    #
    # Calibration:
    # Used to measure typical prediction error
    # and create the salary range.
    #
    # Test:
    # Used only for final evaluation.
    # ==================================================

    (
        X_train,
        X_temp,
        y_train,
        y_temp
    ) = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=42
    )

    (
        X_calibration,
        X_test,
        y_calibration,
        y_test
    ) = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=42
    )

    print("\n===== DATA SPLIT =====")

    print(f"Training rows:    {len(X_train)}")
    print(f"Calibration rows: {len(X_calibration)}")
    print(f"Testing rows:     {len(X_test)}")

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

    X_calibration_transformed = (
        preprocessor.transform(X_calibration)
    )

    X_test_transformed = preprocessor.transform(
        X_test
    )

    print(
        f"Training matrix: "
        f"{X_train_transformed.shape}"
    )

    print(
        f"Calibration matrix: "
        f"{X_calibration_transformed.shape}"
    )

    print(
        f"Testing matrix: "
        f"{X_test_transformed.shape}"
    )

    # ==================================================
    # 7. TRAIN RIDGE MODEL
    # ==================================================

    print("\n===== TRAINING RIDGE MODEL =====")

    model = Ridge(
        alpha=10.0
    )

    model.fit(
        X_train_transformed,
        y_train
    )

    # ==================================================
    # 8. CALIBRATION PREDICTIONS
    # ==================================================

    calibration_predictions = model.predict(
        X_calibration_transformed
    )

    calibration_errors = (
        y_calibration.values
        - calibration_predictions
    )

    # ==================================================
    # 9. CREATE PREDICTION RANGE
    #
    # We use the 10th and 90th percentile of
    # calibration errors.
    #
    # This creates an approximately 80% empirical
    # prediction interval.
    # ==================================================

    lower_error = np.percentile(
        calibration_errors,
        10
    )

    upper_error = np.percentile(
        calibration_errors,
        90
    )

    print("\n===== CALIBRATION =====")

    print(
        f"10th percentile error: "
        f"₹{lower_error:,.2f}"
    )

    print(
        f"90th percentile error: "
        f"₹{upper_error:,.2f}"
    )

    # ==================================================
    # 10. TEST PREDICTIONS
    # ==================================================

    test_predictions = model.predict(
        X_test_transformed
    )

    # ==================================================
    # 11. MODEL PERFORMANCE
    # ==================================================

    mae = mean_absolute_error(
        y_test,
        test_predictions
    )

    rmse = mean_squared_error(
        y_test,
        test_predictions
    ) ** 0.5

    r2 = r2_score(
        y_test,
        test_predictions
    )

    print("\n===== RIDGE TEST PERFORMANCE =====")

    print(f"MAE:  ₹{mae:,.2f}")
    print(f"RMSE: ₹{rmse:,.2f}")
    print(f"R²:   {r2:.4f}")

    # ==================================================
    # 12. CREATE SALARY RANGES
    # ==================================================

    predicted_lower = (
        test_predictions
        + lower_error
    )

    predicted_upper = (
        test_predictions
        + upper_error
    )

    # Salary cannot be negative.
    predicted_lower = np.maximum(
        predicted_lower,
        0
    )

    # ==================================================
    # 13. RANGE WIDTH
    # ==================================================

    actual_lower = salary_df.loc[
        X_test.index,
        "minimumSalary"
    ].values

    actual_upper = salary_df.loc[
        X_test.index,
        "maximumSalary"
    ].values

    actual_midpoint = y_test.values

    # ==================================================
    # 14. RANGE COVERAGE
    # ==================================================

    # Check whether the actual salary midpoint
    # falls inside the predicted range.

    midpoint_inside = (
        (actual_midpoint >= predicted_lower)
        & (actual_midpoint <= predicted_upper)
    )

    midpoint_coverage = (
        midpoint_inside.mean() * 100
    )

    print("\n===== PREDICTION RANGE =====")

    print(
        f"Midpoint coverage: "
        f"{midpoint_coverage:.2f}%"
    )

    # ==================================================
    # 15. ACTUAL RANGE OVERLAP
    # ==================================================

    overlap_lower = np.maximum(
        actual_lower,
        predicted_lower
    )

    overlap_upper = np.minimum(
        actual_upper,
        predicted_upper
    )

    overlap = np.maximum(
        overlap_upper - overlap_lower,
        0
    )

    actual_width = (
        actual_upper - actual_lower
    )

    coverage = (
        overlap / actual_width
    )

    print(
        f"Average actual-range coverage: "
        f"{coverage.mean() * 100:.2f}%"
    )

    print(
        f"Ranges with any overlap: "
        f"{(overlap > 0).mean() * 100:.2f}%"
    )

    # ==================================================
    # 16. RANGE WIDTH
    # ==================================================

    predicted_width = (
        predicted_upper
        - predicted_lower
    )

    print("\n===== RANGE WIDTH =====")

    print(
        f"Average predicted range width: "
        f"₹{predicted_width.mean():,.2f}"
    )

    print(
        f"Average actual salary range width: "
        f"₹{actual_width.mean():,.2f}"
    )

    # ==================================================
    # 17. SAMPLE PREDICTIONS
    # ==================================================

    print("\n===== SAMPLE PREDICTIONS =====")

    sample_indices = X_test.index[:10]

    for index in sample_indices:

        position = X_test.index.get_loc(index)

        title = X_test.loc[
            index,
            "title"
        ]

        actual_min = actual_lower[position]
        actual_max = actual_upper[position]

        pred_min = predicted_lower[position]
        pred_max = predicted_upper[position]

        print(f"\nJob: {title}")

        print(
            f"Actual salary: "
            f"₹{actual_min:,.0f} - "
            f"₹{actual_max:,.0f}"
        )

        print(
            f"Predicted salary: "
            f"₹{pred_min:,.0f} - "
            f"₹{pred_max:,.0f}"
        )

    # ==================================================
    # END
    # ==================================================

    print(
        "\n===== SALARY RANGE RIDGE COMPLETED ====="
    )


if __name__ == "__main__":
    main()