document.addEventListener('DOMContentLoaded', function() {
    const searchButton = document.getElementById('searchButton');
    const searchQuery = document.getElementById('searchQuery');
    const searchType = document.getElementById('searchType');
    const resultsDiv = document.getElementById('results');
    const loadingDiv = document.getElementById('loading');
    
    // Initialize Bootstrap modal
    const cocktailModal = new bootstrap.Modal(document.getElementById('cocktailModal'));
    
    // Search when button is clicked or Enter is pressed
    searchButton.addEventListener('click', performSearch);
    searchQuery.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
    
    function performSearch() {
        const query = searchQuery.value.trim();
        const type = searchType.value;
        
        if (!query) {
            showAlert('Please enter a search term', 'warning');
            return;
        }
        
        // Show loading indicator
        loadingDiv.classList.remove('d-none');
        resultsDiv.innerHTML = '';
        
        // Make API request
        fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: type,
                query: query
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            displayResults(data.results);
        })
        .catch(error => {
            showAlert(error.message || 'An error occurred while searching', 'danger');
        })
        .finally(() => {
            loadingDiv.classList.add('d-none');
        });
    }
    
    function displayResults(cocktails) {
        resultsDiv.innerHTML = '';
        
        if (cocktails.length === 0) {
            showAlert('No cocktails found matching your search', 'info');
            return;
        }
        
        const resultsHeader = document.createElement('h3');
        resultsHeader.textContent = `Found ${cocktails.length} cocktail${cocktails.length !== 1 ? 's' : ''}:`;
        resultsDiv.appendChild(resultsHeader);
        
        const row = document.createElement('div');
        row.className = 'row row-cols-1 row-cols-md-2 g-4 mt-2';
        
        cocktails.forEach(cocktail => {
            const col = document.createElement('div');
            col.className = 'col';
            
            const card = document.createElement('div');
            card.className = 'card h-100';
            
            const image = document.createElement('img');
            image.src = cocktail.image || 'https://via.placeholder.com/300x200?text=No+Image';
            image.className = 'card-img-top';
            image.alt = cocktail.name;
            image.style.height = '200px';
            image.style.objectFit = 'cover';
            
            const cardBody = document.createElement('div');
            cardBody.className = 'card-body';
            
            const title = document.createElement('h5');
            title.className = 'card-title';
            title.textContent = cocktail.name;
            
            const category = document.createElement('p');
            category.className = 'card-text text-muted';
            category.textContent = cocktail.category;
            
            const viewButton = document.createElement('button');
            viewButton.className = 'btn btn-outline-primary btn-sm mt-2';
            viewButton.textContent = 'View Recipe';
            viewButton.onclick = () => showCocktailDetails(cocktail);
            
            cardBody.appendChild(title);
            cardBody.appendChild(category);
            cardBody.appendChild(viewButton);
            
            card.appendChild(image);
            card.appendChild(cardBody);
            col.appendChild(card);
            row.appendChild(col);
        });
        
        resultsDiv.appendChild(row);
    }
    
    function showCocktailDetails(cocktail) {
        document.getElementById('modalTitle').textContent = cocktail.name;
        
        const image = document.getElementById('modalImage');
        image.src = cocktail.image || 'https://via.placeholder.com/500x300?text=No+Image';
        image.alt = cocktail.name;
        
        document.getElementById('modalCategory').textContent = cocktail.category;
        document.getElementById('modalGlass').textContent = cocktail.glass;
        document.getElementById('modalAlcoholic').textContent = cocktail.alcoholic;
        document.getElementById('modalInstructions').textContent = cocktail.instructions;
        
        const ingredientsList = document.getElementById('modalIngredients');
        ingredientsList.innerHTML = '';
        
        cocktail.ingredients.forEach(item => {
            const li = document.createElement('li');
            li.className = 'list-group-item';
            li.textContent = `${item.measure ? item.measure + ' ' : ''}${item.ingredient}`;
            ingredientsList.appendChild(li);
        });
        
        cocktailModal.show();
    }
    
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.role = 'alert';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        resultsDiv.innerHTML = '';
        resultsDiv.appendChild(alertDiv);
    }
});
