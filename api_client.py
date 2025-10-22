# smartplate/api_client.py
import requests
import json
from .ui.theme_manager import ThemeManager

class ApiClient:
    """Handles communication with the Spoonacular API (complexSearch endpoint)."""

    # ✅ Use the correct endpoint for searching recipes
    BASE_URL = "https://api.spoonacular.com/recipes/complexSearch"

    def __init__(self):
        # Key will be refreshed before each call
        pass

    def refresh_credentials(self):
        """Reload the Spoonacular API key dynamically."""
        # ✅ Use getter for Spoonacular key
        self.api_key = ThemeManager.get_spoonacular_api_key().strip()
        print(f"[ApiClient] Refreshed Spoonacular credentials: API Key='{self.api_key[:4]}...'")

    def analyze_natural(self, query):
        """Analyzes a meal description using Spoonacular complexSearch."""
        print(f"[ApiClient] Analyzing query with Spoonacular: '{query}'")
        if not query.strip(): return {"error": "Query cannot be empty."}

        self.refresh_credentials()

        if not self.api_key:
            print("[ApiClient] ERROR: Spoonacular API Key is missing.")
            return {"error": "Spoonacular API Key missing. Please save it in Settings."}

        params = {
            "apiKey": self.api_key,
            "query": query,
            "addRecipeNutrition": True, # Request nutritional info
            "number": 5,                # Get a few results to choose from
            "cuisine": "Indian,Asian,Middle Eastern,European,American", # Prioritize Indian, but allow others
            "fillIngredients": False,   # Don't need ingredient details now
            "addRecipeInformation": False # Don't need full recipe steps now
        }

        print(f"[ApiClient] Sending request to Spoonacular...")

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=15)
            print(f"[ApiClient] Spoonacular response status code: {response.status_code}")

            # --- Handle Spoonacular Error Codes ---
            if response.status_code == 401: # Auth failed
                print("[ApiClient] ERROR: 401 Authentication failed.")
                return {"error": "Invalid Spoonacular API Key. Please recheck and save."}
            if response.status_code == 402: # Quota exceeded
                print("[ApiClient] ERROR: 402 Payment Required (Quota Exceeded).")
                return {"error": "Spoonacular API quota exceeded for today."}
            if response.status_code >= 400: # Other errors
                 try: error_msg = response.json().get('message', response.text)
                 except: error_msg = response.text
                 print(f"[ApiClient] ERROR: {response.status_code} - {error_msg}")
                 return {"error": f"Spoonacular API Error {response.status_code}: {error_msg}"}

            # --- Process Successful Response ---
            result = response.json()
            recipes_data = result.get("results")

            if not recipes_data:
                 print("[ApiClient] No recipes found in Spoonacular results.")
                 return {"error": f"Spoonacular found no recipes matching '{query}'. Try different terms."}

            extracted_recipes = []
            for item in recipes_data:
                nutrients = item.get("nutrition", {}).get("nutrients", [])

                # Helper to find a nutrient by name
                def get_nutrient_val(name, unit='g'):
                    nutrient = next((n for n in nutrients if n.get("name") == name), None)
                    return nutrient.get("amount", 0) if nutrient else 0

                # Extract desired nutrients
                calories = get_nutrient_val('Calories', 'kcal')
                protein = get_nutrient_val('Protein', 'g')
                carbs = get_nutrient_val('Carbohydrates', 'g')
                fat = get_nutrient_val('Fat', 'g')
                fiber = get_nutrient_val('Fiber', 'g')
                sugar = get_nutrient_val('Sugar', 'g')
                sodium = get_nutrient_val('Sodium', 'mg')

                # Reformat into Edamam-like structure for consistency
                nutrients_reformatted = {
                    'ENERC_KCAL': {'quantity': calories, 'unit': 'kcal'},
                    'PROCNT': {'quantity': protein, 'unit': 'g'},
                    'CHOCDF': {'quantity': carbs, 'unit': 'g'},
                    'FAT': {'quantity': fat, 'unit': 'g'},
                    'FIBTG': {'quantity': fiber, 'unit': 'g'},
                    'SUGAR': {'quantity': sugar, 'unit': 'g'},
                    'NA': {'quantity': sodium, 'unit': 'mg'},
                }

                extracted_recipes.append({
                    "title": item.get("title", "Unknown Recipe"),
                    "calories": round(calories),
                    "nutrients": nutrients_reformatted
                })

            print(f"[ApiClient] Spoonacular analysis successful. Found {len(extracted_recipes)} recipes.")
            # Return *all* found recipes - MealLogPage needs update to handle multiple
            return {"recipes": extracted_recipes}

        # ... (keep exception handling as before) ...
        except requests.exceptions.Timeout: return {"error": "Request timed out."}
        except requests.exceptions.ConnectionError: return {"error": "Could not connect to Spoonacular API."}
        except json.JSONDecodeError: return {"error": f"Failed to parse response from Spoonacular: {response.text}"}
        except Exception as e: print(f"[ApiClient] Unexpected API error: {e}"); return {"error": "An unexpected error occurred."}