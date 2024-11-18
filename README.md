# Meal Planner Project

This project is a meal planning application that recommends recipes, creates meal plans, generates shopping lists, and provides nutritional analysis.

## Setup (what she has in her example)
1. Clone the repository
2. Install the required packages
~~example she gives: pip install -r requirements.txt
3. Ensure you have 'ingredients.csv', 'preferences.json', and 'recipes.txt' in the project directory
4. Run the main script
example: python main_menu.py

## Running Tests
To run the unit tests:
~~her example: python -m unittest test_myProject.py

## Features
- User can set or update their preferences on diet and nutrition
- Recipes will be recommended based on the ingredients in the ingredient.csv file and the dietary preferences that the user chooses
- Can generate a weekly meal plan of recipes
- Can generate a shopping list of the necessary ingredients based off the meals for the user
- Can display a nutritional analysis of meal plans

## File Structure 
- 'main_menu.py': Main script containing a display menu where user can choose options and their correlating functions
- 'ingredients.csv': CSV file containing available ingredients and the ingredients nutrition
- 'recipes.txt': TXT file containing the recipes, the type of diets the meal pertains to, and the ingredients that the meal contains
- 'preferences.json': JSON file containing user preferences and nutritional goals
- 'requirements.txt': List of required Python packages
# need to add unit test file name here
# her example: 'test_myProject.py': Unit tests for the project