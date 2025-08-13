// API Base URL
const API_BASE_URL = 'http://localhost:5000/api';

// API Functions
async function apiRequest(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        showNotification('Erreur de connexion au serveur', 'error');
        throw error;
    }
}

// Categories API
async function loadCategories() {
    try {
        categories = await apiRequest('/categories');
        return categories;
    } catch (error) {
        console.error('Failed to load categories:', error);
        return [];
    }
}

async function createCategory(categoryData) {
    try {
        const newCategory = await apiRequest('/categories', {
            method: 'POST',
            body: JSON.stringify(categoryData)
        });
        categories.push(newCategory);
        return newCategory;
    } catch (error) {
        console.error('Failed to create category:', error);
        throw error;
    }
}

// Products API
async function loadProducts() {
    try {
        products = await apiRequest('/products');
        return products;
    } catch (error) {
        console.error('Failed to load products:', error);
        return [];
    }
}

async function createProduct(productData) {
    try {
        const newProduct = await apiRequest('/products', {
            method: 'POST',
            body: JSON.stringify(productData)
        });
        products.push(newProduct);
        return newProduct;
    } catch (error) {
        console.error('Failed to create product:', error);
        throw error;
    }
}

async function updateProduct(productId, productData) {
    try {
        const updatedProduct = await apiRequest(`/products/${productId}`, {
            method: 'PUT',
            body: JSON.stringify(productData)
        });
        
        const index = products.findIndex(p => p.id === productId);
        if (index !== -1) {
            products[index] = updatedProduct;
        }
        
        return updatedProduct;
    } catch (error) {
        console.error('Failed to update product:', error);
        throw error;
    }
}

async function deleteProduct(productId) {
    try {
        await apiRequest(`/products/${productId}`, {
            method: 'DELETE'
        });
        
        const index = products.findIndex(p => p.id === productId);
        if (index !== -1) {
            products.splice(index, 1);
        }
        
        return true;
    } catch (error) {
        console.error('Failed to delete product:', error);
        throw error;
    }
}

// Movements API
async function loadMovements() {
    try {
        movements = await apiRequest('/movements');
        return movements;
    } catch (error) {
        console.error('Failed to load movements:', error);
        return [];
    }
}

async function createMovement(movementData) {
    try {
        const newMovement = await apiRequest('/movements', {
            method: 'POST',
            body: JSON.stringify(movementData)
        });
        movements.unshift(newMovement); // Add to beginning for recent movements
        return newMovement;
    } catch (error) {
        console.error('Failed to create movement:', error);
        throw error;
    }
}

// Dashboard API
async function loadDashboardData() {
    try {
        const dashboardData = await apiRequest('/dashboard');
        return dashboardData;
    } catch (error) {
        console.error('Failed to load dashboard data:', error);
        return {
            total_products: 0,
            low_stock: 0,
            out_stock: 0,
            total_value: 0,
            recent_movements: []
        };
    }
}

// Updated initialization function
async function initializeApp() {
    try {
        // Load all data from API
        await Promise.all([
            loadCategories(),
            loadProducts(),
            loadMovements()
        ]);
        
        // Update UI
        updateDashboard();
        populateSelects();
        
        // Show success message
        showNotification('✅ Données chargées avec succès', 'success');
    } catch (error) {
        console.error('Failed to initialize app:', error);
        showNotification('❌ Erreur lors du chargement des données', 'error');
    }
}

// Updated product management functions
async function handleProductSubmit(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('productName').value,
        categoryId: parseInt(document.getElementById('productCategory').value),
        quantity: parseInt(document.getElementById('productQuantity').value),
        price: parseFloat(document.getElementById('productPrice').value) || 0,
        minStock: parseInt(document.getElementById('productMinStock').value) || 0,
        description: document.getElementById('productDescription').value
    };
    
    try {
        if (currentProductId) {
            await updateProduct(currentProductId, formData);
            showNotification('✅ Article modifié avec succès', 'success');
        } else {
            await createProduct(formData);
            showNotification('✅ Article ajouté avec succès', 'success');
        }
        
        closeProductModal();
        updateDashboard();
        populateSelects();
        if (currentPage === 'inventory') {
            renderInventory();
        }
    } catch (error) {
        showNotification('❌ Erreur lors de la sauvegarde', 'error');
    }
}

// Updated movement functions
async function handleQuickEntry(e) {
    e.preventDefault();
    
    const productId = parseInt(document.getElementById('quickEntryProduct').value);
    const quantity = parseInt(document.getElementById('quickEntryQuantity').value);
    const reason = document.getElementById('quickEntryReason').value;
    
    const product = products.find(p => p.id === productId);
    if (!product) return;
    
    showConfirmModal(
        `Confirmer l'ajout de ${quantity} unités de "${product.name}" ?`,
        async () => {
            try {
                const movementData = {
                    productId: productId,
                    productName: product.name,
                    type: 'entry',
                    quantity: quantity,
                    reason: reason,
                    user: currentUser.name,
                    date: new Date().toISOString(),
                    comment: 'Entrée rapide'
                };
                
                await createMovement(movementData);
                
                // Update local product quantity
                product.quantity += quantity;
                
                // Reset form
                resetQuickEntry();
                
                // Update UI
                updateDashboard();
                
                showNotification(`✅ Ajouté avec succès: +${quantity} ${product.name}`, 'success');
                
                // Focus back on search for next entry
                setTimeout(() => {
                    document.getElementById('quickEntrySearch').focus();
                }, 100);
            } catch (error) {
                showNotification('❌ Erreur lors de l\'ajout', 'error');
            }
        }
    );
}

async function handleQuickExit(e) {
    e.preventDefault();
    
    const productId = parseInt(document.getElementById('quickExitProduct').value);
    const quantity = parseInt(document.getElementById('quickExitQuantity').value);
    const reason = document.getElementById('quickExitReason').value;
    
    const product = products.find(p => p.id === productId);
    if (!product || product.quantity < quantity) {
        showNotification('❌ Stock insuffisant', 'error');
        return;
    }
    
    showConfirmModal(
        `Confirmer le retrait de ${quantity} unités de "${product.name}" ?`,
        async () => {
            try {
                const movementData = {
                    productId: productId,
                    productName: product.name,
                    type: 'exit',
                    quantity: quantity,
                    reason: reason,
                    user: currentUser.name,
                    date: new Date().toISOString(),
                    comment: 'Sortie rapide'
                };
                
                await createMovement(movementData);
                
                // Update local product quantity
                product.quantity -= quantity;
                
                // Reset form
                resetQuickExit();
                
                // Update UI
                updateDashboard();
                
                showNotification(`✅ Retiré avec succès: -${quantity} ${product.name}`, 'success');
                
                // Focus back on search for next exit
                setTimeout(() => {
                    document.getElementById('quickExitSearch').focus();
                }, 100);
            } catch (error) {
                showNotification('❌ Erreur lors du retrait', 'error');
            }
        }
    );
}

// Updated dashboard function
async function updateDashboard() {
    try {
        const dashboardData = await loadDashboardData();
        
        // Update dashboard cards
        document.getElementById('totalProducts').textContent = dashboardData.total_products;
        document.getElementById('lowStockProducts').textContent = dashboardData.low_stock;
        document.getElementById('outOfStockProducts').textContent = dashboardData.out_stock;
        document.getElementById('totalValue').textContent = `€${dashboardData.total_value.toFixed(2)}`;
        
        // Update recent movements
        const recentMovementsContainer = document.getElementById('recentMovements');
        if (recentMovementsContainer) {
            recentMovementsContainer.innerHTML = dashboardData.recent_movements.map(movement => `
                <div class="flex items-center justify-between py-2 border-b border-gray-100 last:border-b-0">
                    <div class="flex-1">
                        <div class="flex items-center space-x-2">
                            <span class="text-sm font-medium text-gray-900">${movement.product_name}</span>
                            <span class="px-2 py-1 text-xs font-medium rounded-full ${
                                movement.type === 'entry' 
                                    ? 'bg-green-100 text-green-800' 
                                    : 'bg-red-100 text-red-800'
                            }">
                                ${movement.type === 'entry' ? '+' : '-'}${movement.quantity}
                            </span>
                        </div>
                        <div class="text-xs text-gray-500">
                            ${movement.reason} • ${movement.user} • ${new Date(movement.date).toLocaleDateString()}
                        </div>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to update dashboard:', error);
    }
}
