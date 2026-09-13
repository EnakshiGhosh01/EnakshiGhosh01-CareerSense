import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


INPUT_FILE = "data/processed/jobs_cleaned.csv"

FEATURES = [
    "title",
    "location",
    "tagsAndSkills",
    "experience_midpoint"
]


def main():

    # ==================================================
    # 1. LOAD DATA
    # ==================================================

    print("Loading cleaned dataset...")

    df = pd.read_csv(INPUT_FILE)

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

    salary_df = salary_df[
        salary_df["salary_midpoint"] > 0
    ].copy()

    print(
        f"Salary records: {len(salary_df)}"
    )

    # ==================================================
    # 2. FEATURES
    # ==================================================

    X = salary_df[FEATURES].copy()

    y = salary_df["salary_midpoint"].astype(float)

    # Log target
    y_log = np.log1p(y)

    # ==================================================
    # 3. CLEAN TEXT
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
    # 4. TRAIN / CALIBRATION / TEST SPLIT
    # ==================================================

    (
        X_train,
        X_temp,
        y_train,
        y_temp
    ) = train_test_split(
        X,
        y_log,
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

    print(f"Training:    {len(X_train)}")
    print(f"Calibration: {len(X_calibration)}")
    print(f"Testing:     {len(X_test)}")

    # ==================================================
    # 5. PREPROCESSING
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

    print("\nFitting preprocessor...")

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
        f"Feature matrix: "
        f"{X_train_transformed.shape}"
    )

    # ==================================================
    # 6. TRAIN RIDGE
    # ==================================================

    print("\nTraining log-salary Ridge model...")

    model = Ridge(
        alpha=10.0
    )

    model.fit(
        X_train_transformed,
        y_train
    )

    # ==================================================
    # 7. CALIBRATION
    # ==================================================

    calibration_predictions_log = model.predict(
        X_calibration_transformed
    )

    calibration_errors = (
        y_calibration.values
        - calibration_predictions_log
    )

    lower_error = np.percentile(
        calibration_errors,
        15
    )

    upper_error = np.percentile(
        calibration_errors,
        85
    )

    print("\n===== CALIBRATION =====")

    print(
        f"Lower log-error: {lower_error:.4f}"
    )

    print(
        f"Upper log-error: {upper_error:.4f}"
    )

    # ==================================================
    # 8. TEST PREDICTIONS
    # ==================================================

    predictions_log = model.predict(
        X_test_transformed
    )

    predicted_midpoint = np.expm1(
        predictions_log
    )

    predicted_lower = np.expm1(
        predictions_log + lower_error
    )

    predicted_upper = np.expm1(
        predictions_log + upper_error
    )

    actual_salary = np.expm1(
        y_test.values
    )

    # ==================================================
    # 9. OVERALL METRICS
    # ==================================================

    mae = mean_absolute_error(
        actual_salary,
        predicted_midpoint
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual_salary,
            predicted_midpoint
        )
    )

    r2 = r2_score(
        actual_salary,
        predicted_midpoint
    )

    print("\n===== OVERALL TEST PERFORMANCE =====")

    print(f"MAE:  ₹{mae:,.2f}")
    print(f"RMSE: ₹{rmse:,.2f}")
    print(f"R²:   {r2:.4f}")

    # ==================================================
    # 10. SALARY RANGE PERFORMANCE
    # ==================================================

    actual_lower = salary_df.loc[
        X_test.index,
        "minimumSalary"
    ].values

    actual_upper = salary_df.loc[
        X_test.index,
        "maximumSalary"
    ].values

    # Midpoint falls inside predicted range
    midpoint_coverage = (
        (actual_salary >= predicted_lower)
        &
        (actual_salary <= predicted_upper)
    ).mean() * 100

    # Any overlap between predicted and actual range
    overlap = (
        (predicted_upper >= actual_lower)
        &
        (predicted_lower <= actual_upper)
    ).mean() * 100

    # Predicted range completely contains actual range
    containment = (
        (predicted_lower <= actual_lower)
        &
        (predicted_upper >= actual_upper)
    ).mean() * 100

    predicted_width = (
        predicted_upper - predicted_lower
    )

    actual_width = (
        actual_upper - actual_lower
    )

    print("\n===== RANGE PERFORMANCE =====")

    print(
        f"Midpoint coverage: "
        f"{midpoint_coverage:.2f}%"
    )

    print(
        f"Any overlap: "
        f"{overlap:.2f}%"
    )

    print(
        f"Full containment: "
        f"{containment:.2f}%"
    )

    print(
        f"Average predicted width: "
        f"₹{predicted_width.mean():,.0f}"
    )

    print(
        f"Average actual width: "
        f"₹{actual_width.mean():,.0f}"
    )

    # ==================================================
    # 11. PERFORMANCE BY SALARY BAND
    # ==================================================

    print("\n===== PERFORMANCE BY SALARY BAND =====")

    evaluation = pd.DataFrame({
        "actual": actual_salary,
        "predicted": predicted_midpoint
    })

    evaluation["salary_band"] = pd.cut(
        evaluation["actual"],
        bins=[
            0,
            300000,
            500000,
            1000000,
            2500000,
            np.inf
        ],
        labels=[
            "< ₹3L",
            "₹3L–₹5L",
            "₹5L–₹10L",
            "₹10L–₹25L",
            "> ₹25L"
        ]
    )

    for band, group in evaluation.groupby(
        "salary_band",
        observed=False
    ):

        if len(group) == 0:
            continue

        band_mae = mean_absolute_error(
            group["actual"],
            group["predicted"]
        )

        band_rmse = np.sqrt(
            mean_squared_error(
                group["actual"],
                group["predicted"]
            )
        )

        print(
            f"\n{band}"
        )

        print(
            f"Jobs: {len(group)}"
        )

        print(
            f"MAE: ₹{band_mae:,.0f}"
        )

        print(
            f"RMSE: ₹{band_rmse:,.0f}"
        )

    # ==================================================
    # 12. SAMPLE PREDICTIONS
    # ==================================================

    print("\n===== SAMPLE PREDICTIONS =====")

    sample = pd.DataFrame({
        "title": X_test["title"].values,
        "actual": actual_salary,
        "predicted": predicted_midpoint,
        "lower": predicted_lower,
        "upper": predicted_upper
    })

    for _, row in sample.head(10).iterrows():

        print(
            f"\nJob: {row['title']}"
        )

        print(
            f"Actual midpoint: "
            f"₹{row['actual']:,.0f}"
        )

        print(
            f"Predicted midpoint: "
            f"₹{row['predicted']:,.0f}"
        )

        print(
            f"Predicted range: "
            f"₹{row['lower']:,.0f} - "
            f"₹{row['upper']:,.0f}"
        )

    print(
        "\n===== FINAL EVALUATION COMPLETED ====="
    )


if __name__ == "__main__":
    main()