# Documentation for `pd.read_sql_query`

### pd.read_sql_query(sql: str, con, **kwargs) -> DataFrame

**Description:**
The `pd.read_sql_query` function is part of the Pandas library and is used to execute a SQL query against a database connection and return the result as a Pandas DataFrame. This function simplifies the process of retrieving data from a SQL database, allowing users to leverage SQL's querying capabilities while working within the Pandas ecosystem.

**Parameters:**
- `sql` (`str`): A string containing the SQL query to be executed.
- `con`: A database connection object that specifies the database to connect to. This can be a SQLAlchemy engine or a database connection object from other database libraries.
- `**kwargs`: Additional keyword arguments that can be passed to customize the behavior of the function, such as parameters for the SQL query or options for the DataFrame.

**Expected Input:**
- The `sql` parameter should be a valid SQL query string. It must conform to the syntax and semantics of the SQL dialect supported by the database specified in the `con` parameter.
- The `con` parameter must be a valid database connection object. It should be established prior to calling this function.
- Additional keyword arguments can include parameters for the SQL query, which should be provided in a format compatible with the database being queried.

**Returns:**
`DataFrame`: A Pandas DataFrame containing the results of the executed SQL query. Each row in the DataFrame corresponds to a row in the result set of the SQL query, and each column corresponds to a column in the result set.

**Detailed Logic:**
- The function begins by establishing a connection to the database using the provided connection object.
- It then executes the SQL query specified in the `sql` parameter against the connected database.
- The results of the query are fetched and converted into a Pandas DataFrame.
- If any additional keyword arguments are provided, they are utilized to modify the execution of the SQL query or the resulting DataFrame.
- Finally, the function returns the DataFrame containing the query results, allowing for further data manipulation and analysis using Pandas' powerful data handling capabilities. 

This function is particularly useful for data analysis tasks where SQL databases are involved, enabling seamless integration of SQL querying with Pandas' data manipulation features.

---
*Generated with 100% context confidence*
