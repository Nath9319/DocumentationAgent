# File Summary

# 📌 Basic Information

## Title & Overview
**File Name:** `stats_service.py`  
**Overview:** This file contains the `StatsService` class, which is designed to perform statistical analysis on data retrieved from a SQLite database. It provides various statistical methods for computing metrics and performing tests on the data, leveraging external libraries like NumPy and SciPy.

## Purpose
The primary purpose of the `stats_service.py` file is to facilitate the extraction, manipulation, and analysis of data through statistical computations. It serves as a service layer that connects to a SQLite database, retrieves data, and performs various statistical analyses, providing insights that can inform decision-making processes.

## Scope
This file encompasses the implementation of statistical methods, including confidence intervals, correlation matrices, descriptive statistics, standard deviation calculations, Z-scores, t-tests, and OLS regression. It is intended for use in applications that require statistical analysis of data stored in SQLite databases.

---

# ⚙️ Technical or Functional Details

## Architecture / Design
The `StatsService` class is structured to manage the interaction with a SQLite database and perform statistical computations. It relies on the following components:
- **Database Connection:** Establishes a connection to the SQLite database using the provided `db_path`.
- **Data Retrieval:** Utilizes the `_load_data` method to fetch data from a specified table in the database.
- **Statistical Methods:** Implements various statistical functions to analyze the retrieved data.

## Features & Functions
- **calculate_confidence_interval(data: List[float], confidence_level: float) -> Tuple[float, float]:** Computes the confidence interval for a given list of numerical data points.
- **calculate_correlation_matrix() -> dict:** Calculates the Pearson correlation matrix for specified columns in a dataset.
- **calculate_descriptive_stats(numbers: list) -> dict:** Computes descriptive statistics including mean, median, mode, variance, and standard deviation.
- **calculate_standard_deviation(numbers: list) -> float:** Calculates the standard deviation of a list of numerical values.
- **calculate_z_scores(numbers: list) -> list:** Computes the Z-Scores for a given list of numbers.
- **perform_independent_ttest(sample1: Union[List[float], np.ndarray], sample2: Union[List[float], np.ndarray]) -> Tuple[float, float]:** Conducts an independent two-sample t-test.
- **perform_ols_regression() -> dict:** Performs Ordinary Least Squares regression and returns a summary of the regression analysis.
- **_load_data() -> pd.DataFrame:** Loads data from a specified SQLite database table into a pandas DataFrame.

## Requirements
- **Dependencies:** The file requires external libraries such as NumPy and SciPy for statistical calculations and pandas for data manipulation.
- **Data Inputs:** The `StatsService` class requires:
  - `db_path` (string): A valid path to an existing SQLite database file.
  - `table_name` (string): The name of a table within the database that contains the data for analysis.

---

# 🚀 Setup and Usage

## Installation Instructions
To use the `stats_service.py` file, ensure that the following libraries are installed in your Python environment:
```bash
pip install numpy scipy pandas
```

## Configuration Settings
Before utilizing the `StatsService`, configure the following parameters:
- `db_path`: Set this to the file path of your SQLite database.
- `table_name`: Specify the name of the table containing the data for analysis.

## Usage Guidelines
1. **Instantiate the `StatsService`:**
   ```python
   from app.services.stats_service import StatsService

   stats_service = StatsService(db_path='path/to/database.db', table_name='your_table_name')
   ```

2. **Load Data:**
   The data is automatically loaded when you call any statistical method that requires it.

3. **Perform Statistical Analysis:**
   Call the desired statistical method, for example:
   ```python
   confidence_interval = stats_service.calculate_confidence_interval(data=[1.0, 2.0, 3.0], confidence_level=0.95)
   correlation_matrix = stats_service.calculate_correlation_matrix()
   descriptive_stats = stats_service.calculate_descriptive_stats(numbers=[1, 2, 3, 4, 5])
   ```

By following these guidelines, you can effectively utilize the statistical analysis capabilities provided by the `stats_service.py` file.