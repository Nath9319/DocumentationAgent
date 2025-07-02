### DataService

**Description:**  
Service for loading data into pandas objects from files and databases. This class provides an interface for 
interacting with various data sources, facilitating the conversion of data into a format suitable for analysis 
using the pandas library.

**Parameters / Attributes:**  
| Name          | Type                | Description                                           |
|---------------|---------------------|-------------------------------------------------------|
| file_path     | str                  | Path to the data file to be loaded.                  |
| database_url  | str                  | Connection string for the database to load data from.|
| data_format   | str                  | Format of the data (e.g., 'csv', 'json', 'excel').  |
| pandas_object  | pd.DataFrame or pd.Series | The resulting pandas object after loading the data. |

**Expected Input:**  
• `file_path` must be a valid path to an existing file.  
• `database_url` must be a valid connection string for the database.  
• `data_format` must be one of the supported formats (e.g., 'csv', 'json', 'excel').  

**Returns:**  
`pd.DataFrame` or `pd.Series` – a pandas object containing the loaded data, structured according to the 
input source.

**Detailed Logic:**  
• The service checks the specified `data_format` to determine the appropriate loading method.  
• If loading from a file, it verifies the existence of the file at `file_path`.  
• For database connections, it establishes a connection using `database_url` and retrieves the data.  
• The data is then processed and converted into a pandas object, which is returned to the caller.

**Raises / Errors:**  
• Raises `FileNotFoundError` if the specified file does not exist.  
• Raises `ValueError` if the `data_format` is unsupported.  
• Raises `ConnectionError` if the database connection fails.

**Usage Example:**  
```python
from app.services.data_service import DataService

data_service = DataService(file_path='data.csv', data_format='csv')
data_frame = data_service.load_data()
```