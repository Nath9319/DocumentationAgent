# Documentation for `zip`

### zip(*iterables: Iterable) -> Iterator[Tuple]

**Description:**
The `zip` function takes multiple iterable objects (such as lists, tuples, or strings) and aggregates them into tuples. Each tuple contains elements from the input iterables that are at the same index. The resulting tuples are returned as an iterator, which can be converted into a list or used in a loop.

**Parameters:**
- `*iterables` (`Iterable`): One or more iterable objects (e.g., lists, tuples, strings) that will be zipped together. The function can accept any number of iterables.

**Expected Input:**
- The input should consist of one or more iterable objects. Each iterable can be of different types (e.g., list, tuple, string), but they should be compatible in terms of indexing.
- If the input iterables are of different lengths, the resulting tuples will be formed only up to the length of the shortest iterable. Any excess elements in the longer iterables will be ignored.

**Returns:**
`Iterator[Tuple]`: An iterator that produces tuples, where each tuple contains elements from the input iterables at the same index. If no iterables are provided, an empty iterator is returned.

**Detailed Logic:**
- The function begins by accepting a variable number of iterable arguments.
- It then creates an iterator for each iterable, allowing it to traverse through the elements.
- Using the `zip` logic, it retrieves the first element from each iterable, forming a tuple, and continues this process for subsequent elements.
- The iteration stops when the shortest input iterable is exhausted, ensuring that all returned tuples are of equal length.
- The resulting tuples are yielded one at a time, making the function memory efficient, especially when dealing with large datasets. 
- This function does not rely on any external modules and operates using basic iteration and tuple construction.

---
*Generated with 100% context confidence*
