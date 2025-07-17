# Documentation for `os.listdir`

### os.listdir(path: str = '.') -> List[str]

**Description:**
The `os.listdir` function returns a list of the names of the entries in the directory given by the specified path. This includes files and subdirectories but does not include the special entries `.` (current directory) and `..` (parent directory). If the path is not specified, it defaults to the current working directory.

**Parameters:**
- `path` (`str`, optional): The path to the directory whose entries are to be listed. If not provided, the current working directory is used.

**Expected Input:**
- `path` should be a valid string representing a directory path. It can be an absolute or relative path. If the specified path does not exist or is not a directory, an error will be raised.

**Returns:**
`List[str]`: A list of strings, where each string is the name of an entry in the specified directory.

**Detailed Logic:**
- The function begins by validating the provided `path` to ensure it points to a directory.
- It retrieves the list of entries in the directory using system calls that interact with the file system.
- The function constructs and returns a list containing the names of all entries found in the directory, excluding the current (`.`) and parent (`..`) directory entries.
- If the specified path is invalid or inaccessible, an appropriate exception is raised, indicating the nature of the error (e.g., `FileNotFoundError` or `NotADirectoryError`).
- This function does not depend on any internal modules but interacts with the operating system's file system to gather directory contents.

---
*Generated with 100% context confidence*
