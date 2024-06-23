# Development
This document outlines the structure of the project and coding standards. It is intended to provide a guide for developers working on the project to ensure consistency and maintainability.

## Project Structure
### Directory Structure Overview
```
|-- /docs (all documentation)
|-- /config (environment variable handling)
|-- /database (database interactions and models)
|-- /models (models and schemas)
|-- /routes (routes and endpoints)
|-- /services (funcs that interact with the database)
|-- /templates (HTML templates)
|-- /utils (non-database interacting funcs)
|-- /validators (funcs that validate input or models)
|-- common.py (instantiates & stores common objects)
|-- main.py (the entry point)
|-- dockerfile (used to build the container)
|-- docker-compose.yml (used to run the services)
|-- .env.template (template for the .env file)
|-- requirements.txt (Python dependencies)
```

### Directory Structure Details
- `/docs`: Contains all the documentation for the project. This includes the API documentation, environment setup, and development guidelines.
- `/config`: Contains the Config class that handles environment variables. It is responsible for loading the environment variables from the `.env` file and other sources. This directory should be the only place where environment variables are accessed directly.
- `/database`: Contains all functions and models that interact with the database directly. This includes the database connection and any queries that need to be executed. Plaintext NoSQL queries should only be present in this directory.
- `/models`: Contains all the models and schemas used by the application. This includes the Pydantic models used for request and response validation.
- `/routes`: Contains all the routes and endpoints for the application. This includes the FastAPI routers and the route handlers. The routes should be organized by the resource they represent (e.g. /routes/account_router.py for endpoints related to accounts (/account)).
- `/services`: Contains all the functions that interact with the database but do not contain any database queries. The functions in this directory are typically used by endpoints to perform logic that requires database access.
- `/templates`: Contains all the HTML templates used by the application. This directory is only used if the application serves HTML content (e.g. login pages).
- `/utils`: Contains all the utility functions that do not interact with the database. This includes functions for generating tokens, hashing passwords, and other general-purpose functions.
- `/validators`: Contains all the functions that validate input or models. This includes functions that validate email addresses, passwords, and other input data. Functions in this directory can interact with the database but should not contain any hardcoded plaintext database queries (these should be defined in the database directory).
- `common.py`: Contains the instantiation of common objects used by the application. This includes (but is not limited to) the config object storing environment variables, the db_manager object for database interactions, and the token_manager object for token generation and validation. This file should be imported by all other files that require access to these objects.
- `main.py`: The entry point for the application. This file creates the FastAPI application, registers the routers, and starts the application.
- `dockerfile`: Used to build the Docker container for the application. This file should contain the necessary steps to build the application and run it in a container.
- `docker-compose.yml`: Used to run the services required by the application. This file should define the services required by the application (e.g. the database service) and any other services that need to be run alongside the application.
- `.env.template`: A template for the `.env` file. This file contains all the environment variables required by the application along with descriptions of each variable.
- `requirements.txt`: Contains the Python dependencies required by the application. This file should be used to install the dependencies using `pip install -r requirements.txt`.

## Coding Standards
The project follows the [PEP 8](https://pep8.org/) coding standards for Python. The following are some key points to keep in mind when writing code for the project:
- Use 4 spaces for indentation.
- Limit all lines to a reasonable length and wrap them if necessary.
- Use descriptive variable and function names.
- Use type hints for function arguments, return values, and variables where possible. Import custom types from modules if necessary.
- Use docstrings to document functions, classes, and modules. Follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html) for docstrings. Include type hints in docstrings where necessary.
- Modularize code into functions and classes where possible. Avoid writing long functions that perform multiple tasks or have complex logic. Break down complex logic into smaller, more manageable functions.
- Any edits or additions related to endpoints should be documented in the [API documentation](ENDPOINTS.md) file.
- Write tests for all new code and ensure that all tests pass before submitting a pull request. While the project does not have a strict test coverage requirement, it is encouraged to write tests for all new code to ensure that it works as expected.