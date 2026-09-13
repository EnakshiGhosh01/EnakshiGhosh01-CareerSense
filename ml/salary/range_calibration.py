import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


INPUT_FILE = "data/processed/jobs_cleaned.csv"


def calculate_metrics(
    actual_midpoint,
    predictions,
    actual_lower,
    actual_upper,
    lower_error,
    upper_error
):

    # Create predicted range
    predicted_lower = np.maximum(
        predictions + lower_error,
        0
    )

    predicted_upper = np.maximum(
        predictions + upper_error,
        0
    )

    # Make sure lower <= upper
    final_lower = np.minimum(
        predicted_lower,
        predicted_upper
    )

    final_upper = np.maximum(
        predicted_lower,
        predicted_upper
    )

    # --------------------------------------------------
    # Midpoint coverage
    # --------------------------------------------------

    midpoint_inside = (
        (actual_midpoint >= final_lower)
        & (actual_midpoint <= final_upper)
    )

    midpoint_coverage = (
        midpoint_inside.mean() * 100
    )

    # --------------------------------------------------
    # Range overlap
    # --------------------------------------------------

    overlap_lower = np.maximum(
        actual_lower,
        final_lower
    )

    overlap_upper = np.minimum(
        actual_upper,
        final_upper
    )

    overlap = np.maximum(
        overlap_upper - overlap_lower,
        0
    )

    actual_width = (
        actual_upper - actual_lower
    )

    # Only calculate coverage where the actual
    # range has non-zero width.
    valid_width = actual_width > 0

    range_coverage = np.mean(
        overlap[valid_width]
        / actual_width[valid_width]
    ) * 100

    any_overlap = (
        overlap > 0
    ).mean() * 100

    # --------------------------------------------------
    # Range width
    # --------------------------------------------------

    predicted_width = (
        final_upper - final_lower
    )

    average_predicted_width = (
        predicted_width.mean()
    )

    average_actual_width = (
        actual_width.mean()
    )

    # --------------------------------------------------
    # Containment
    # --------------------------------------------------

    contains_actual = (
        (final_lower <= actual_lower)
        & (final_upper >= actual_upper)
    )

    containment = (
        contains_actual.mean() * 100
    )

    return {
        "midpoint_coverage": midpoint_coverage,
        "range_coverage": range_coverage,
        "any_overlap": any_overlap,
        "containment": containment,
        "predicted_width": average_predicted_width,
        "actual_width": average_actual_width
    }


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
            "salary_midpoint",
            "minimumSalary",
            "maximumSalary"
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
    # 2. FEATURES
    # ==================================================

    features = [
        "title",
        "location",
        "tagsAndSkills",
        "experience_midpoint"
    ]

    X = salary_df[features].copy()

    y = salary_df["salary_midpoint"].copy()

    actual_lower = salary_df[
        "minimumSalary"
    ].copy()

    actual_upper = salary_df[
        "maximumSalary"
    ].copy()

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
    # ==================================================

    (
        X_train,
        X_temp,
        y_train,
        y_temp,
        lower_train,
        lower_temp,
        upper_train,
        upper_temp
    ) = train_test_split(
        X,
        y,
        actual_lower,
        actual_upper,
        test_size=0.30,
        random_state=42
    )

    (
        X_calibration,
        X_test,
        y_calibration,
        y_test,
        lower_calibration,
        lower_test,
        upper_calibration,
        upper_test
    ) = train_test_split(
        X_temp,
        y_temp,
        lower_temp,
        upper_temp,
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
        f"Feature matrix: "
        f"{X_train_transformed.shape}"
    )

    # ==================================================
    # 6. TRAIN RIDGE
    # ==================================================

    print("\nTraining Ridge model...")

    model = Ridge(
        alpha=10.0
    )

    model.fit(
        X_train_transformed,
        y_train
    )

    # ==================================================
    # 7. CALIBRATION PREDICTIONS
    # ==================================================

    calibration_predictions = model.predict(
        X_calibration_transformed
    )

    calibration_errors = (
        y_calibration.values
        - calibration_predictions
    )

    # ==================================================
    # 8. TEST PREDICTIONS
    # ==================================================

    test_predictions = model.predict(
        X_test_transformed
    )

    # ==================================================
    # 9. MODEL PERFORMANCE
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

    print("\n===== RIDGE MODEL =====")

    print(f"MAE:  ₹{mae:,.2f}")
    print(f"RMSE: ₹{rmse:,.2f}")
    print(f"R²:   {r2:.4f}")

    # ==================================================
    # 10. TEST DIFFERENT RANGE SIZES
    # ==================================================

    # We test several empirical intervals.
    #
    # 50% interval = 25th to 75th percentile
    # 60% interval = 20th to 80th percentile
    # 70% interval = 15th to 85th percentile
    # 80% interval = 10th to 90th percentile

    intervals = [
        ("50%", 25, 75),
        ("60%", 20, 80),
        ("70%", 15, 85),
        ("80%", 10, 90)
    ]

    results = []

    print("\n===== RANGE CALIBRATION =====")

    for name, lower_percentile, upper_percentile in intervals:

        lower_error = np.percentile(
            calibration_errors,
            lower_percentile
        )

        upper_error = np.percentile(
            calibration_errors,
            upper_percentile
        )

        metrics = calculate_metrics(
            y_test.values,
            test_predictions,
            lower_test.values,
            upper_test.values,
            lower_error,
            upper_error
        )

        results.append({
            "Interval": name,
            "Lower Error": lower_error,
            "Upper Error": upper_error,
            **metrics
        })

        print(f"\n--- {name} interval ---")

        print(
            f"Error bounds: "
            f"₹{lower_error:,.0f} "
            f"to "
            f"₹{upper_error:,.0f}"
        )

        print(
            f"Midpoint coverage: "
            f"{metrics['midpoint_coverage']:.2f}%"
        )

        print(
            f"Average range coverage: "
            f"{metrics['range_coverage']:.2f}%"
        )

        print(
            f"Any range overlap: "
            f"{metrics['any_overlap']:.2f}%"
        )

        print(
            f"Full containment: "
            f"{metrics['containment']:.2f}%"
        )

        print(
            f"Average predicted width: "
            f"₹{metrics['predicted_width']:,.0f}"
        )

        print(
            f"Average actual width: "
            f"₹{metrics['actual_width']:,.0f}"
        )

    # ==================================================
    # 11. COMPARISON TABLE
    # ==================================================

    print("\n===== COMPARISON TABLE =====")

    results_df = pd.DataFrame(results)

    display_columns = [
        "Interval",
        "midpoint_coverage",
        "range_coverage",
        "any_overlap",
        "containment",
        "predicted_width",
        "actual_width"
    ]

    print(
        results_df[
            display_columns
        ].to_string(index=False)
    )

    # ==================================================
    # END
    # ==================================================

    print(
        "\n===== RANGE CALIBRATION COMPLETED ====="
    )


if __name__ == "__main__":
    main()