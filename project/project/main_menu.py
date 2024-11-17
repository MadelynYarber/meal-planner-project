import sys
import json
import csv
import random

def load_preferences(filename: str):
    try:
        with open(filename, mode='r') as file:
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
        print("Recipes loaded successfully.\n")  # Temporary print validation
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
        print("Ingredients loaded successfully.\n")  # Temporary validation print
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
    selected_preference = pick_preference(preferences)
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
    for recipe in sorted_recipes:
        ingredients_list = ", ".join(recipe["ingredients"])  # Join ingredients into string
        print(f"- {recipe['name']} (Ingredients: {len(recipe['ingredients'])})")
        print(f"  Ingredients: {ingredients_list}\n")
    
    return sorted_recipes
#used in meal_plan
def pick_from_sorted(recipes, preferences):
    # Get the sorted list of recommended recipes
    recommended_recipes = recommend_recipes(recipes, preferences)
    
    if not recommended_recipes:
        print("No recommended recipes available.")
        return []

    selected_recipes = []  # List to store the selected recipes
    available_recipes = recommended_recipes[:]  # Copy of recommended recipes to track remaining options

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
    # Daily calorie limit from the selected diet
    calorie_limit = selected_diet["nutritional_goals"]["calories"]

    # 7-day meal plan
    meal_plan = {day: [] for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]}
    day_nutrition_totals = {day: {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0} for day in meal_plan}

    # List of available recipes
    recipes = list(selected_recipes_nutrition.items())

    # Meal plan random no repeats for each day
    for day in meal_plan.keys():
        used_recipes = set()  # Track used recipes for the day
        while day_nutrition_totals[day]["calories"] < calorie_limit:
            recipe_name, nutrition = random.choice(recipes)  # Randomly select a recipe

            # Check if recipe already used daily
            if recipe_name not in used_recipes:
                # Check if adding the recipe would exceed the calorie limit
                if day_nutrition_totals[day]["calories"] + nutrition["calories"] <= calorie_limit:
                    # Add recipe to the current day
                    meal_plan[day].append(recipe_name)
                    used_recipes.add(recipe_name)  # Mark recipe as used

                    # Update nutritional totals for the day
                    for key in day_nutrition_totals[day]:
                        day_nutrition_totals[day][key] += nutrition[key]
                else:
                    break  # Stop adding if the calorie limit would be exceeded

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

def generate_shopping_list(meal_plan_file, recipes_file, output_filename='meal_plan.txt'):
    #Load recipes and their ingredients
    recipes_ingredients = load_recipes_from_text(recipes_file)
    
    #Count times appears in the meal plan
    recipe_occurrences = count_recipe_occurrences(meal_plan_file)

    #Aggregate ingredient occurrences
    shopping_list = Counter()
    for recipe, count in recipe_occurrences.items():
        if recipe in recipes_ingredients:
            for ingredient in recipes_ingredients[recipe]:
                shopping_list[ingredient] += count
        else:
            print(f"Warning: '{recipe}' not found in recipes_ingredients.")

    #Write to the file meal_plan.txt for call after meal planned
    with open(output_filename, 'a') as file:  # Append to existing file
        file.write("\nShopping List:\n")
        for ingredient, count in shopping_list.items():
            file.write(f"{ingredient}: {count}x\n")

    print("Shopping list generated to the output file.")

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

    #Recommend recipes based on user preference
    print("recipes recommended by preference")
    recommended_recipes = recommend_recipes(recipes, preferences)
    
    
    #Allow the user to pick recipes for meal planning
    print("select preference to see available recipes")
    selected_recipes = pick_from_sorted(recommended_recipes, preferences)
    #print (selected_recipes)
    
    selected_recipes_nutrition = calculate_nutrition(selected_recipes, ingredients)
    #print(selected_recipes_nutrition)
    
    #creates semi random meal plan with nutrition and selected diet in mind
    create_meal_plan(selected_recipes_nutrition, selected_diet)
    
    #generates shopping list based on # of occurences of ingredient 
    generate_shopping_list('meal_plan.txt', 'recipes.txt')
    
if __name__ == "__main__":
    main()

'''Final thoughts: this is basic and creates the semi-random meal plan based on a calorie limiter. Could
implement a limiter for different nutritional values. SHOULD have started from "selected_diet before continuing
on. Some of the menu items repeat within the same day, maybe dont allow that? larger input sets would help
smooth out output.DATA on ingredients/preferences could be tweaked to be more realistic on food intake. Lost team
member late in the game. '''



