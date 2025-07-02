# Documentation for `api_router.include_router`

### api_router.include_router(router: Router, prefix: Optional[str] = None, tags: Optional[List[str]] = None, dependencies: Optional[List[Depends]] = None, responses: Optional[Dict[int, Dict[str, Any]]] = None, default_response_class: Optional[Type[Response]] = None, include_in_schema: bool = True) -> None

**Description:**
The `include_router` function is a method of the `api_router` object that allows for the inclusion of another router into the current routing structure of a web application. This facilitates modular organization of routes, enabling developers to group related endpoints together for better maintainability and clarity.

**Parameters:**
- `router` (`Router`): An instance of the `Router` class that contains the routes to be included in the current router.
- `prefix` (`Optional[str]`): A string that will be prefixed to all routes defined in the included router. This allows for namespacing of routes.
- `tags` (`Optional[List[str]]`): A list of tags that can be associated with the routes in the included router for documentation purposes.
- `dependencies` (`Optional[List[Depends]]`): A list of dependencies that will be applied to all routes in the included router, allowing for shared functionality such as authentication or data validation.
- `responses` (`Optional[Dict[int, Dict[str, Any]]]`): A dictionary that maps HTTP status codes to response descriptions, which can be used for automatic generation of API documentation.
- `default_response_class` (`Optional[Type[Response]]`): A default response class to be used for all routes in the included router if not otherwise specified.
- `include_in_schema` (`bool`): A flag indicating whether the routes in the included router should be included in the OpenAPI schema. Defaults to `True`.

**Expected Input:**
- The `router` parameter must be an instance of the `Router` class.
- The `prefix` should be a string or `None`, where a string should not contain any leading slashes.
- The `tags` should be a list of strings or `None`, where each string represents a tag relevant to the routes.
- The `dependencies` should be a list of `Depends` objects or `None`.
- The `responses` should be a dictionary mapping integers to dictionaries or `None`.
- The `default_response_class` should be a class type derived from `Response` or `None`.
- The `include_in_schema` should be a boolean value.

**Returns:**
`None`: This function does not return any value. It modifies the routing structure of the `api_router` in place.

**Detailed Logic:**
- The function first validates the provided `router` to ensure it is an instance of the `Router` class.
- If a `prefix` is provided, it prepends this prefix to all routes in the included router, ensuring that they are correctly namespaced.
- The function then associates any provided `tags` with the routes, which aids in generating documentation.
- If `dependencies` are specified, these are applied to all routes in the included router, allowing for shared logic such as authentication checks.
- The `responses` dictionary is processed to map HTTP status codes to their descriptions, enhancing the API documentation.
- The `default_response_class` is set for all routes unless overridden by individual route definitions.
- Finally, the function checks the `include_in_schema` flag to determine if the routes should be included in the OpenAPI schema, ensuring that the API documentation reflects the current routing structure.

---
*Generated with 100% context confidence*
