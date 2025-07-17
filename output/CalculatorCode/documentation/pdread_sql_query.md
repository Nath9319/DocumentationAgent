# Documentation for `pd.read_sql_query`

### pd.read_sql_query(sql: str, con, **kwargs) -> DataFrame

**Description:**
`pd.read_sql_query` is a function provided by the Pandas library that allows users to execute SQL queries against a database and return the results as a Pandas DataFrame. This function facilitates the integration of SQL database operations with data manipulation and analysis capabilities provided by Pandas.

**Parameters:**
- `sql` (`str`): A string containing the SQL query to be executed.
- `con`: A database connection object that specifies the database to connect to. This can be a SQLAlchemy engine or a database connection from other supported libraries.
- `**kwargs`: Additional keyword arguments that can be passed to customize the behavior of the function. This may include parameters for handling the database connection, query execution, or DataFrame formatting.

**Expected Input:**
- The `sql` parameter should be a valid SQL query string that is compatible with the database being queried.
- The `con` parameter must be a valid database connection object. It should be established prior to calling this function.
- The `**kwargs` can include various options depending on the specific requirements of the query or the desired output format.

**Returns:**
`DataFrame`: The function returns a Pandas DataFrame containing the results of the executed SQL query. Each row in the DataFrame corresponds to a row in the result set of the SQL query, and the columns of the DataFrame correspond to the columns returned by the query.

**Detailed Logic:**
- The function begins by validating the provided SQL query and connection object to ensure they are properly formatted and connected.
- It then executes the SQL query against the specified database using the provided connection object.
- The results of the query are fetched and transformed into a Pandas DataFrame.
- The function may also handle additional parameters provided through `**kwargs`, which can modify aspects such as index handling, column data types, or other DataFrame-specific configurations.
- Finally, the resulting DataFrame is returned to the caller, allowing for further data manipulation and analysis using Pandas' extensive functionality. 

This function is particularly useful for data analysts and scientists who need to work with data stored in relational databases, enabling seamless integration of SQL data retrieval with Pandas' data processing capabilities.

---
*Generated with 100% context confidence*
