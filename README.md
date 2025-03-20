# Automation Agents

## Introduction

This project is a consolidation of various automation utilities and services. It includes a range of functionalities such as data cleaning, currency conversion, and more, all accessible through a RESTful API.

## Installation Instructions

**Prerequisite:** Ensure you have [Poetry](https://python-poetry.org/) installed

To set up the project locally, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a virtual environment**:
    ```bash
    python -m venv .venv
    ```

3. **Disable Poetry auto-generated virtual environments**:
    ```bash
    poetry config virtualenvs.create false
    ```

4. **Activate your virtual environment**:
    ```bash
    source .venv/bin/activate
    ```

2. **Install Dependencies**:
   ```bash
   poetry install
   ```

3. **Run the Application**:
   Use the following command to start the application:
   ```bash
   python main.py
   ```

## Folder Structure

The project is organized as follows:

- **`api/`**: Contains the core application logic and utilities.
  - **`core/`**: Configuration settings.
  - **`utils/`**: Utility scripts for various tasks.
  - **`v1/`**: Version 1 of the API, including routes, schemas, and services.

- **`main.py`**: The main entry point of the application, setting up the FastAPI app and including middleware for CORS.

## Key Features

- **Utilities**: Includes a range of utilities such as address conversion, API key randomization, and more.
- **Modular Design**: Organized into clear modules for scalability and maintainability.

## Usage Examples

To access the API, navigate to the root endpoint, which redirects to the API documentation: