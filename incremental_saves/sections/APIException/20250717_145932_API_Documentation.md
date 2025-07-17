# API Documentation

*Generated: 2025-07-17 14:59:32*
*Component: APIException*

---

### API Documentation

#### POST /api/v1/perform_regression
Handles POST requests to perform Ordinary Least Squares regression analysis and returns the results.

| Parameter | Type | Description |
|-----------|------|-------------|
| dataset   | List[float] | The dataset to be analyzed for regression. |
| response  | JSON | The results of the regression analysis. |

```json
{
  "dataset": [1.0, 2.0, 3.0, 4.0]
}
```

---

#### POST /api/v1/get_descriptive_stats
Handles POST requests to compute and return descriptive statistics for a given dataset.

| Parameter | Type | Description |
|-----------|------|-------------|
| dataset   | List[float] | The dataset for which descriptive statistics are to be computed. |
| response  | JSON | The computed descriptive statistics. |

```json
{
  "dataset": [1.0, 2.0, 3.0, 4.0]
}
```

---

#### POST /api/v1/get_confidence_interval
Handles HTTP POST requests to calculate and return the confidence interval for a given dataset.

| Parameter | Type | Description |
|-----------|------|-------------|
| dataset   | List[float] | The dataset for which the confidence interval is to be calculated. |
| response  | Tuple[float, float] | The lower and upper bounds of the confidence interval. |

```json
{
  "dataset": [1.0, 2.0, 3.0, 4.0]
}
```

---

#### POST /api/v1/get_z_scores
Handles HTTP POST requests to calculate z-scores for a given dataset.

| Parameter | Type | Description |
|-----------|------|-------------|
| dataset   | List[float] | The dataset for which z-scores are to be calculated. |
| response  | List[float] | The calculated z-scores for the dataset. |

```json
{
  "dataset": [1.0, 2.0, 3.0, 4.0]
}
```

---

#### POST /api/v1/calculate_loan_payment
Calculates the periodic payment required to amortize a loan based on interest rate, number of periods, and present value.

| Parameter      | Type   | Description |
|----------------|--------|-------------|
| rate           | float  | The interest rate per period. |
| num_periods    | int    | The total number of payment periods. |
| present_value   | float  | The present value or principal amount of the loan. |
| response       | float  | The calculated periodic payment. |

```json
{
  "rate": 0.05,
  "num_periods": 12,
  "present_value": 1000
}
```

---

### Exception Handling

#### APIException
The `APIException` is a custom exception class designed to handle errors that occur during API operations. It is essential for managing error responses and ensuring that clients receive meaningful feedback when issues arise.

> **Note:** The `APIException` class may inherit from the base `Exception` class, which serves as the foundational class for all built-in exceptions in Python.

#### DataError
`DataError` is a custom exception that handles exceptions related to data processing errors, providing specific context for error management.

> ⚠️ **Note:** Some dependencies could not be fully resolved. Documentation may be incomplete.

### Dependencies
- `super().__init__` - Used in the initialization of custom exceptions.

### Conclusion
This documentation provides a comprehensive overview of the API endpoints available for statistical analysis and loan calculations, along with the exception handling mechanisms in place. Each endpoint is designed to facilitate specific data processing tasks, ensuring that users can effectively interact with the API.