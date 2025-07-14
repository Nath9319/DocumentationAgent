# Documentation for `len`

### len(obj: Any) -> int

**Description:**
The `len` function returns the number of items in an object. It is a built-in function in Python that can be used with various data types, including strings, lists, tuples, dictionaries, and sets. The primary purpose of this function is to provide a way to determine the size or length of a given object.

**Parameters:**
- `obj` (`Any`): The object whose length is to be determined. This can be a string, list, tuple, dictionary, set, or any other collection type that supports length measurement.

**Expected Input:**
- The input `obj` can be any object that implements the `__len__` method. Common examples include:
  - Strings (e.g., `"hello"`)
  - Lists (e.g., `[1, 2, 3]`)
  - Tuples (e.g., `(1, 2, 3)`)
  - Dictionaries (e.g., `{"key": "value"}`)
  - Sets (e.g., `{1, 2, 3}`)
- If the input is not a valid type that supports length measurement, a `TypeError` will be raised.

**Returns:**
`int`: The number of items in the object. For example, if the input is a list with three elements, the function will return `3`.

**Detailed Logic:**
- The `len` function internally calls the `__len__` method of the object passed as an argument. This method is defined in the object’s class and is responsible for returning the length of the object.
- If the object does not have a `__len__` method, a `TypeError` is raised, indicating that the object is not of a type that can have a length.
- The function operates in constant time for built-in types, meaning it efficiently retrieves the length without needing to iterate through the elements of the object.

---
*Generated with 100% context confidence*
