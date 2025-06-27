import streamlit as st
import json
from PIL import Image
import requests
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="🍹 Cocktail Explorer",
    page_icon="🍹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 1rem;
    }
    .cocktail-card {
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
        cursor: pointer;
    }
    .cocktail-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .ingredient-list {
        margin: 0.5rem 0;
        padding-left: 1.2rem;
    }
    .instructions {
        white-space: pre-line;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

class CocktailDB:
    def __init__(self, json_file):
        """Initialize the database with the given JSON file."""
        with open(json_file, 'r', encoding='utf-8') as f:
            self.cocktails = json.load(f)
    
    def search_by_name(self, name, case_sensitive=False):
        """Search for cocktails by name."""
        name = name if case_sensitive else name.lower()
        return [
            cocktail for cocktail in self.cocktails
            if name in (cocktail['strDrink'].lower() if not case_sensitive else cocktail['strDrink'])
        ]
    
    def search_by_ingredient(self, ingredient, case_sensitive=False):
        """Search for cocktails containing a specific ingredient."""
        ingredient = ingredient if case_sensitive else ingredient.lower()
        results = []
        
        for cocktail in self.cocktails:
            for i in range(1, 16):
                ingredient_key = f'strIngredient{i}'
                if ingredient_key in cocktail and cocktail[ingredient_key]:
                    cocktail_ingredient = cocktail[ingredient_key]
                    if not case_sensitive:
                        cocktail_ingredient = cocktail_ingredient.lower()
                    if ingredient in cocktail_ingredient:
                        results.append(cocktail)
                        break
        return results
    
    def search_by_category(self, category, case_sensitive=False):
        """Search for cocktails by category."""
        category = category if case_sensitive else category.lower()
        return [
            cocktail for cocktail in self.cocktails
            if cocktail.get('strCategory') and 
            (category in (cocktail['strCategory'].lower() if not case_sensitive else cocktail['strCategory']))
        ]
    
    def get_cocktail_by_id(self, drink_id):
        """Get a cocktail by its ID."""
        for cocktail in self.cocktails:
            if cocktail.get('idDrink') == drink_id:
                return cocktail
        return None

# Initialize the database
db = CocktailDB('cocktaildb_dump.json')

# Session state to track the current view
if 'view' not in st.session_state:
    st.session_state.view = 'search'  # 'search' or 'detail'
    st.session_state.current_cocktail = None

def show_cocktail_detail(cocktail):
    """Display detailed view of a single cocktail."""
    st.session_state.view = 'detail'
    st.session_state.current_cocktail = cocktail

def show_search():
    """Display the search interface."""
    st.session_state.view = 'search'
    st.session_state.current_cocktail = None

def display_cocktail_detail(cocktail):
    """Render the cocktail detail view."""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Display cocktail image
        if cocktail.get('strDrinkThumb'):
            try:
                response = requests.get(cocktail['strDrinkThumb'])
                img = Image.open(BytesIO(response.content))
                st.image(img, use_container_width=True, caption=cocktail.get('strDrink', ''))
            except:
                st.image("https://via.placeholder.com/400x400?text=No+Image", 
                        use_container_width=True)
        else:
            st.image("https://via.placeholder.com/400x400?text=No+Image", 
                    use_container_width=True)
    
    with col2:
        st.title(cocktail.get('strDrink', 'Unnamed Cocktail'))
        
        # Basic info
        st.subheader("📋 Details")
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            st.metric("Category", cocktail.get('strCategory', 'N/A'))
            st.metric("Glass", cocktail.get('strGlass', 'N/A'))
        with col_info2:
            st.metric("Alcoholic", cocktail.get('strAlcoholic', 'N/A'))
            if cocktail.get('strIBA'):
                st.metric("IBA", cocktail.get('strIBA'))
        
        # Ingredients
        st.subheader("🥄 Ingredients")
        ingredients = []
        for i in range(1, 16):
            ingredient = cocktail.get(f'strIngredient{i}')
            if ingredient:
                measure = cocktail.get(f'strMeasure{i}')
                measure_str = measure.strip() if measure and isinstance(measure, str) else ''
                ingredients.append(f"- {measure_str} {ingredient}" if measure_str else f"- {ingredient}")
        
        st.markdown("\n".join(ingredients))
        
        # Instructions
        st.subheader("📝 Instructions")
        st.markdown(f"<div class='instructions'>{cocktail.get('strInstructions', 'No instructions available')}</div>", 
                   unsafe_allow_html=True)
        
        # Tags
        if cocktail.get('strTags'):
            st.subheader("🏷️ Tags")
            tags = [tag.strip() for tag in cocktail['strTags'].split(',')]
            st.write(" ".join([f"`{tag}`" for tag in tags]))
        
        # Back button
        st.button("← Back to Search", on_click=show_search)

def display_search():
    """Render the search interface."""
    st.title("🍹 Cocktail Explorer")
    
    # Search bar
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Search for cocktails by name or ingredient", 
                                   placeholder="e.g., Margarita or Tequila")
    with col2:
        search_type = st.selectbox("Search by", ["Name", "Ingredient"])
    
    # Search button
    if st.button("Search") or search_query:
        if search_query.strip():
            if search_type == "Name":
                results = db.search_by_name(search_query)
            else:
                results = db.search_by_ingredient(search_query)
            
            if not results:
                st.warning("No cocktails found matching your search.")
            else:
                st.success(f"Found {len(results)} cocktail{'s' if len(results) > 1 else ''}:")
                
                # Display results in a grid
                cols = st.columns(3)
                for i, cocktail in enumerate(results):
                    with cols[i % 3]:
                        with st.container():
                            # Create a clickable card
                            card = st.container()
                            with card:
                                # Display cocktail image
                                if cocktail.get('strDrinkThumb'):
                                    try:
                                        response = requests.get(cocktail['strDrinkThumb'])
                                        img = Image.open(BytesIO(response.content))
                                        st.image(img, use_container_width=True)
                                    except:
                                        st.image("https://via.placeholder.com/300x200?text=No+Image", 
                                               use_container_width=True)
                                else:
                                    st.image("https://via.placeholder.com/300x200?text=No+Image", 
                                           use_container_width=True)
                                
                                # Cocktail name and category
                                st.write(f"**{cocktail.get('strDrink', 'Unnamed Cocktail')}**")
                                st.caption(cocktail.get('strCategory', 'Cocktail'))
                                
                                # Make the whole card clickable
                                if st.button("View Recipe", key=f"view_{cocktail.get('idDrink')}", 
                                           use_container_width=True):
                                    show_cocktail_detail(cocktail)
                                
                                st.markdown("---")
        else:
            st.warning("Please enter a search term")
    else:
        # Show featured cocktails if no search
        st.markdown("### 🎉 Featured Cocktails")
        featured = db.search_by_name("", case_sensitive=False)[:6]
        
        if featured:
            cols = st.columns(3)
            for i, cocktail in enumerate(featured):
                with cols[i % 3]:
                    with st.container():
                        # Display cocktail image
                        if cocktail.get('strDrinkThumb'):
                            try:
                                response = requests.get(cocktail['strDrinkThumb'])
                                img = Image.open(BytesIO(response.content))
                                st.image(img, use_container_width=True)
                            except:
                                st.image("https://via.placeholder.com/300x200?text=No+Image", 
                                       use_container_width=True)
                        
                        # Cocktail name and category
                        st.write(f"**{cocktail.get('strDrink', 'Unnamed Cocktail')}**")
                        st.caption(cocktail.get('strCategory', 'Cocktail'))
                        
                        # View button
                        if st.button("View Recipe", 
                                   key=f"featured_{cocktail.get('idDrink')}",
                                   use_container_width=True):
                            show_cocktail_detail(cocktail)
                        
                        st.markdown("---")

# Main app logic
if st.session_state.view == 'search' or st.session_state.current_cocktail is None:
    display_search()
else:
    display_cocktail_detail(st.session_state.current_cocktail)
