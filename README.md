# Recipe Fetching App

## Overview
This is designed to retrieve recipes based on specific criteria such as food type, recipe difficulty, and dietary restrictions. It integrates with an external recipe API to fetch relevant recipes and interacts with Catalyst to store data.

## Requirements
- Python 3.6 or higher
- `functions-framework` module
- `requests` module
- Access to an (Spoonacular recipe API)[https://spoonacular.com/food-api]

## Installation
1. **Install Python Packages**:
   - Install `functions-framework` and `requests` using pip:
     ```bash
     pip install functions-framework requests
     ```

2. **API Key**:
   - Obtain Spoonacular API

## Setup

1. **Deployment**:
   - Deploy the function to Google Cloud

## Usage
- **Sending a Request**:
  - Send a JSON payload to the function's HTTP endpoint with the following structure:
    ```json
        {
            "key": "123e4567-e89b-12d3-a456-426614174000",
            "value": {
                "request": "true",
                "foodType": "pasta",
                "recipeDifficulty": "easy",
                "foodRestrictions": "vegetarian",
                "createdAt": "2023-11-22T12:00:00Z"
            }
        }
    ```

- **Receiving a Response**:
  - The function will return a recipe or a relevant message based on the provided criteria.

## Function Details
- **`get_recipe_http`**:
  - This is the main function that handles incoming HTTP requests.
  - It extracts the payload, fetches a recipe using the given criteria, and returns the recipe details.
