import json
from typing import List, Dict, Any

class CocktailDB:
    def __init__(self, json_file: str):
        """Initialize the database with the given JSON file."""
        with open(json_file, 'r', encoding='utf-8') as f:
            self.cocktails = json.load(f)
    
    def search_by_name(self, name: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search for cocktails by name."""
        results = []
        name = name if case_sensitive else name.lower()
        
        for cocktail in self.cocktails:
            cocktail_name = cocktail.get('strDrink', '')
            if not case_sensitive:
                cocktail_name = cocktail_name.lower()
            if name in cocktail_name:
                results.append(cocktail)
        return results
    
    def search_by_ingredient(self, ingredient: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search for cocktails containing a specific ingredient."""
        results = []
        ingredient = ingredient if case_sensitive else ingredient.lower()
        
        for cocktail in self.cocktails:
            # Check all ingredient fields (strIngredient1 through strIngredient15)
            for i in range(1, 16):
                ingredient_key = f'strIngredient{i}'
                if ingredient_key in cocktail and cocktail[ingredient_key]:
                    cocktail_ingredient = cocktail[ingredient_key]
                    if not case_sensitive:
                        cocktail_ingredient = cocktail_ingredient.lower()
                    if ingredient in cocktail_ingredient:
                        results.append(cocktail)
                        break  # No need to check other ingredients for this cocktail
        return results
    
    def search_by_category(self, category: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """Search for cocktails by category."""
        category = category if case_sensitive else category.lower()
        return [
            cocktail for cocktail in self.cocktails
            if cocktail.get('strCategory') and 
            (category in (cocktail['strCategory'].lower() if not case_sensitive else cocktail['strCategory']))
        ]

def print_cocktail(cocktail: Dict[str, Any]) -> None:
    """Print a formatted cocktail recipe."""
    print(f"\n{'='*50}")
    print(f"Name: {cocktail.get('strDrink', 'N/A')}")
    print(f"Category: {cocktail.get('strCategory', 'N/A')}")
    print(f"Glass: {cocktail.get('strGlass', 'N/A')}")
    print(f"Alcoholic: {cocktail.get('strAlcoholic', 'N/A')}")
    
    # Print ingredients and measures
    print("\nIngredients:")
    for i in range(1, 16):
        ingredient = cocktail.get(f'strIngredient{i}')
        if ingredient:  # Only process if ingredient exists
            measure = cocktail.get(f'strMeasure{i}')
            measure_str = measure.strip() if measure and measure.strip() else ''
            print(f"- {measure_str} {ingredient}" if measure_str else f"- {ingredient}")
    
    # Print instructions
    print("\nInstructions:")
    print(cocktail.get('strInstructions', 'No instructions available'))
    
    # Print image URL if available
    if cocktail.get('strDrinkThumb'):
        print(f"\nImage: {cocktail['strDrinkThumb']}")

def main():
    # Initialize the database
    try:
        db = CocktailDB('cocktaildb_dump.json')
        print("Cocktail database loaded successfully!")
    except Exception as e:
        print(f"Error loading database: {e}")
        return
    
    while True:
        print("\n=== Cocktail Search ===")
        print("1. Search by name")
        print("2. Search by ingredient")
        print("3. Search by category")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            name = input("Enter cocktail name (or part of it): ")
            results = db.search_by_name(name)
            print(f"\nFound {len(results)} cocktails matching '{name}':")
            
        elif choice == '2':
            ingredient = input("Enter ingredient name: ")
            results = db.search_by_ingredient(ingredient)
            print(f"\nFound {len(results)} cocktails with '{ingredient}':")
            
        elif choice == '3':
            category = input("Enter category (e.g., 'Cocktail', 'Ordinary Drink'): ")
            results = db.search_by_category(category)
            print(f"\nFound {len(results)} cocktails in category '{category}':")
            
        elif choice == '4':
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")
            continue
        
        # Display results
        if choice in ['1', '2', '3']:
            if not results:
                print("No results found.")
            else:
                for i, cocktail in enumerate(results, 1):
                    print(f"{i}. {cocktail.get('strDrink')}")
                
                view = input("\nEnter number to view details, or press Enter to continue: ")
                if view.isdigit() and 1 <= int(view) <= len(results):
                    print_cocktail(results[int(view)-1])
                    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
