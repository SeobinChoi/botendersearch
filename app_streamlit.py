import streamlit as st
import json
from cocktail_search import CocktailDB
from PIL import Image
import requests
from io import BytesIO

# Set page config
st.set_page_config(
    page_title="Cocktail Search",
    page_icon="🍹",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize the database
db = CocktailDB('cocktaildb_dump.json')

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .cocktail-card {
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s;
    }
    .cocktail-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .stButton>button {
        width: 100%;
    }
    .ingredient-list {
        margin: 0.5rem 0;
        padding-left: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar for search options
with st.sidebar:
    st.title("🍹 Cocktail Search")
    
    search_type = st.radio(
        "Search by:",
        ["Name", "Ingredient", "Category"]
    )
    
    search_query = st.text_input(
        f"Enter {search_type.lower()} to search",
        placeholder=f"e.g. {'margarita' if search_type == 'Name' else 'tequila' if search_type == 'Ingredient' else 'cocktail'}"
    )
    
    search_button = st.button("Search")

# Main content
st.title("🍹 Cocktail Search")

if search_button and search_query:
    with st.spinner(f'Searching for cocktails with {search_type.lower()}: {search_query}...'):
        if search_type == "Name":
            results = db.search_by_name(search_query)
        elif search_type == "Ingredient":
            results = db.search_by_ingredient(search_query)
        else:  # Category
            results = db.search_by_category(search_query)
            
        if not results:
            st.warning(f"No cocktails found matching your search: {search_query}")
        else:
            st.success(f"Found {len(results)} cocktail{'s' if len(results) > 1 else ''}:")
            
            # Display results in a grid
            cols = st.columns(3)
            for i, cocktail in enumerate(results):
                with cols[i % 3]:
                    with st.container():
                        st.markdown(f"### {cocktail.get('strDrink', 'Unnamed Cocktail')}")
                        
                        # Display image if available
                        if cocktail.get('strDrinkThumb'):
                            try:
                                response = requests.get(cocktail['strDrinkThumb'])
                                img = Image.open(BytesIO(response.content))
                                st.image(img, use_column_width=True)
                            except:
                                st.image("https://via.placeholder.com/300x200?text=No+Image", 
                                       use_column_width=True)
                        
                        # Basic info
                        st.caption(f"**Category:** {cocktail.get('strCategory', 'N/A')}")
                        st.caption(f"**Glass:** {cocktail.get('strGlass', 'N/A')}")
                        
                        # Ingredients
                        ingredients = []
                        for j in range(1, 16):
                            ingredient = cocktail.get(f'strIngredient{j}')
                            if ingredient:
                                measure = cocktail.get(f'strMeasure{j}', '').strip()
                                ingredients.append(f"- {measure} {ingredient}" if measure else f"- {ingredient}")
                        
                        with st.expander("View Ingredients"):
                            st.markdown("\n".join(ingredients))
                        
                        # Instructions
                        with st.expander("View Instructions"):
                            st.write(cocktail.get('strInstructions', 'No instructions available'))
                        
                        st.markdown("---")

# Show instructions if no search has been performed
elif not search_button:
    st.markdown("""
    ### Welcome to Cocktail Search! 🍸
    
    Use the sidebar to search for cocktails by:
    - **Name**: Find cocktails by their name
    - **Ingredient**: Discover cocktails that use a specific ingredient
    - **Category**: Browse cocktails by category
    
    Simply enter your search term and click the "Search" button to get started!
    """)
    
    # Display some featured cocktails
    st.markdown("### Featured Cocktails")
    featured = db.search_by_name("", case_sensitive=False)[:6]  # Get first 6 cocktails
    
    if featured:
        cols = st.columns(3)
        for i, cocktail in enumerate(featured):
            with cols[i % 3]:
                st.markdown(f"**{cocktail.get('strDrink', 'Unnamed Cocktail')}**")
                if cocktail.get('strDrinkThumb'):
                    try:
                        response = requests.get(cocktail['strDrinkThumb'])
                        img = Image.open(BytesIO(response.content))
                        st.image(img, use_column_width=True)
                    except:
                        st.image("https://via.placeholder.com/300x200?text=No+Image", 
                               use_column_width=True)
                st.markdown(f"*{cocktail.get('strCategory', 'Cocktail')}*")
                st.markdown("---")
