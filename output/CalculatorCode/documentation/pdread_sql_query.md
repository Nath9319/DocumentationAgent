# Documentation for `pd.read_sql_query`

### pd.read_sql_query(sql: str, con, **kwargs) -> DataFrame

**Description:**
The `pd.read_sql_query` function is a powerful utility in the Pandas library that allows users to execute SQL queries against a database and return the results as a Pandas DataFrame. This function facilitates seamless integration of SQL databases with data analysis workflows in Python, enabling users to leverage SQL's querying capabilities while benefiting from Pandas' data manipulation features.

**Parameters:**
- `sql` (`str`): A string containing the SQL query to be executed.
- `con`: A database connection object that provides the interface to the database. This can be a connection from libraries such as SQLite, SQLAlchemy, or others compatible with Pandas.
- `**kwargs`: Additional keyword arguments that can be passed to customize the behavior of the function. These may include options for handling index columns, specifying data types, or controlling how the results are fetched.

**Expected Input:**
- The `sql` parameter must be a valid SQL query string that can be executed against the specified database.
- The `con` parameter must be a valid database connection object. It should be established prior to calling this function.
- The `**kwargs` can include various optional parameters, which may vary based on the specific requirements of the database or the desired output format.

**Returns:**
`DataFrame`: A Pandas DataFrame containing the results of the executed SQL query. The DataFrame will have columns corresponding to the fields selected in the SQL query and rows representing the records returned.

**Detailed Logic:**
- The function begins by validating the provided SQL query and database connection.
- It executes the SQL query using the provided connection, retrieving the results from the database.
- The results are then transformed into a Pandas DataFrame, allowing for easy manipulation and analysis of the data.
- The function may utilize additional parameters from `**kwargs` to customize the DataFrame's structure, such as setting specific columns as the index or converting data types.
- This function does not have any internal dependencies but relies on the underlying database connection and SQL execution capabilities provided by the database driver or ORM (Object-Relational Mapping) library in use.

---
*Generated with 100% context confidence*
