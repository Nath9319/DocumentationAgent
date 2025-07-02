Scientific Calculator API (V2)This project is a powerful, modular Scientific Calculator built with Python and FastAPI. It provides a RESTful API for basic arithmetic, scientific functions, matrix operations, financial calculations, and advanced statistical analysis on various data sources.This version includes a simple web frontend to interact with some of the calculator's features.FeaturesBasic & Scientific Math: All standard calculator functions from addition to logarithms.Matrix Operations: Determinant and Inverse of a matrix.Financial Calculations: Future Value, Present Value, and Loan Payments.Statistical Analysis:Descriptive statistics (mean, median, std, etc.) on lists, CSV files, and SQLite data.Ordinary Least Squares (OLS) regression analysis.New: Correlation Matrix calculation for a given dataset.Independent T-Test.Web User Interface: A simple frontend to test basic math functions in the browser.Robust Architecture: Modular code separated into logical layers (API, Services, Models) for maintainability and scalability.It can also calculate OLS regression.Centralized Error Handling: Consistent JSON error responses for all API exceptions.Project Structurescientific_calculator_api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py
│   │       └── endpoints/
│   │           ├── basic_math.py
│   │           ├── scientific.py
│   │           ├── statistics.py
│   │           ├── matrix.py
│   │           └── financial.py       # New
│   ├── core/
│   │   ├── config.py
│   │   └── exceptions.py        # New
│   ├── models/
│   │   └── calculator.py
│   ├── services/
│   │   ├── calculation_service.py
│   │   ├── data_service.py
│   │   ├── stats_service.py
│   │   └── financial_service.py # New
│   └── __init__.py
├── data/
│   ├── sample_data.csv
│   └── sample_database.db
├── static/                      # New
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
├── templates/                   # New
│   └── index.html
├── .gitignore
├── create_db.py
├── main.py
└── requirements.txt
Setup and Installation1. PrerequisitesPython 3.8+pip package manager2. Install DependenciesNavigate to the project's root directory and run:pip install -r requirements.txt
3. Generate Sample DatabaseTo use the SQLite-based features, create the sample database by running:python create_db.py
This creates data/sample_database.db.4. Run the ApplicationStart the FastAPI server with Uvicorn:uvicorn main:app --reload
5. Using the APIInteractive API Docs (Swagger): Go to http://127.0.0.1:8000/docsSimple Web Frontend: Go to http://127.0.0.1:8000/ to use the web-based calculator.