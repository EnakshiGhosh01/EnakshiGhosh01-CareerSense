import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


INPUT_FILE = "data/processed/jobs_cleaned.csv"


def evaluate_model(name, y_true, predictions):

    mae = mean_absolute_error(
        y_true,
        predictions
    )

    rmse = mean_squared_error(
        y_true,
        predictions
    ) ** 0.5

    r2 = r2_score(
        y_true,
        predictions
    )

    print(f"\n===== {name} =====")
    print(f"MAE:  ₹{mae:,.2f}")
    print(f"RMSE: ₹{rmse:,.2f}")
    print(f"R²:   {r2:.4f}")

    return mae, rmse, r2


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

    # We need BOTH minimum and maximum salary.
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

    # Keep only valid positive salary ranges.
    salary_df = salary_df[
        (salary_df["minimumSalary"] > 0)
        & (salary_df["maximumSalary"] > 0)
        & (
            salary_df["maximumSalary"]
            >= salary_df["minimumSalary"]
        )
    ].copy()

    print(
        f"Rows available for range modeling: "
        f"{len(salary_df)}"
    )

    # ==================================================
    # 3. FEATURES
    # ==================================================

    features = [
        "title",
        "location",
        "tagsAndSkills",
        "experience_midpoint"
    ]

    X = salary_df[features]

    # Two targets
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

    print("\n===== TRAIN / TEST SPLIT =====")

    print(f"Training rows: {len(X_train)}")
    print(f"Testing rows: {len(X_test)}")

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

    print(
        f"Training matrix shape: "
        f"{X_train_transformed.shape}"
    )

    print(
        f"Testing matrix shape: "
        f"{X_test_transformed.shape}"
    )

    # ==================================================
    # 7. LOWER SALARY MODEL
    # ==================================================

    print("\nTraining lower salary model...")

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

    evaluate_model(
        "LOWER SALARY MODEL",
        y_lower_test,
        lower_predictions
    )

    # ==================================================
    # 8. UPPER SALARY MODEL
    # ==================================================

    print("\nTraining upper salary model...")

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

    evaluate_model(
        "UPPER SALARY MODEL",
        y_upper_test,
        upper_predictions
    )

    # ==================================================
    # 9. MAKE SURE RANGE IS VALID
    # ==================================================

    print("\n===== RANGE VALIDATION =====")

    # If the lower prediction is accidentally
    # greater than the upper prediction,
    # swap them for a valid range.

    predicted_lower = pd.Series(
        lower_predictions,
        index=X_test.index
    )

    predicted_upper = pd.Series(
        upper_predictions,
        index=X_test.index
    )

    invalid_ranges = (
        predicted_lower > predicted_upper
    )

    print(
        f"Invalid predicted ranges before correction: "
        f"{invalid_ranges.sum()}"
    )

    corrected_lower = predicted_lower.copy()
    corrected_upper = predicted_upper.copy()

    corrected_lower[invalid_ranges] = (
        predicted_upper[invalid_ranges]
    )

    corrected_upper[invalid_ranges] = (
        predicted_lower[invalid_ranges]
    )

    # ==================================================
    # 10. SHOW SAMPLE PREDICTIONS
    # ==================================================

    print("\n===== SAMPLE SALARY PREDICTIONS =====")

    samples = pd.DataFrame({
        "Job Title": X_test["title"].values[:10],
        "Actual Min": y_lower_test.values[:10],
        "Actual Max": y_upper_test.values[:10],
        "Predicted Min": corrected_lower.values[:10],
        "Predicted Max": corrected_upper.values[:10]
    })

    for _, row in samples.iterrows():

        print(
            f"\nJob: {row['Job Title']}"
        )

        print(
            f"Actual range: "
            f"₹{row['Actual Min']:,.0f} - "
            f"₹{row['Actual Max']:,.0f}"
        )

        print(
            f"Predicted range: "
            f"₹{row['Predicted Min']:,.0f} - "
            f"₹{row['Predicted Max']:,.0f}"
        )

    # ==================================================
    # 11. RANGE WIDTH
    # ==================================================

    actual_width = (
        y_upper_test.values
        - y_lower_test.values
    )

    predicted_width = (
        corrected_upper.values
        - corrected_lower.values
    )

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
    # END
    # ==================================================

    print("\n===== SALARY RANGE MODELING COMPLETED =====")


if __name__ == "__main__":
    main()