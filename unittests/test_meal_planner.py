import unittest
from project.main_menu import load_preferences, load_recipes, load_ingredients, pick_preference, recommend_recipes, create_meal_plan, generate_shopping_list

class TestMealPlanner(unittest.TestCase):

    # Test load_preferences function - WORKS
    def test_load_preferences(self):
        preferences = load_preferences('project/preferences.json')
        print(f"Loaded preferences: {preferences}")
        self.assertIn("user_preferences", preferences)

    # Test load_recipes function - WORKS
    def test_load_recipes(self):
        recipes = load_recipes('project/recipes.json')
        print(f"Loaded recipes: {recipes}")

    
    # Test load_ingredients function
    def test_load_ingredients(self):
        ingredients = load_ingredients('project/ingredients.csv')
        print(f"Loaded ingredients: {ingredients}")

    # Test pick_preference function - Works but might have to change if the edit calories changes
    def test_pick_preference(self):
        preferences = {
            "user_preferences": [
                {"diet": "omnivore", "nutritional_goals": {"calories": 2000}}
            ]
        }
        selected_diet = pick_preference(preferences)
        self.assertIsInstance(selected_diet, dict)
        self.assertEqual(selected_diet["diet"], "omnivore")

    
    # Test recommend_recipes function - Works
    def test_recommend_recipes(self):
        recipes = [
            {"name": "Potato Soup", "tags": ["All"], "ingredients": []},
            {"name": "Chicken Salad", "tags": ["Omni"], "ingredients": []}
        ]
        preferences = {"selected_preference": {"diet": "vegan"}}
        recommended = recommend_recipes(recipes, preferences)
        print(f"Recommended recipes: {[recipe['name'] for recipe in recommended]}") # should print Potato Soup


    # Test create_meal_plan function - Works, but not enough ingredients
    def test_create_meal_plan(self):
        recipes = [
            {"name": "Beans and Rice", "nutrition": {"calories": 431, "protein": 19.2, "carbs": 85.2, "fat": 1.3, "fiber": 15.6}},
            {"name": "Garlic Potato", "nutrition": {"calories": 167.5, "protein": 4.5, "carbs": 39, "fat": 0.3, "fiber": 5.4}}
        ]
        selected_diet = {"user_preferences": {"vegan"}, "nutritional_goals":{"calories": 1400, "protein": 60, "carbs": 210, "fat": 50, "fiber": 35}}
        meal_plan = create_meal_plan(recipes, selected_diet)
        self.assertEqual(len(meal_plan), 7)  # Meal plan should have 7 days
    
if __name__ == '__main__':
    unittest.main()
