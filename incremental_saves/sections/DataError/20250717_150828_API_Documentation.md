# API Documentation

*Generated: 2025-07-17 15:08:28*
*Component: DataError*

---

### API Documentation

#### POST /api/v1/perform_regression
Handles POST requests to perform Ordinary Least Squares regression analysis and returns the results.

| Parameter | Type         | Description                                           |
|-----------|--------------|-------------------------------------------------------|
| dataset   | List[float]  | The dataset to be analyzed for regression.           |
| response  | Dict[str, Any] | The results of the regression analysis, including coefficients and statistics. |

```json
{
  "dataset": [1.0, 2.0, 3.0, 4.0]
}
```

> **Note:** This endpoint is designed to facilitate the execution of regression analysis within a web application.

---

#### POST /api/v1/get_descriptive_stats
Handles POST requests to compute and return descriptive statistics for a given dataset.

| Parameter | Type         | Description                                           |
|-----------|--------------|-------------------------------------------------------|
| dataset   | List[float]  | The dataset for which descriptive statistics are to be computed. |
| response  | Dict[str, Any] | The computed descriptive statistics, such as mean, median, and standard deviation. |

```json
{
  "dataset": [1.0, 2.0, 3.0, 4.0]
}
```

> **Note:** This endpoint processes incoming data to provide statistical insights.

---

#### POST /api/v1/get_confidence_interval
Handles HTTP POST requests to calculate and return the confidence interval for a given dataset.

| Parameter         | Type         | Description                                           |
|-------------------|--------------|-------------------------------------------------------|
| dataset           | List[float]  | The dataset for which the confidence interval is to be calculated. |
| confidence_level  | float        | The desired confidence level (e.g., 0.95 for 95% confidence). |
| response          | Tuple[float, float] | The lower and upper bounds of the confidence interval. |

```json
{
  "dataset": [1.0, 2.0, 3.0, 4.0],
  "confidence_level": 0.95
}
```

> **Note:** This endpoint is designed to provide statistical confidence intervals based on the provided dataset.

---

#### POST /api/v1/get_z_scores
Handles HTTP POST requests to calculate z-scores for a given dataset.

| Parameter | Type         | Description                                           |
|-----------|--------------|-------------------------------------------------------|
| dataset   | List[float]  | The dataset for which z-scores are to be calculated. |
| response  | List[float]  | The calculated z-scores for the dataset.             |

```json
{
  "dataset": [1.0, 2.0, 3.0, 4.0]
}
```

> **Note:** This endpoint processes the dataset to compute z-scores, which indicate how many standard deviations an element is from the mean.

---

#### POST /api/v1/calculate_loan_payment
Calculates the periodic payment required to amortize a loan based on interest rate, number of periods, and present value.

| Parameter      | Type   | Description                                           |
|----------------|--------|-------------------------------------------------------|
| rate           | float  | The interest rate per period.                         |
| num_periods    | int    | The total number of payment periods.                  |
| present_value   | float  | The present value or principal amount of the loan.   |
| response       | float  | The calculated periodic payment amount.               |

```json
{
  "rate": 0.05,
  "num_periods": 60,
  "present_value": 10000
}
```

> **Note:** This endpoint computes the periodic payment necessary to repay the loan over the specified number of periods.

---

### Exception Handling

#### APIException
`APIException` is a custom exception class designed to handle errors that occur during API requests. It provides a structured way to manage exceptions and return meaningful error messages to the client.

- **Base Class**: Inherits from the built-in `Exception` class, allowing for custom error signaling.

#### DataError
`DataError` is a specific exception related to data processing errors, providing context for error management.

- **Relationship**: Related to `APIException` as a specific type of error that may be raised during API operations.

> **Note:** Some dependencies related to `DataError` could not be fully resolved, and documentation may be incomplete.

---

### Connected Components

#### module_code (app\api\v1\api.py)
The `module_code` serves as a central component within the FastAPI application, specifically designed to facilitate the routing of API requests. It utilizes the `APIRouter` to manage the endpoints effectively.

#### module_code (app\api\v1\endpoints\statistics.py)
The `module_code` serves as a central component within the `statistics.py` file, which is part of the API endpoints for the application. This module is responsible for defining and managing the API endpoints for retrieving and processing statistical data.

---

#### POST /api/v1/check_min_columns
Handles POST requests to validate the minimum number of columns in a dataset.

| Parameter | Type         | Description                                           |
|-----------|--------------|-------------------------------------------------------|
| dataset   | List[List[float]] | The dataset to be validated for minimum column count. |
| min_columns | int        | The minimum number of columns required.              |
| response  | Dict[str, Any] | A confirmation message indicating whether the dataset meets the minimum column requirement. |

```json
{
  "dataset": [[1.0, 2.0], [3.0, 4.0]],
  "min_columns": 2
}
```

> **Note:** This endpoint utilizes the `field_validator` utility to ensure that the dataset meets the specified minimum column criteria. If the dataset does not meet the requirement, a `ValueError` may be raised.

---