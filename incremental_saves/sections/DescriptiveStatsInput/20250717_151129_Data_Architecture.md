# Data Architecture

*Generated: 2025-07-17 15:11:29*
*Component: DescriptiveStatsInput*

---

# Data Architecture

This document outlines the data architecture, focusing on the `BaseModel` and its related data models. Each model is designed to facilitate specific operations and ensure data integrity during interactions with the database.

### BaseModel

The `BaseModel` serves as the foundational class for various data models, providing common functionalities and attributes necessary for database interactions. It encapsulates essential methods for data validation, serialization, and persistence, ensuring that all derived models maintain a consistent structure and behavior.

### SingleInput

| Column       | Type   | Constraints | Description                                         |
|-------------|--------|-------------|-----------------------------------------------------|
| id          | INT    | PRIMARY KEY | Unique identifier for each SingleInput instance.    |
| input_value | FLOAT  | NOT NULL    | The single numerical input value for calculations.   |

**Description:**
`SingleInput` is a model class designed to handle operations that require a single numerical input. It extends the functionality of the `BaseModel`, inheriting its properties and methods.

### DualInput

| Column       | Type   | Constraints | Description                                         |
|-------------|--------|-------------|-----------------------------------------------------|
| id          | INT    | PRIMARY KEY | Unique identifier for each DualInput instance.      |
| input_value1| FLOAT  | NOT NULL    | The first numerical input value for calculations.    |
| input_value2| FLOAT  | NOT NULL    | The second numerical input value for calculations.   |

**Description:**
`DualInput` facilitates operations that require two numerical inputs, extending the functionality of the `BaseModel`.

### LoanPaymentInput

| Column       | Type   | Constraints | Description                                         |
|-------------|--------|-------------|-----------------------------------------------------|
| id          | INT    | PRIMARY KEY | Unique identifier for each LoanPaymentInput instance.|
| principal   | FLOAT  | NOT NULL    | The principal amount of the loan.                   |
| interest_rate| FLOAT | NOT NULL    | The interest rate applicable to the loan.           |
| term        | INT    | NOT NULL    | The term of the loan in months.                     |

**Description:**
`LoanPaymentInput` captures and validates input data for loan payment calculations, ensuring data integrity before processing.

### PresentValueInput

| Column       | Type   | Constraints | Description                                         |
|-------------|--------|-------------|-----------------------------------------------------|
| id          | INT    | PRIMARY KEY | Unique identifier for each PresentValueInput instance.|
| future_value| FLOAT  | NOT NULL    | The future value to be discounted.                  |
| rate        | FLOAT  | NOT NULL    | The discount rate.                                  |
| periods     | INT    | NOT NULL    | The number of periods until payment.                |

**Description:**
`PresentValueInput` represents the input parameters required for calculating the present value in financial calculations.

### ListInput

| Column       | Type   | Constraints | Description                                         |
|-------------|--------|-------------|-----------------------------------------------------|
| id          | INT    | PRIMARY KEY | Unique identifier for each ListInput instance.      |
| values      | TEXT   | NOT NULL    | A comma-separated list of numeric values.           |

**Description:**
`ListInput` is designed to perform operations on a list of numbers, extending the functionality of the `BaseModel`.

### StdDevInput

| Column       | Type   | Constraints | Description                                         |
|-------------|--------|-------------|-----------------------------------------------------|
| id          | INT    | PRIMARY KEY | Unique identifier for each StdDevInput instance.    |
| dataset     | TEXT   | NOT NULL    | A comma-separated list of numeric values for std dev calculation. |

**Description:**
`StdDevInput` facilitates the calculation of the standard deviation of a dataset, inheriting from the `BaseModel`.

### DescriptiveStatsInput

| Column       | Type   | Constraints | Description                                         |
|-------------|--------|-------------|-----------------------------------------------------|
| id          | INT    | PRIMARY KEY | Unique identifier for each DescriptiveStatsInput instance.|
| dataset     | TEXT   | NOT NULL    | A comma-separated list of numeric values for descriptive statistics. |

**Description:**
`DescriptiveStatsInput` is designed to facilitate the calculation of descriptive statistics such as mean, median, and variance.

### ZScoreInput

| Column       | Type   | Constraints | Description                                         |
|-------------|--------|-------------|-----------------------------------------------------|
| id          | INT    | PRIMARY KEY | Unique identifier for each ZScoreInput instance.    |
| value       | FLOAT  | NOT NULL    | The value for which the Z-score is calculated.      |
| mean        | FLOAT  | NOT NULL    | The mean of the dataset.                            |
| std_dev     | FLOAT  | NOT NULL    | The standard deviation of the dataset.              |

**Description:**
`ZScoreInput` is designed to handle inputs related to the calculation of Z-scores.

### ConfidenceIntervalInput

| Column       | Type   | Constraints | Description                                         |
|-------------|--------|-------------|-----------------------------------------------------|
| id          | INT    | PRIMARY KEY | Unique identifier for each ConfidenceIntervalInput instance.|
| sample_mean | FLOAT  | NOT NULL    | The mean of the sample.                             |
| std_dev     | FLOAT  | NOT NULL    | The standard deviation of the sample.               |
| sample_size | INT    | NOT NULL    | The size of the sample.                             |

**Description:**
`ConfidenceIntervalInput` facilitates the calculation of confidence intervals within the application.

### CorrelationInput

| Column       | Type   | Constraints | Description                                         |
|-------------|--------|-------------|-----------------------------------------------------|
| id          | INT    | PRIMARY KEY | Unique identifier for each CorrelationInput instance.|
| dataset     | TEXT   | NOT NULL    | A comma-separated list of numeric values for correlation analysis. |

**Description:**
`CorrelationInput` represents input data for generating a correlation matrix, ensuring at least two columns are specified.

### TTestInput

| Column       | Type   | Constraints | Description                                         |
|-------------|--------|-------------|-----------------------------------------------------|
| id          | INT    | PRIMARY KEY | Unique identifier for each TTestInput instance.     |
| sample1     | TEXT   | NOT NULL    | A comma-separated list of values for the first sample. |
| sample2     | TEXT   | NOT NULL    | A comma-separated list of values for the second sample. |

**Description:**
`TTestInput` represents and validates the input data for conducting an independent t-test.

### MatrixInput

| Column       | Type   | Constraints | Description                                         |
|-------------|--------|-------------|-----------------------------------------------------|
| id          | INT    | PRIMARY KEY | Unique identifier for each MatrixInput instance.    |
| matrix_data | TEXT   | NOT NULL    | A serialized representation of the matrix.          |

**Description:**
`MatrixInput` facilitates matrix operations and validation within the application.

### FutureValueInput

| Column       | Type   | Constraints | Description                                         |
|-------------|--------|-------------|-----------------------------------------------------|
| id          | INT    | PRIMARY KEY | Unique identifier for each FutureValueInput instance.|
| present_value| FLOAT | NOT NULL    | The present value to be compounded.                 |
| rate        | FLOAT  | NOT NULL    | The interest rate for compounding.                  |
| periods     | INT    | NOT NULL    | The number of periods for compounding.              |

**Description:**
`FutureValueInput` encapsulates the input parameters required for calculating the future value of an investment.

### RegressionInput

| Column       | Type   | Constraints | Description                                         |
|-------------|--------|-------------|-----------------------------------------------------|
| id          | INT    | PRIMARY KEY | Unique identifier for each RegressionInput instance.|
| dependent_var| TEXT  | NOT NULL    | The dependent variable for regression analysis.     |
| independent_vars| TEXT| NOT NULL   | A comma-separated list of independent variables.    |

**Description:**
`RegressionInput` represents the input variables for Ordinary Least Squares (OLS) regression analysis, ensuring the uniqueness of independent variables.

### DataService

The `DataService` is responsible for managing database interactions, including data retrieval, storage, and manipulation. It utilizes various utilities and functions to facilitate these operations.

#### Database Connections

- **sqlite3.connect**: This utility establishes and manages a connection to a SQLite database, allowing for SQL command execution and data management.

```sql
sqlite3.connect(database: str, timeout: float = 5.0, detect_types: int = 0, isolation_level: Optional[str] = None, check_same_thread: bool = True, factory: Optional[Type[Connection]] = None, cache...)
```

#### Data Retrieval

- **pd.read_sql_query**: This function executes SQL queries against a database and returns the results as a Pandas DataFrame.

```sql
pd.read_sql_query(sql: str, con, **kwargs) -> DataFrame
```

- **get_dataframe_from_sqlite**: This utility retrieves data from a SQLite database and returns it as a Pandas DataFrame for analysis.

#### Data Input from Files

- **pd.read_csv**: This function reads CSV files and converts them into Pandas DataFrames for data analysis.

```sql
pd.read_csv(filepath_or_buffer: Union[str, Path, IO], sep: str = ',', header: Union[int, List[int], None] = 'infer', ...) -> DataFrame
```

- **StringIO**: This utility facilitates efficient reading and writing of string data in memory, simulating file-like operations.

The `DataService` integrates these components to ensure efficient data handling and processing, maintaining data integrity and supporting the various input models defined above.