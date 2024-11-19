import sys
import json
import csv
import random

def load_preferences(filename: str):
    try:
        with open(filename, mode='r') as file:
            preferences = json.load(file)
        #print("Preferences loaded successfully.\n")  # Temporary print for validation
        #print(preferences)  # can delete these lines later
        return preferences
    except FileNotFoundError:
        print("Error: JSON file not found.")
        return {}
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON data.")
        return {}
        
def load_recipes(filename: str):
    recipes = []
    try:
        with open(filename, mode='r') as file:
            for line in file:
                # Ignore empty
                line = line.strip()
                if not line:
                    continue
                
                # get name, tags, and ingredients
                try:
                    name, rest = line.split(":", 1)
                    tags, ingredients = rest.split("}{")
                    
                    # Clean 
                    name = name.strip()
                    tags = tags.replace("{", "").replace("}", "").strip().split(", ")
                    ingredients = ingredients.replace("}", "").strip().split(", ")

                    # Add structured recipe data to the list
                    recipes.append({
                        "name": name,
                        "tags": tags,
                        "ingredients": ingredients
                    })
                except ValueError:
                    print(f"Skipping invalid line: {line}")
        #print("Recipes loaded successfully.\n")  # Temporary print validation
        #print(recipes)  # Delete this later?
        return recipes
    except FileNotFoundError:
        print("Error: Text file not found.")
        return []
    except Exception as e:
        print(f"Error: Failed to load recipes. {e}")
        return []
        
def load_ingredients(filename: str):
    ingredients = []
    try:
        with open(filename, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Each row dictionary with column headers
                ingredients.append({key.strip(): value.strip() for key, value in row.items()})
        #print("Ingredients loaded successfully.\n")  # Temporary validation print
        #print(ingredients)  # Delete this line later
        return ingredients
    except FileNotFoundError:
        print("Error: CSV file not found.")
        return []
    except Exception as e:
        print(f"Error: Failed to load ingredients. {e}")
        return []
    
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
    #FIX
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
        if tag_to_match.lower() in [tag.lower() for tag in recipe["tags"]] or "all" in [tag.lower() for tag in recipe["tags"]]
    ]
    
    #Sorting by the number of ingredients making shopping/picking easier
    sorted_recipes = sorted(filtered_recipes, key=lambda r: len(r["ingredients"]))
    
    print(f"\nRecommended recipes for the {diet_type} diet (including recipes tagged 'All'):\n")
    #for recipe in sorted_recipes:
        #ingredients_list = ", ".join(recipe["ingredients"])  # Join ingredients into string
        #print(f"- {recipe['name']} (Ingredients: {len(recipe['ingredients'])})")
        #print(f"  Ingredients: {ingredients_list}\n")
    
    return sorted_recipes
#used in meal_plan
def pick_from_sorted(recipes, preferences):
    # Get the sorted list of recommended recipes
    # recommended_recipes = recommend_recipes(recipes, preferences)
    
    if not recipes:
        print("No recommended recipes available.")
        return []

    selected_recipes = []  # List to store the selected recipes
    available_recipes = recipes[:]  # Copy of recommended recipes to track remaining options

    while available_recipes:
        # Display available recipes with numbering
        print("\nAvailable recipes to pick from:")
        for index, recipe in enumerate(available_recipes, start=1):
            ingredients_list = ", ".join(recipe["ingredients"])
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
                    # Add the chosen recipe to the selected list
                    selected_recipes.append(available_recipes.pop(choice - 1))
                    print(f"{selected_recipes[-1]['name']} has been added to your list.")
                else:
                    print("Invalid selection. Please enter a valid number.")
            except ValueError:
                print("Invalid input. Please enter a number, 'all', or 'done'.")
                
    # Display the final list of selected recipes
    print("\nSelected recipes for meal planning:")
    for recipe in selected_recipes:
        ingredients_list = ", ".join(recipe["ingredients"])
        print(f"- {recipe['name']} (Ingredients: {len(recipe['ingredients'])})")
        print(f"  Ingredients: {ingredients_list}\n")    

    return selected_recipes

def calculate_nutrition(selected_recipes, ingredients):
   
    nutrition_summary = {}

    # get data drom ingredients list
    nutritional_data = {
        item['ingredient'].lower(): {
            "calories": float(item.get('calories', 0)),
            "protein": float(item.get('protein', 0)),
            "carbs": float(item.get('carbs', 0)),
            "fat": float(item.get('fat', 0)),
            "fiber": float(item.get('fiber', 0))
        }
        for item in ingredients
    }

    for recipe in selected_recipes:
        recipe_name = recipe['name']
        total_nutrition = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0}

        for ingredient in recipe['ingredients']:
            ingredient_lower = ingredient.lower()

            # Check if the ingredient exists
            if ingredient_lower in nutritional_data:
                nutrition_info = nutritional_data[ingredient_lower]

                # Sum nutritional values
                total_nutrition['calories'] += nutrition_info['calories']
                total_nutrition['protein'] += nutrition_info['protein']
                total_nutrition['carbs'] += nutrition_info['carbs']
                total_nutrition['fat'] += nutrition_info['fat']
                total_nutrition['fiber'] += nutrition_info['fiber']
            else:
                print(f"Warning: Nutritional data missing for {ingredient}")

        nutrition_summary[recipe_name] = total_nutrition

    return nutrition_summary


def create_meal_plan(selected_recipes_nutrition, selected_diet, output_filename='meal_plan.txt'):
    # Daily calorie limit from the selected diet with a ±200 range
    calorie_limit = selected_diet["nutritional_goals"]["calories"]
    lower_calorie_limit = calorie_limit - 200
    upper_calorie_limit = calorie_limit + 200

    # 7-day meal plan
    meal_plan = {day: [] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
    day_nutrition_totals = {day: {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0} for day in meal_plan}

    # List of available recipes
    recipes = list(selected_recipes_nutrition.items())

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
            recipe_name, nutrition = random.choice(recipes)  # Randomly select a recipe
            attempt_count += 1

            # Check if recipe already used for the day
            if recipe_name not in used_recipes:
                # Check if adding the recipe would keep within the upper calorie limit
                if day_nutrition_totals[day]["calories"] + nutrition["calories"] <= upper_calorie_limit:
                    # Add recipe to the current day
                    meal_plan[day].append(recipe_name)
                    used_recipes.add(recipe_name)  # Mark recipe as used

                    # Update nutritional totals for the day
                    for key in day_nutrition_totals[day]:
                        day_nutrition_totals[day][key] += nutrition[key]
                else:
                    break  # Stop adding if the upper calorie limit would be exceeded

    # Write meal plan to a file
    with open(output_filename, 'w') as file:
        for day, recipes in meal_plan.items():
            file.write(f"\n{day}:\n")
            if recipes:
                for recipe in recipes:
                    file.write(f"  - {recipe}\n")
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

def generate_shopping_list(meal_plan_file, recipes_file, ingredients_file, output_filename='meal_plan.txt'):
    # Load recipes and their ingredients
    recipes_ingredients = load_recipes_from_text(recipes_file)
    
    # Count occurrences of each recipe in the meal plan
    recipe_occurrences = count_recipe_occurrences(meal_plan_file)
    
    # Load ingredient data with quantities and units
    ingredients_data = load_ingredients(ingredients_file)
    ingredient_details = {
        item['ingredient'].lower(): {
            "quantity": float(item.get('quantity', 1)),
            "unit": item.get('unit', '')
        }
        for item in ingredients_data
    }

    # Aggregate ingredient occurrences
    shopping_list = {}
    for recipe, count in recipe_occurrences.items():
        if recipe in recipes_ingredients:
            for ingredient in recipes_ingredients[recipe]:
                ingredient_lower = ingredient.lower()
                if ingredient_lower in ingredient_details:
                    # Calculate total quantity based on recipe occurrence
                    total_quantity = count * ingredient_details[ingredient_lower]["quantity"]
                    unit = ingredient_details[ingredient_lower]["unit"]
                    
                    # Aggregate the quantities 
                    if ingredient_lower in shopping_list:
                        shopping_list[ingredient_lower]["total_quantity"] += total_quantity
                    else:
                        shopping_list[ingredient_lower] = {
                            "total_quantity": total_quantity,
                            "unit": unit
                        }
                else:
                    print(f"Warning: '{ingredient}' not found in ingredients data.")

    # Write shopping list same file
    with open(output_filename, 'a') as file:  # Append file
        file.write("\nShopping List:\n")
        for ingredient, details in shopping_list.items():
            file.write(f"{ingredient}: {details['total_quantity']} {details['unit']}\n")

    print("Shopping list generated and written to the output file.")

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
    # Load data files
    preferences = load_preferences('preferences.json')
    recipes = load_recipes('recipes.txt')
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
    selected_recipes = pick_from_sorted(recommended_recipes, preferences)
    
    
    selected_recipes_nutrition = calculate_nutrition(selected_recipes, ingredients)
    #print(selected_recipes_nutrition)
    
    #creates semi random meal plan with nutrition and selected diet in mind
    day_nutrition_totals=create_meal_plan(selected_recipes_nutrition, selected_diet)
    
    #generates shopping list based on # of occurences of ingredient 
    generate_shopping_list('meal_plan.txt', 'recipes.txt', 'ingredients.csv')
    
    #uses matplot to plot the daily nutrients 
    plot_day_nutrition_totals(day_nutrition_totals)
    
if __name__ == "__main__":
    main()

'''Final thoughts: this is basic and creates the semi-random meal plan based on a calorie limiter. Could
implement a limiter for different nutritional values. SHOULD have started from "selected_diet before continuing
on. Some of the menu items repeat within the same day, maybe dont allow that? larger input sets would help
smooth out output.DATA on ingredients/preferences could be tweaked to be more realistic on food intake. Lost team
member late in the game.
-restraints for meal planner can be tightened from the .json
-or using the lower_limit and upper_limit on calories
-or by adjusting the MAX counter to give more attempts at filling the caloric restraints
-meal planner currently focuses on calories '''



