import os
import joblib
import numpy as np
import pandas as pd


MODEL_FILE = "models/salary_ridge_log_model.pkl"
PREPROCESSOR_FILE = "models/salary_log_preprocessor.pkl"
CALIBRATION_FILE = "models/salary_log_calibration.pkl"


def load_model():

    model = joblib.load(
        MODEL_FILE
    )

    preprocessor = joblib.load(
        PREPROCESSOR_FILE
    )

    calibration = joblib.load(
        CALIBRATION_FILE
    )

    return (
        model,
        preprocessor,
        calibration
    )


def predict_salary_range(
    title,
    location,
    tags_and_skills,
    experience_midpoint
):

    # ================================================
    # Load trained artifacts
    # ================================================

    model, preprocessor, calibration = load_model()

    # ================================================
    # Prepare input
    # ================================================

    input_data = pd.DataFrame([
        {
            "title": str(title).strip().lower(),

            "location": str(location)
            .strip()
            .lower(),

            "tagsAndSkills": str(tags_and_skills)
            .strip()
            .lower(),

            "experience_midpoint": (
                float(experience_midpoint)
                if experience_midpoint is not None
                else 0.0
            )
        }
    ])

    # ================================================
    # Transform features
    # ================================================

    transformed = preprocessor.transform(
        input_data
    )

    # ================================================
    # Predict log salary
    # ================================================

    predicted_log = model.predict(
        transformed
    )[0]

    # ================================================
    # Convert to salary
    # ================================================

    predicted_midpoint = np.expm1(
        predicted_log
    )

    # ================================================
    # Apply calibrated range
    # ================================================

    lower_error = calibration[
        "lower_error"
    ]

    upper_error = calibration[
        "upper_error"
    ]

    predicted_lower = np.expm1(
        predicted_log + lower_error
    )

    predicted_upper = np.expm1(
        predicted_log + upper_error
    )

    # ================================================
    # Safety checks
    # ================================================

    predicted_lower = max(
        0,
        predicted_lower
    )

    predicted_midpoint = max(
        0,
        predicted_midpoint
    )

    predicted_upper = max(
        predicted_midpoint,
        predicted_upper
    )

    # ================================================
    # Return result
    # ================================================

    return {
        "midpoint": round(
            predicted_midpoint
        ),

        "lower": round(
            predicted_lower
        ),

        "upper": round(
            predicted_upper
        ),

        "midpoint_lpa": round(
            predicted_midpoint / 100000,
            2
        ),

        "lower_lpa": round(
            predicted_lower / 100000,
            2
        ),

        "upper_lpa": round(
            predicted_upper / 100000,
            2
        ),

        "label": (
            "CareerSense Estimated Salary Range"
        )
    }


if __name__ == "__main__":

    result = predict_salary_range(
        title="Planning Engineer",
        location="Pune",
        tags_and_skills="planning engineering project management autocad",
        experience_midpoint=3.0
    )

    print("\n===== SALARY PREDICTION TEST =====")

    print(
        f"Estimated midpoint: "
        f"₹{result['midpoint']:,}"
    )

    print(
        f"Estimated range: "
        f"₹{result['lower']:,} - "
        f"₹{result['upper']:,}"
    )

    print(
        f"Estimated range: "
        f"₹{result['lower_lpa']} - "
        f"{result['upper_lpa']} LPA"
    )