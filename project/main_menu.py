import sys
import json
import csv
import random

def load_preferences(filename: str):
    try:
        with open(filename, mode='r') as file:
            preferences = json.load(file)
        print("Preferences loaded successfully.\n")  # Temporary print for validation
        #print(preferences)  #delete these lines later
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
                # Ignore empty lines
                line = line.strip()
                if not line:
                    continue
                
                # get name, tags, and ingredients
                try:
                    name, rest = line.split(":", 1)
                    tags, ingredients = rest.split("}{")
                    
                    # Clean data
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
        print("Recipes loaded successfully.\n")  # Temporary print for validation
        #print(recipes)  # Delete this line later if not needed
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
                # Each row is a dictionary where keys are column headers
                ingredients.append({key.strip(): value.strip() for key, value in row.items()})
        print("Ingredients loaded successfully.\n")  # Temporary print for validation
        #print(ingredients)  # Delete this line later if not needed
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

    # Filter recipes based on diet preference (case-insensitive comparison)
    filtered_recipes = [
        recipe for recipe in recipes
        if tag_to_match.lower() in [tag.lower() for tag in recipe["tags"]] or "all" in [tag.lower() for tag in recipe["tags"]]
    ]
    
    #Sorting by the number of ingredients (ascending)
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

                # Sum up the nutritional values
                total_nutrition['calories'] += nutrition_info['calories']
                total_nutrition['protein'] += nutrition_info['protein']
                total_nutrition['carbs'] += nutrition_info['carbs']
                total_nutrition['fat'] += nutrition_info['fat']
                total_nutrition['fiber'] += nutrition_info['fiber']
            else:
                print(f"Warning: Nutritional data missing for {ingredient}")

        nutrition_summary[recipe_name] = total_nutrition

    return nutrition_summary



def main():
    # Load data files
    preferences = load_preferences('preferences.json')
    recipes = load_recipes('recipes.txt')
    ingredients = load_ingredients('ingredients.csv')
    
    #revelation starts here!!!!
    selected_diet = pick_preference(preferences)
    print(selected_diet)
    #^^^ can then pass selected diet instead go back and fix
    #Recommend recipes based on user preference
    print("recipes recommended by preference")
    recommended_recipes = recommend_recipes(recipes, preferences)
    
    
    #Allow the user to pick recipes for meal planning
    print("select preference to see available recipes")
    selected_recipes = pick_from_sorted(recommended_recipes, preferences)
    print (selected_recipes)
    
    selected_recipes_nutrition = calculate_nutrition(selected_recipes, ingredients)
    
if __name__ == "__main__":
    main()

'''go forward with rewrtiging functions calling selected_diet from line 265 down need rewrite
fix nutritional. and make it call less
ALL The loads are good. just need to fix things after pick_preference
'''



