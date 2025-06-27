from flask import Flask, render_template, request, jsonify
from cocktail_search import CocktailDB
import os

app = Flask(__name__)

# Initialize the database
db = CocktailDB('cocktaildb_dump.json')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    search_type = request.json.get('type')
    query = request.json.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Search query cannot be empty'}), 400
    
    try:
        if search_type == 'name':
            results = db.search_by_name(query)
        elif search_type == 'ingredient':
            results = db.search_by_ingredient(query)
        elif search_type == 'category':
            results = db.search_by_category(query)
        else:
            return jsonify({'error': 'Invalid search type'}), 400
            
        # Convert results to a list of dicts for JSON serialization
        cocktails = []
        for cocktail in results:
            # Get ingredients and measures
            ingredients = []
            for i in range(1, 16):
                ingredient = cocktail.get(f'strIngredient{i}')
                if ingredient:
                    measure = cocktail.get(f'strMeasure{i}', '').strip()
                    ingredients.append({
                        'ingredient': ingredient,
                        'measure': measure
                    })
            
            cocktails.append({
                'name': cocktail.get('strDrink', 'Unnamed Cocktail'),
                'category': cocktail.get('strCategory', 'N/A'),
                'glass': cocktail.get('strGlass', 'N/A'),
                'alcoholic': cocktail.get('strAlcoholic', 'N/A'),
                'instructions': cocktail.get('strInstructions', 'No instructions available'),
                'image': cocktail.get('strDrinkThumb', ''),
                'ingredients': ingredients
            })
            
        return jsonify({'results': cocktails})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
