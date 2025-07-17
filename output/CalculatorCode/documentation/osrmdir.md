# Documentation for `os.rmdir`

### os.rmdir(path: str) -> None

**Description:**
The `os.rmdir` function is used to remove (delete) an empty directory specified by the given path. This function is part of the `os` module, which provides a way of using operating system-dependent functionality in Python.

**Parameters:**
- `path` (`str`): The path to the directory that you want to remove. This can be an absolute or relative path.

**Expected Input:**
- `path` should be a string representing the directory path. The directory must exist and must be empty for the operation to succeed. If the directory contains files or other directories, the function will raise an error.

**Returns:**
`None`: This function does not return a value. If the operation is successful, the directory is removed without any output. If it fails (for example, if the directory is not empty or does not exist), an exception is raised.

**Detailed Logic:**
- The function first checks if the specified directory exists and whether it is empty. 
- If the directory is not empty or does not exist, it raises an `OSError`, indicating the reason for the failure (e.g., "Directory not empty" or "No such file or directory").
- Upon successful execution, the directory is removed from the filesystem.
- This function interacts directly with the operating system's file management system to perform the deletion, ensuring that the specified directory is handled appropriately according to the underlying OS's rules and permissions.

---
*Generated with 100% context confidence*
