import sys
import json
import csv
import random

# load in preferences file
#MADDIE----
def load_preferences(filename: str):
    try:
        with open(filename, mode='r') as file:
            preferences = json.load(file)
        print("Preferences loaded successfully.\n")  # Temporary print for validation
        return preferences
    except FileNotFoundError:
        print("Error: JSON file not found.")
        return {}
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON data.")
        return {}

# load in recipes file
def load_recipes(filename: str):
    try:
        with open(filename, mode='r') as file:
            recipes_data = json.load(file)
        print("Recipes loaded successfully.\n")  # Temporary print for validation
        return recipes_data['recipes']
    except FileNotFoundError:
        print("Error: recipes JSON file not found.")
        return {}
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON data.")
        return {}

# load in ingredients file
def load_ingredients(filename: str):
    ingredients = {}
    
    with open(filename, mode='r') as file:
        reader = csv.DictReader(file)
        
        # Clean the fieldnames (headers) to remove any leading/trailing spaces
        reader.fieldnames = [field.strip() for field in reader.fieldnames]
        
        for row in reader:
            # Check if 'ingredient' exists in the row
            ingredient_name = row.get('ingredient', '').strip().lower() if 'ingredient' in row else ''
            
            # Skip if the ingredient is missing
            if not ingredient_name:
                print("Skipping row due to missing ingredient.")
                continue

            # validation check for quantity, set quanitity to 0 if it is missing
            quantity = row.get('quantity', None) 
            if quantity is None or quantity == '': 
                quantity = 0 

            # Ensure that quantity is a valid number
            try:
                quantity = float(quantity)
            except ValueError:
                print(f"Warning: Invalid quantity '{quantity}' for ingredient '{ingredient_name}'. Setting it to 1.0.")
                quantity = 1.0  # Default to 1.0 if there's an invalid value

            # Check if 'unit' exists, default to empty string if missing
            unit = row.get('unit', '')
            
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
# XAVIER-----
#function return preference
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

    #USER TAKES OUT RECIPES
    while available_recipes:
        # Display available recipes with numbering
        print("\nAre there any recipes that you DONT want on the meal plan:")
        for index, recipe in enumerate(available_recipes, start=1):
            ingredients_list = ", ".join([ingredient['ingredient'] for ingredient in recipe["ingredients"]])  # Corrected ingredient extraction
            print(f"{index}. {recipe['name']} (Ingredients: {len(recipe['ingredients'])})")
            print(f"   Ingredients: {ingredients_list}\n")

        # Prompt the user to pick a recipe or add all remaining recipes
        user_input = input("Enter the number of the recipe you want to REMOVE or type 'done' to finish: ").strip().lower()
        
        if user_input == "done":
            # Finish the selection process
            print("Done.")
            break
        else:
            try:
                choice = int(user_input)
                if 1 <= choice <= len(available_recipes):
                    selected_recipes.remove(available_recipes.pop(choice - 1))
                    print(f"{selected_recipes[-1]['name']} has been added to your list.")
                else:
                    print("Invalid selection. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number or 'done'.")

    #USER PICKS WHAT RECIPES THEY WANT
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
            # Add all remaining recipes to the selected list
            selected_recipes.extend(available_recipes)
            print("All remaining recipes added.")
            break
        elif user_input == "done":
            # Finish the selection process
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

def create_meal_plan(selected_recipes, selected_diet, output_filename='meal_plan.txt'):
    # Daily calorie limit from the selected diet with a ±200 range
    calorie_limit = selected_diet["nutritional_goals"]["calories"]
    lower_calorie_limit = calorie_limit - 200
    upper_calorie_limit = calorie_limit + 200

    # 7-day meal plan
    meal_plan = {day: [] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
    day_nutrition_totals = {day: {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0} for day in meal_plan}

    # List of available recipes
    recipes = {recipe["name"]: recipe["nutrition"] for recipe in selected_recipes}

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
                print(f"Max attempts to fill {day}'s meal plan. Consider adding more recipes.")
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

    # Write meal plan to meal_plan.txt
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
#MADDIE--------
# go through recipes
def parse_recipes(recipes_file):
    try:
        with open(recipes_file, 'r') as file:
            data = json.load(file)
        # Recipes are in the 'recipes' list, contain 'name', 'ingredients', and 'quantity'
        recipes = {recipe['name']: {ingredient['ingredient']: ingredient['quantity'] for ingredient in recipe['ingredients']} for recipe in data['recipes']}
        return recipes
    except Exception as e:
        print(f"Error reading recipes file: {e}")
        return {}  

# recipes were printing with "-", this fixes that
def parse_meal_plan(meal_plan_file):
    meal_plan = {}
    
    with open(meal_plan_file, 'r') as file:
        for line in file:
            # Remove leading/trailing spaces and skip empty lines
            line = line.strip()
            if not line:
                continue

            # Check if the line starts with "- ", removes
            if line.startswith('-'):
                recipe_name = line[1:].strip()
                # counts occurences
                if recipe_name in meal_plan:
                    meal_plan[recipe_name] += 1
                else:
                    meal_plan[recipe_name] = 1
    
    return meal_plan


def generate_shopping_list(meal_plan_file, recipes_file, ingredient_file, output_filename='meal_plan.txt'):
    # Load recipes from the JSON file and user_available ingredients from CSV file
    recipes = load_recipes(recipes_file)
    available_ingredients = load_ingredients(ingredient_file)

    meal_plan = parse_meal_plan(meal_plan_file)

    shopping_list = {}

    # Aggregate ingredient quantities for each recipe in the meal plan
    for recipe_name, count in meal_plan.items():
        # Find the recipe in the recipes data
        recipe = next((r for r in recipes if r["name"] == recipe_name), None)

        if recipe:
            ingredients = recipe["ingredients"]

            for ingredient in ingredients:
                ingredient_name = ingredient["ingredient"].strip().lower()
                required_quantity = ingredient["quantity"] * count  # Total quantity required for the meal plan
                unit = ingredient.get("unit", "unit")  # Extract unit from the recipe ingredient data

                # Checks if the ingredient is in the ingredients CSV
                if ingredient_name in available_ingredients:
                    available_quantity = available_ingredients[ingredient_name]['quantity']
                else:
                    available_quantity = 0

                # Subtracts total needed ingredients in recipes with the ingredients the user has
                remaining_quantity = max(0, required_quantity - available_quantity)

                if remaining_quantity > 0:
                    if ingredient_name in shopping_list:
                        shopping_list[ingredient_name]['quantity'] += remaining_quantity
                    else:
                        shopping_list[ingredient_name] = {
                            'quantity': remaining_quantity,
                            'unit': unit
                        }

    # Write the shopping list to meal_plan.txt
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
#XAVIER-------
# Import "matplotlib.pyplot"
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

def main():
    #MADDIE-------
    # Load data files
    preferences = load_preferences('preferences.json')
    recipes = load_recipes('recipes.json')

    # User selects their preferred diet
    selected_diet = pick_preference(preferences)
    preferences['selected_preference'] = selected_diet
    #XAVIER------
    # Recommend recipes based on user preference
    recommended_recipes = recommend_recipes(recipes, preferences)
    
    # Allow the user to pick recipes for meal planning
    selected_recipes = pick_from_sorted(recommended_recipes, preferences)
    
    #creates semi random meal plan with nutrition and selected diet in mind
    day_nutrition_totals = create_meal_plan(selected_recipes, selected_diet)

    #MADDIE----
    #generates shopping list based on # of occurences of ingredient 
    generate_shopping_list('meal_plan.txt', 'recipes.json', 'ingredients.csv')

    #XAVIER-----
    #uses matplot to plot the daily nutrients 
    plot_day_nutrition_totals(day_nutrition_totals)
    
if __name__ == "__main__":
    main()

