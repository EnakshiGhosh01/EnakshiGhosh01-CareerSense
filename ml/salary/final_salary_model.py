import os
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


INPUT_FILE = "data/processed/jobs_cleaned.csv"
MODEL_DIR = "models"

MODEL_FILE = os.path.join(
    MODEL_DIR,
    "salary_ridge_log_model.pkl"
)

PREPROCESSOR_FILE = os.path.join(
    MODEL_DIR,
    "salary_log_preprocessor.pkl"
)

CALIBRATION_FILE = os.path.join(
    MODEL_DIR,
    "salary_log_calibration.pkl"
)


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

    # Only impossible/non-positive salaries are removed.
    salary_df = salary_df[
        salary_df["salary_midpoint"] > 0
    ].copy()

    print(
        f"Salary records used: {len(salary_df)}"
    )

    # ==================================================
    # 2. FEATURES AND TARGET
    # ==================================================

    X = salary_df[FEATURES].copy()

    y = salary_df["salary_midpoint"].astype(float)

    # Log-transform the highly skewed salary target.
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
    # 4. THREE-WAY SPLIT
    #
    # 70% training
    # 15% calibration
    # 15% testing
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

    print(
        f"Training:    {len(X_train)}"
    )

    print(
        f"Calibration: {len(X_calibration)}"
    )

    print(
        f"Testing:     {len(X_test)}"
    )

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
    #
    # Residuals are calculated in log-salary space.
    #
    # 15th–85th percentile = 70% empirical interval.
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
        f"Lower log-error bound: "
        f"{lower_error:.4f}"
    )

    print(
        f"Upper log-error bound: "
        f"{upper_error:.4f}"
    )

    # ==================================================
    # 8. TEST PREDICTIONS
    # ==================================================

    test_predictions_log = model.predict(
        X_test_transformed
    )

    # Convert midpoint prediction back to rupees.
    predicted_midpoint = np.expm1(
        test_predictions_log
    )

    predicted_lower = np.expm1(
        test_predictions_log + lower_error
    )

    predicted_upper = np.expm1(
        test_predictions_log + upper_error
    )

    predicted_lower = np.maximum(
        predicted_lower,
        0
    )

    # ==================================================
    # 9. TEST METRICS
    # ==================================================

    actual_salary = np.expm1(
        y_test.values
    )

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

    print("\n===== TEST PERFORMANCE =====")

    print(
        f"MAE:  ₹{mae:,.2f}"
    )

    print(
        f"RMSE: ₹{rmse:,.2f}"
    )

    print(
        f"R²:   {r2:.4f}"
    )

    # ==================================================
    # 10. RANGE EVALUATION
    # ==================================================

    actual_lower = salary_df.loc[
        X_test.index,
        "minimumSalary"
    ].values

    actual_upper = salary_df.loc[
        X_test.index,
        "maximumSalary"
    ].values

    midpoint_inside = (
        (actual_salary >= predicted_lower)
        &
        (actual_salary <= predicted_upper)
    )

    midpoint_coverage = (
        midpoint_inside.mean() * 100
    )

    actual_range_overlap = (
        (predicted_upper >= actual_lower)
        &
        (predicted_lower <= actual_upper)
    )

    overlap_percentage = (
        actual_range_overlap.mean() * 100
    )

    full_containment = (
        (predicted_lower <= actual_lower)
        &
        (predicted_upper >= actual_upper)
    )

    containment_percentage = (
        full_containment.mean() * 100
    )

    predicted_width = (
        predicted_upper - predicted_lower
    )

    actual_width = (
        actual_upper - actual_lower
    )

    print("\n===== SALARY RANGE PERFORMANCE =====")

    print(
        f"Midpoint coverage: "
        f"{midpoint_coverage:.2f}%"
    )

    print(
        f"Any overlap with actual range: "
        f"{overlap_percentage:.2f}%"
    )

    print(
        f"Full containment: "
        f"{containment_percentage:.2f}%"
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
    # 11. SAVE MODEL
    # ==================================================

    os.makedirs(
        MODEL_DIR,
        exist_ok=True
    )

    joblib.dump(
        model,
        MODEL_FILE
    )

    joblib.dump(
        preprocessor,
        PREPROCESSOR_FILE
    )

    calibration_data = {
        "lower_error": lower_error,
        "upper_error": upper_error,
        "interval": "70%",
        "target_transform": "log1p"
    }

    joblib.dump(
        calibration_data,
        CALIBRATION_FILE
    )

    print("\n===== MODEL SAVED =====")

    print(
        f"Model:        {MODEL_FILE}"
    )

    print(
        f"Preprocessor: {PREPROCESSOR_FILE}"
    )

    print(
        f"Calibration:  {CALIBRATION_FILE}"
    )

    # ==================================================
    # 12. SAMPLE PREDICTIONS
    # ==================================================

    print("\n===== SAMPLE PREDICTIONS =====")

    for i in range(
        min(10, len(X_test))
    ):

        title = X_test.iloc[i]["title"]

        print(
            f"\nJob: {title}"
        )

        print(
            f"Estimated range: "
            f"₹{predicted_lower[i]:,.0f} - "
            f"₹{predicted_upper[i]:,.0f}"
        )

    print(
        "\n===== FINAL LOG-SALARY MODEL CREATED ====="
    )


if __name__ == "__main__":
    main()