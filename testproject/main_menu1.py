import sys
import json
import csv
import random

def load_preferences(filename: str):
    try:
        with open('preferences1.json') as file:
            preferences = json.load(file)
        print("Preferences loaded successfully.\n")  # Temporary print for validation
        #print(preferences)  # can delete these lines later
        return preferences
    except FileNotFoundError:
        print("Error: JSON file not found.")
        return {}
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON data.")
        return {}

def load_recipes(filename: str):
    try:
        with open('recipes1.json') as file:
            recipes_data = json.load(file)
        print("recipes loaded successfully.\n")  # Temporary print for validation
        #print(recipes)  # can delete these lines later
        return recipes_data['recipes']
    except FileNotFoundError:
        print("Error: recipes JSON file not found.")
        return {}
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON data.")
        return {}


def load_ingredients(file_path):
    ingredients = {}
    
    with open('ingredients1.csv') as file:
        reader = csv.DictReader(file)
        
        # Clean the fieldnames (headers) to remove any leading/trailing spaces
        reader.fieldnames = [field.strip() for field in reader.fieldnames]
        
        for row in reader:
            # Check if 'ingredient' exists in the row
            ingredient_name = row.get('ingredient', '').strip().lower() if 'ingredient' in row else ''
            
            # Skip this row if the ingredient is missing
            if not ingredient_name:
                print("Skipping row due to missing ingredient.")
                continue

            # Check if 'quantity' exists in the row and is a valid value
            quantity = row.get('quantity', None)  # Default to None if quantity is missing
            if quantity is None or quantity == '':  # If 'quantity' is missing or empty
                quantity = 1.0  # Set to default value (1.0)

            # Ensure that quantity is a valid number
            try:
                quantity = float(quantity)
            except ValueError:
                print(f"Warning: Invalid quantity '{quantity}' for ingredient '{ingredient_name}'. Setting it to 1.0.")
                quantity = 1.0  # Default to 1.0 if there's an invalid value

            # Check if 'unit' exists, default to empty string if missing
            unit = row.get('unit', '')  # Default to empty string if no unit is provided
            
            ingredients[ingredient_name] = {
                'quantity': quantity,
                'unit': unit,
            }
    
    return ingredients



    
#obligatory promts user and returns selected_diet
def pick_preference(preferences):
    available_diets = [pref["diet"] for pref in preferences.get("user_preferences", [])]
    if not available_diets:
        print("No available dietary preferences to choose from.")
        return None
    
    print("Available dietary preferences:")
    for index, diet in enumerate(available_diets, start=1):
        print(f"{index}. {diet}")
    
    try:
        choice = int(input("Please select a dietary preference by number: "))
        if 1 <= choice <= len(available_diets):
            selected_diet = preferences["user_preferences"][choice - 1]
            print(f"You have selected the {selected_diet['diet']} diet.")
            return selected_diet
        else:
            print("Invalid selection. Please try again.")
            return None
    except ValueError:
        print("Invalid input. Please enter a number.")
        return None     
    
#function return preference FIX 
def recommend_recipes(recipes, preferences):
    # Create mapping full diet names and tags
    diet_tag_mapping = {
        "omnivore": "Omni",
        "vegetarian": "Veg",
        "pescatarian": "Pesc",
        "vegan": "All"  # Vegan users will only see recipes tagged as "All"
    }

    # Get user-selected preference using the pick_preference function
    selected_preference = preferences.get('selected_preference', None)
    if not selected_preference:
        print("No valid preference selected. Cannot recommend recipes.")
        return []

    # Extract the user's diet preference
    diet_type = selected_preference.get("diet", "All").lower()
    tag_to_match = diet_tag_mapping.get(diet_type, "All")

    # Filter recipes based on diet preference
    filtered_recipes = [
        recipe for recipe in recipes
        if isinstance(recipe, dict) and "tags" in recipe and isinstance(recipe["tags"], list) and (
            tag_to_match.lower() in [tag.lower() for tag in recipe["tags"]] or "all" in [tag.lower() for tag in recipe["tags"]]
        )
    ]
    
    # Sorting by the number of ingredients making shopping/picking easier
    sorted_recipes = sorted(filtered_recipes, key=lambda r: len(r["ingredients"]))
    
    print(f"\nRecommended recipes for the {diet_type} diet (including recipes tagged 'All'):\n")
    
    return sorted_recipes

#used in meal_plan
def pick_from_sorted(recipes, preferences):
    if not recipes:
        print("No recommended recipes available.")
        return []

    selected_recipes = []  # List to store the selected recipes
    available_recipes = recipes[:]  # Copy of recommended recipes to track remaining options

    while available_recipes:
        # Display available recipes with numbering
        print("\nAvailable recipes to pick from:")
        for index, recipe in enumerate(available_recipes, start=1):
            ingredients_list = ", ".join([ingredient['ingredient'] for ingredient in recipe["ingredients"]])  # Corrected ingredient extraction
            print(f"{index}. {recipe['name']} (Ingredients: {len(recipe['ingredients'])})")
            print(f"   Ingredients: {ingredients_list}\n")

        # Prompt the user to pick a recipe or add all remaining recipes
        user_input = input("Enter the number of the recipe to pick, 'all' to add all remaining recipes, or 'done' to finish: ").strip().lower()
        
        if user_input == "all":
            selected_recipes.extend(available_recipes)
            print("All remaining recipes added.")
            break
        elif user_input == "done":
            print("Recipe selection finished.")
            break
        else:
            try:
                choice = int(user_input)
                if 1 <= choice <= len(available_recipes):
                    selected_recipes.append(available_recipes.pop(choice - 1))
                    print(f"{selected_recipes[-1]['name']} has been added to your list.")
                else:
                    print("Invalid selection. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number, 'all', or 'done'.")
                
    # Display the final list of selected recipes
    print("\nSelected recipes for meal planning:")
    for recipe in selected_recipes:
        ingredients_list = ", ".join([ingredient['ingredient'] for ingredient in recipe["ingredients"]])  # Corrected ingredient extraction
        print(f"- {recipe['name']} (Ingredients: {len(recipe['ingredients'])})")
        print(f"  Ingredients: {ingredients_list}\n")    

    return selected_recipes

'''
def calculate_nutrition(selected_recipes, ingredients):
    nutrition_summary = {}

    for recipe in selected_recipes:
        recipe_name = recipe['name']
        total_nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0}

        for ingredient in recipe["ingredients"]:
            ingredient_name = get_cleaned_ingredient_name(ingredient[0])  # Clean the ingredient name

            # Check if the cleaned ingredient name exists in the nutritional data
            if ingredient_name in ingredients:
                nutrition_info = ingredients[ingredient_name]

                # Sum nutritional values
                total_nutrition['calories'] += nutrition_info['calories']
                total_nutrition['protein'] += nutrition_info['protein']
                total_nutrition['carbs'] += nutrition_info['carbs']
                total_nutrition['fat'] += nutrition_info['fat']
                total_nutrition['fiber'] += nutrition_info['fiber']
            else:
                print(f"Warning: Nutritional data missing for {ingredient_name}")

        nutrition_summary[recipe_name] = total_nutrition

    return nutrition_summary
'''


def create_meal_plan(selected_recipes, selected_diet, output_filename='meal_plan.txt'):
    # Daily calorie limit from the selected diet with a ±200 range
    calorie_limit = selected_diet["nutritional_goals"]["calories"]
    lower_calorie_limit = calorie_limit - 200
    upper_calorie_limit = calorie_limit + 200

    # 7-day meal plan
    meal_plan = {day: [] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
    day_nutrition_totals = {day: {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0} for day in meal_plan}

    # List of available recipes
    #recipes = list(selected_recipes_nutrition.items())
    recipe_nutrition_dict = {recipe["name"]: recipe["nutrition"] for recipe in selected_recipes}

    # Protects from infinite loop
    MAX_ATTEMPTS = 100

    # Meal plan random no repeats for each day
    for day in meal_plan.keys():
        used_recipes = set()  # Track used recipes for the day
        attempt_count = 0  # Reset the attempt count for each day
        print(f"Creating meal plan for {day}.")

        while day_nutrition_totals[day]["calories"] < lower_calorie_limit or (
            day_nutrition_totals[day]["calories"] < upper_calorie_limit
        ):
            if attempt_count >= MAX_ATTEMPTS:
                print(f"Too many attempts to fill {day}'s meal plan. Exiting.")
                break
            recipe = random.choice(selected_recipes)  # Randomly select a recipe
            attempt_count += 1

            # Check if recipe already used for the day
            if recipe["name"] not in used_recipes:
                # Check if adding the recipe would keep within the upper calorie limit
                if day_nutrition_totals[day]["calories"] + recipe["nutrition"]["calories"] <= upper_calorie_limit:
                    # Add recipe to the current day
                    meal_plan[day].append(recipe["name"])
                    used_recipes.add(recipe["name"])  # Mark recipe as used

                    # Update nutritional totals for the day
                    for key in day_nutrition_totals[day]:
                        day_nutrition_totals[day][key] += recipe["nutrition"][key]
                else:
                    break  # Stop adding if the upper calorie limit would be exceeded

    # Write meal plan to a file
    with open(output_filename, 'w') as file:
        for day, recipes in meal_plan.items():
            file.write(f"\n{day}:\n")
            if recipes:
                for recipe_name in recipes:
                    file.write(f"  - {recipe_name}\n")
                file.write("Total Nutritional Values for the day:\n")
                file.write(f"  Calories: {round(day_nutrition_totals[day]['calories'], 1)} kcal\n")
                file.write(f"  Protein: {round(day_nutrition_totals[day]['protein'], 1)} g\n")
                file.write(f"  Carbs: {round(day_nutrition_totals[day]['carbs'], 1)} g\n")
                file.write(f"  Fat: {round(day_nutrition_totals[day]['fat'], 1)} g\n")
                file.write(f"  Fiber: {round(day_nutrition_totals[day]['fiber'], 1)} g\n")
            else:
                file.write("  No recipes available for this day.\n")

    print(f"Meal plan has been written to {output_filename}")
    return day_nutrition_totals
    
'''
from collections import Counter

def load_recipes_from_text(file_path):
    #recipes and ingredients the text file
    recipes_ingredients = {}
    with open(file_path, 'r') as file:
        for line in file:
            if ':' in line:
                recipe_name, rest = line.split(':', 1)
                ingredients_part = rest.split('}{')[-1].strip(' }{\n')  # Extract ingredients 
                ingredients = [ingredient.strip() for ingredient in ingredients_part.split(',')]
                recipes_ingredients[recipe_name.strip()] = ingredients
    return recipes_ingredients

def count_recipe_occurrences(meal_plan_file):
    # Count occurrences recipe in the meal_plan.txt
    recipe_counter = Counter()
    with open(meal_plan_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('-'):
                recipe = line[1:].strip()  # Remove whitespace
                recipe_counter[recipe] += 1
    return recipe_counter


# import csv

def parse_ingredient_units(ingredient_file):
    ingredient_units = {}
    try:
        with open(ingredient_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                ingredient = row['ingredient'].strip()  # Ingredient name
                #unit = row['unit'].strip()  # Unit of measurement
                #ingredient_units[ingredient] = unit
                # print(f"Loaded unit for {ingredient}: {unit}")  # Debugging the units
    except Exception as e:
        print(f"Error reading ingredient file: {e}")
    
    return ingredient_units

'''





def parse_recipes(recipes_file):
    try:
        with open(recipes_file, 'r') as file:
            data = json.load(file)
        # Recipes are in the 'recipes' list, each with a 'name' and 'ingredients'
        recipes = {recipe['name']: {ingredient['ingredient']: ingredient['quantity'] for ingredient in recipe['ingredients']} for recipe in data['recipes']}
        return recipes
    except Exception as e:
        print(f"Error reading recipes file: {e}")
        return {}  

def parse_meal_plan(meal_plan_file):
    meal_plan = {}
    
    with open(meal_plan_file, 'r') as file:
        for line in file:
            # Remove leading/trailing spaces and skip empty lines
            line = line.strip()
            if not line:
                continue

            # Check if the line starts with "- ", indicating a recipe entry
            if line.startswith('-'):
                recipe_name = line[1:].strip()  # Remove leading "- " to get the recipe name
                if recipe_name in meal_plan:
                    meal_plan[recipe_name] += 1
                else:
                    meal_plan[recipe_name] = 1
    
    return meal_plan

   
def generate_shopping_list(meal_plan_file, recipes_file, ingredient_file, output_filename='meal_plan.txt'):
    # Load recipes from the JSON file
    recipes = load_recipes(recipes_file)

    # Parse the meal plan to get the list of recipes and their occurrences
    meal_plan = parse_meal_plan(meal_plan_file)

    # Load available ingredients from the CSV file
    available_ingredients = load_ingredients(ingredient_file)

    # Initialize an empty shopping list
    shopping_list = {}

    # Aggregate ingredient quantities for each recipe in the meal plan
    for recipe_name, count in meal_plan.items():
        # Find the recipe in the recipes data
        recipe = next((r for r in recipes if r["name"] == recipe_name), None)

        if recipe:
            ingredients = recipe["ingredients"]

            for ingredient in ingredients:
                ingredient_name = ingredient["ingredient"].strip().lower()  # Normalize the ingredient name
                required_quantity = ingredient["quantity"] * count  # Total quantity required for the meal plan
                unit = ingredient.get("unit", "unit")  # Extract unit from the recipe ingredient data

                # Check if the ingredient is available in the ingredients CSV
                if ingredient_name in available_ingredients:
                    available_quantity = available_ingredients[ingredient_name]['quantity']
                else:
                    available_quantity = 0  # If not found in the CSV, assume no available quantity

                # Calculate the remaining quantity needed for the shopping list
                remaining_quantity = max(0, required_quantity - available_quantity)

                if remaining_quantity > 0:
                    # Add to shopping list (if not already present, initialize the quantity)
                    if ingredient_name in shopping_list:
                        shopping_list[ingredient_name]['quantity'] += remaining_quantity
                    else:
                        shopping_list[ingredient_name] = {
                            'quantity': remaining_quantity,
                            'unit': unit
                        }

    # Write the shopping list to the output file
    try:
        with open(output_filename, 'a') as file:
            file.write("\nShopping List:\n")
            for ingredient, details in shopping_list.items():
                unit = details['unit']
                total_quantity = details['quantity']

                if total_quantity > 1 and not unit.endswith('s'):
                    unit += 's'
                    
                file.write(f"{ingredient}: {total_quantity} {unit}\n")

        print(f"Shopping list has been successfully appended to {output_filename}.")
    except Exception as e:
        print(f"Error appending shopping list: {e}")


'''
import matplotlib.pyplot as plt

def plot_day_nutrition_totals(day_nutrition_totals):
    # Prepare data for plotting
    days = list(day_nutrition_totals.keys())
    calories = [day_nutrition_totals[day]['calories'] for day in days]
    protein = [day_nutrition_totals[day]['protein'] for day in days]
    carbs = [day_nutrition_totals[day]['carbs'] for day in days]
    fat = [day_nutrition_totals[day]['fat'] for day in days]
    fiber = [day_nutrition_totals[day]['fiber'] for day in days]

    #Plotting 
    plt.figure(figsize=(10, 6))
    
    plt.bar(days, calories, label='Calories', color='red')
    plt.bar(days, protein, bottom=calories, label='Protein', color='blue')
    plt.bar(days, carbs, bottom=[calories[i] + protein[i] for i in range(len(days))], label='Carbs', color='green')
    plt.bar(days, fat, bottom=[calories[i] + protein[i] + carbs[i] for i in range(len(days))], label='Fat', color='orange')
    plt.bar(days, fiber, bottom=[calories[i] + protein[i] + carbs[i] + fat[i] for i in range(len(days))], label='Fiber', color='purple')
    #Labels
    plt.xlabel('Days of the Week')
    plt.ylabel('Nutritional Values')
    plt.title('Daily Nutrition Totals (Stacked Bar Graph)')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()
    
    '''

def main():
    # Load data files
    preferences = load_preferences('preferences.json')
    recipes = load_recipes('recipes.json')
    ingredients = load_ingredients('ingredients.csv')

    #These all work beautifully
    
    #revelation starts here!!!!
    selected_diet = pick_preference(preferences)
    #print(selected_diet)
    #^^^ can then pass selected diet instead go back and fix
    preferences['selected_preference'] = selected_diet

    #Recommend recipes based on user preference
    #print("recipes recommended by preference")
    recommended_recipes = recommend_recipes(recipes, preferences)
    
    
    #Allow the user to pick recipes for meal planning
    # print("select preference to see available recipes")
    selected_recipes = pick_from_sorted(recipes, preferences)
    
    '''
    selected_recipes_nutrition = calculate_nutrition(selected_recipes, ingredients)
    #print(selected_recipes_nutrition)
    '''
    #creates semi random meal plan with nutrition and selected diet in mind
    day_nutrition_totals = create_meal_plan(recipes, selected_diet)
    
    #generates shopping list based on # of occurences of ingredient 
    generate_shopping_list('meal_plan.txt', 'recipes.json', 'ingredients.csv')
    
    #uses matplot to plot the daily nutrients 
    #plot_day_nutrition_totals(day_nutrition_totals)
    
if __name__ == "__main__":
    main()
