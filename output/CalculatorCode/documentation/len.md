# Documentation for `len`

### len(obj: Any) -> int

**Description:**
The `len` function returns the number of items in an object. It is a built-in function in Python that can be used with various data types, including strings, lists, tuples, dictionaries, and sets. The primary purpose of this function is to provide a simple way to determine the size or length of an object.

**Parameters:**
- `obj` (`Any`): The object whose length is to be determined. This can be a string, list, tuple, dictionary, set, or any other object that implements the `__len__` method.

**Expected Input:**
- The input can be any object that supports length measurement. Common examples include:
  - A string (e.g., "Hello")
  - A list (e.g., [1, 2, 3])
  - A tuple (e.g., (1, 2, 3))
  - A dictionary (e.g., {'a': 1, 'b': 2})
  - A set (e.g., {1, 2, 3})
- If the input object does not support length measurement, a `TypeError` will be raised.

**Returns:**
`int`: The number of items in the object. For strings, it returns the number of characters; for lists, tuples, and sets, it returns the number of elements; for dictionaries, it returns the number of key-value pairs.

**Detailed Logic:**
- The function first checks if the provided object has a defined length by looking for the `__len__` method.
- If the method exists, it calls this method to retrieve the length of the object.
- The result is an integer representing the count of items in the object.
- If the object does not support length measurement (i.e., it lacks the `__len__` method), the function raises a `TypeError`, indicating that the object of the given type does not have a length. 

This function is fundamental in Python and is widely used for iterating over collections, validating input sizes, and performing conditional logic based on the number of items in various data structures.

---
*Generated with 100% context confidence*
