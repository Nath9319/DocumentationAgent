# API Documentation

*Generated: 2025-07-17 15:15:56*
*Component: Field*

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

#### CalculationError
Handles errors that occur during mathematical calculations, providing a specific exception for better error management.

- **Relationship**: Related to `APIException`.

#### DataService.get_series_from_file
Handles requests to retrieve a series of data from a specified file.

| Parameter | Type         | Description                                           |
|-----------|--------------|-------------------------------------------------------|
| file_path | str          | The path to the file from which to read the data.    |
| response  | DataFrame    | The data series retrieved from the file, formatted as a Pandas DataFrame. |

```json
{
  "file_path": "path/to/data.csv"
}
```

> **Note:** This endpoint utilizes the `pd.read_csv` function to read CSV files and convert them into Pandas DataFrames for data analysis. The `StringIO` class may also be used for in-memory string data operations, simulating file-like behavior.

---

#### DataService.get_series_from_sqlite
Handles requests to retrieve a series of data from a SQLite database.

| Parameter | Type         | Description                                           |
|-----------|--------------|-------------------------------------------------------|
| query     | str          | The SQL query to execute against the SQLite database. |
| response  | DataFrame    | The data series retrieved from the SQLite database, formatted as a Pandas DataFrame. |

```json
{
  "query": "SELECT * FROM my_table"
}
```

> **Note:** This endpoint is designed to facilitate the extraction of structured data from a SQLite database, leveraging the `get_dataframe_from_sqlite` utility to return the results as a Pandas DataFrame for analysis.

---

### Additional API Endpoints

#### POST /api/v1/calculate_std_deviation
Handles HTTP POST requests to calculate the standard deviation of a dataset provided by the client.

| Parameter | Type         | Description                                           |
|-----------|--------------|-------------------------------------------------------|
| data      | List[float]  | The dataset for which the standard deviation is to be calculated. |
| response  | float        | The calculated standard deviation of the dataset.     |

```json
{
  "data": [1.0, 2.0, 3.0, 4.0]
}
```

> **Note:** This endpoint processes the dataset to compute the standard deviation, which quantifies the amount of variation or dispersion in the dataset.

---

#### POST /api/v1/calculate_future_value
Calculates the future value of an investment based on user-defined parameters and returns the result.

| Parameter      | Type   | Description                                           |
|----------------|--------|-------------------------------------------------------|
| rate           | float  | The interest rate per period.                         |
| periods        | int    | The total number of periods for the investment.       |
| payment        | float  | The payment made each period.                         |
| present_value   | float  | The present value or initial investment amount.       |
| response       | float  | The calculated future value of the investment.        |

```json
{
  "rate": 0.05,
  "periods": 10,
  "payment": 100,
  "present_value": 1000
}
```

> **Note:** This endpoint computes the future value of an investment based on the specified interest rate and payment parameters.

---

#### POST /api/v1/calculate_present_value
Handles HTTP POST requests to calculate the present value of an investment based on user-provided financial parameters.

| Parameter      | Type   | Description                                           |
|----------------|--------|-------------------------------------------------------|
| rate           | float  | The interest rate per period.                         |
| num_periods    | int    | The total number of payment periods.                  |
| payment        | float  | The payment made each period.                         |
| future_value   | float  | The future value of the investment.                   |
| response       | float  | The calculated present value of the investment.       |

```json
{
  "rate": 0.05,
  "num_periods": 10,
  "payment": 100,
  "future_value": 1500
}
```

> **Note:** This endpoint computes the present value of an investment based on the specified financial parameters.

---

#### POST /api/v1/perform_ttest
Handles HTTP POST requests to perform an independent two-sample t-test on provided datasets.

| Parameter | Type         | Description                                           |
|-----------|--------------|-------------------------------------------------------|
| data1     | List[float]  | The first dataset for the t-test.                    |
| data2     | List[float]  | The second dataset for the t-test.                   |
| equal_var | bool         | Indicates whether to assume equal population variances. |
| response  | dict         | The results of the t-test, including t-statistic and p-value. |

```json
{
  "data1": [1.0, 2.0, 3.0],
  "data2": [4.0, 5.0, 6.0],
  "equal_var": true
}
```

> **Note:** This endpoint is designed to assess whether the means of two independent samples are significantly different from each other.

---

### Connected Components

#### LoanPaymentInput
Captures and validates input data for loan payment calculations, ensuring data integrity before processing.

#### PresentValueInput
Represents the input parameters required for calculating the present value in financial calculations.

#### ListInput
Encapsulates operations for manipulating and processing a list of numeric values.

#### TTestInput
Represents and validates the input data for conducting an independent t-test, ensuring that the samples are not identical.

#### MatrixInput
Facilitates matrix operations and validation within the application.

#### FutureValueInput
Encapsulates the input parameters required for calculating the future value of an investment.

#### RegressionInput
Represents the input variables for OLS regression analysis while ensuring the uniqueness of independent variables.