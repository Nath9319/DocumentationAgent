# Documentation for `api_router.include_router`

### api_router.include_router(router: Router, prefix: Optional[str] = None, tags: Optional[List[str]] = None, dependencies: Optional[List[Depends]] = None, responses: Optional[Dict[int, Dict[str, Any]]] = None, default_response_class: Optional[Type[Response]] = None, include_in_schema: bool = True) -> None

**Description:**
The `include_router` function is a method of the `api_router` object that allows for the inclusion of another router into the current API router. This facilitates modular organization of routes, enabling developers to group related endpoints together and manage them more effectively. By using this function, developers can create a hierarchical structure of routes, improving code maintainability and readability.

**Parameters:**
- `router` (`Router`): The router instance to be included. This router contains its own set of routes that will be added to the current router.
- `prefix` (`Optional[str]`): An optional string that specifies a prefix to be added to all routes in the included router. This is useful for namespacing routes.
- `tags` (`Optional[List[str]]`): An optional list of tags that can be associated with the included routes for documentation purposes.
- `dependencies` (`Optional[List[Depends]]`): An optional list of dependencies that should be applied to all routes in the included router. This allows for shared logic, such as authentication or validation, across multiple routes.
- `responses` (`Optional[Dict[int, Dict[str, Any]]]`): An optional dictionary that defines custom responses for the included routes, allowing for more detailed API documentation.
- `default_response_class` (`Optional[Type[Response]]`): An optional class that defines the default response type for the included routes.
- `include_in_schema` (`bool`): A boolean flag indicating whether the routes from the included router should be included in the OpenAPI schema. Defaults to `True`.

**Expected Input:**
- The `router` parameter must be an instance of the `Router` class.
- The `prefix` should be a string if provided, and it should not contain any invalid characters for URL paths.
- The `tags` should be a list of strings, each representing a tag for documentation.
- The `dependencies` should be a list of dependency instances, if provided.
- The `responses` should be a dictionary mapping HTTP status codes to response descriptions.
- The `default_response_class` should be a valid response class if provided.
- The `include_in_schema` should be a boolean value.

**Returns:**
`None`: This function does not return any value. It modifies the current router by adding the routes from the included router.

**Detailed Logic:**
- The function begins by validating the provided `router` to ensure it is an instance of the `Router` class.
- If a `prefix` is provided, it is prepended to all routes in the included router, effectively namespacing them.
- The function then iterates over the routes in the included router, applying any specified `dependencies`, `responses`, and `default_response_class` to each route.
- If `tags` are provided, they are associated with the routes for documentation purposes.
- Finally, the function updates the current router's internal structure to include the routes from the included router, ensuring that they are accessible through the API. The `include_in_schema` parameter determines whether these routes should appear in the generated OpenAPI schema, allowing for better API documentation.

---
*Generated with 100% context confidence*
