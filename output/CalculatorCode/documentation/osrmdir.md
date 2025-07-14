# Documentation for `os.rmdir`

### os.rmdir(path: str) -> None

**Description:**
The `os.rmdir` function is used to remove (delete) an empty directory specified by the given path. This function is part of the `os` module in Python, which provides a way to interact with the operating system.

**Parameters:**
- `path` (`str`): The path to the directory that you want to remove. This can be an absolute or relative path.

**Expected Input:**
- `path` should be a string representing the file system path to the directory. The directory must exist and must be empty for the operation to succeed. If the directory is not empty or does not exist, an error will be raised.

**Returns:**
`None`: This function does not return any value. If the operation is successful, the directory is removed without any output. If it fails, an exception is raised.

**Detailed Logic:**
- The function first checks if the specified directory exists and whether it is empty. 
- If the directory is not empty, the function raises an `OSError`, indicating that the directory cannot be removed.
- If the directory is empty, it proceeds to remove the directory from the file system.
- The function does not return any value upon successful execution, but it may raise exceptions such as `FileNotFoundError` if the directory does not exist, or `OSError` for other issues related to the removal process (e.g., permission errors). 
- This function interacts directly with the operating system's file management capabilities, relying on system-level calls to perform the directory removal.

---
*Generated with 100% context confidence*
