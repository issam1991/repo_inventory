from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os
import hashlib

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database initialization
def init_db():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            permissions TEXT NOT NULL
        )
    ''')
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category_id INTEGER,
            quantity INTEGER DEFAULT 0,
            price REAL DEFAULT 0,
            min_stock INTEGER DEFAULT 0,
            description TEXT,
            FOREIGN KEY (category_id) REFERENCES categories (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            product_name TEXT,
            type TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            reason TEXT,
            user TEXT,
            date TEXT,
            comment TEXT,
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')
    
    # Insert default users if users table is empty
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        # Hash passwords using SHA-256
        admin_password_hash = hashlib.sha256('1234'.encode()).hexdigest()
        employee_password_hash = hashlib.sha256('0000'.encode()).hexdigest()
        
        default_users = [
            ('admin', 'Admin', 'Administrateur', admin_password_hash, 'all'),
            ('employee1', 'Marie', 'Employée', employee_password_hash, 'quick-entry,quick-exit'),
            ('employee2', 'Pierre', 'Employé', employee_password_hash, 'quick-entry,quick-exit')
        ]
        cursor.executemany('INSERT INTO users (id, name, role, password_hash, permissions) VALUES (?, ?, ?, ?, ?)', default_users)
    
    # Insert sample data if tables are empty
    cursor.execute('SELECT COUNT(*) FROM categories')
    if cursor.fetchone()[0] == 0:
        sample_categories = [
            ('Électronique', 'Appareils électroniques et accessoires'),
            ('Vêtements', 'Vêtements et accessoires de mode'),
            ('Alimentaire', 'Produits alimentaires et boissons'),
            ('Maison', 'Articles pour la maison'),
            ('Sport', 'Équipements sportifs')
        ]
        cursor.executemany('INSERT INTO categories (name, description) VALUES (?, ?)', sample_categories)
        
        # Insert sample products
        sample_products = [
            ('Smartphone Samsung A54', 1, 45, 349.99, 10, 'Smartphone Android 128GB'),
            ('Casque Bluetooth Sony', 1, 23, 89.99, 5, 'Casque sans fil avec réduction de bruit'),
            ('T-shirt Coton Bio', 2, 120, 24.99, 20, 'T-shirt unisexe 100% coton bio'),
            ('Jean Denim Classic', 2, 67, 59.99, 15, 'Jean coupe droite délavé'),
            ('Café Arabica 1kg', 3, 89, 18.50, 25, 'Café en grains origine Colombie'),
            ('Thé Vert Bio 100g', 3, 156, 12.99, 30, 'Thé vert biologique en vrac'),
            ('Aspirateur Robot', 4, 8, 299.99, 3, 'Robot aspirateur programmable'),
            ('Lampe LED Bureau', 4, 34, 45.99, 8, 'Lampe de bureau LED réglable'),
            ('Ballon Football', 5, 2, 29.99, 10, 'Ballon de football taille 5'),
            ('Raquette Tennis', 5, 0, 149.99, 5, 'Raquette de tennis professionnelle')
        ]
        cursor.executemany('''
            INSERT INTO products (name, category_id, quantity, price, min_stock, description) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', sample_products)
        
        # Insert sample movements
        sample_movements = [
            (1, 'Smartphone Samsung A54', 'entry', 50, 'Livraison fournisseur', 'Marie', datetime.now().isoformat(), 'Commande #12345'),
            (3, 'T-shirt Coton Bio', 'exit', 15, 'Vente client', 'Pierre', datetime.now().isoformat(), 'Commande magasin'),
            (5, 'Café Arabica 1kg', 'entry', 100, 'Livraison fournisseur', 'Admin', datetime.now().isoformat(), 'Réapprovisionnement mensuel')
        ]
        cursor.executemany('''
            INSERT INTO movements (product_id, product_name, type, quantity, reason, user, date, comment) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_movements)
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_db()

# Helper function to get database connection
def get_db_connection():
    conn = sqlite3.connect('inventory.db')
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

# Authentication helper functions
def hash_password(password):
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify a password against its hash"""
    return hash_password(password) == password_hash

# API Routes

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get('userId')
    password = data.get('password')
    
    if not user_id or not password:
        return jsonify({'error': 'User ID and password are required'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get user from database
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user and verify_password(password, user['password_hash']):
        # Convert permissions string to list
        permissions = user['permissions'].split(',')
        
        return jsonify({
            'id': user['id'],
            'name': user['name'],
            'role': user['role'],
            'permissions': permissions
        })
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/auth/users', methods=['GET'])
def get_users():
    """Get all users (for frontend dropdown)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, role FROM users ORDER BY name')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(users)

@app.route('/api/categories', methods=['GET'])
def get_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM categories ORDER BY name')
    categories = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(categories)

@app.route('/api/categories', methods=['POST'])
def create_category():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO categories (name, description) VALUES (?, ?)', 
                   (data['name'], data.get('description', '')))
    conn.commit()
    category_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': category_id, 'name': data['name'], 'description': data.get('description', '')}), 201

@app.route('/api/products', methods=['GET'])
def get_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, c.name as category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.id 
        ORDER BY p.name
    ''')
    products = []
    for row in cursor.fetchall():
        product = dict(row)
        # Add category field for compatibility with frontend
        product['category'] = product['category_name']
        products.append(product)
    conn.close()
    return jsonify(products)

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO products (name, category_id, quantity, price, min_stock, description) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data['name'], data['categoryId'], data['quantity'], data['price'], data['minStock'], data.get('description', '')))
    
    product_id = cursor.lastrowid
    
    # Get the created product with category name
    cursor.execute('''
        SELECT p.*, c.name as category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.id 
        WHERE p.id = ?
    ''', (product_id,))
    
    product = dict(cursor.fetchone())
    product['category'] = product['category_name']
    
    conn.commit()
    conn.close()
    return jsonify(product), 201

@app.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE products 
        SET name = ?, category_id = ?, quantity = ?, price = ?, min_stock = ?, description = ?
        WHERE id = ?
    ''', (data['name'], data['categoryId'], data['quantity'], data['price'], data['minStock'], data.get('description', ''), product_id))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Product not found'}), 404
    
    # Get the updated product with category name
    cursor.execute('''
        SELECT p.*, c.name as category_name 
        FROM products p 
        LEFT JOIN categories c ON p.category_id = c.id 
        WHERE p.id = ?
    ''', (product_id,))
    
    product = dict(cursor.fetchone())
    product['category'] = product['category_name']
    
    conn.commit()
    conn.close()
    return jsonify(product)

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if product exists
    cursor.execute('SELECT id FROM products WHERE id = ?', (product_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'Product not found'}), 404
    
    # Delete related movements first
    cursor.execute('DELETE FROM movements WHERE product_id = ?', (product_id,))
    
    # Delete the product
    cursor.execute('DELETE FROM products WHERE id = ?', (product_id,))
    
    conn.commit()
    conn.close()
    return jsonify({'message': 'Product deleted successfully'})

@app.route('/api/movements', methods=['GET'])
def get_movements():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM movements ORDER BY date DESC')
    movements = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(movements)

@app.route('/api/movements', methods=['POST'])
def create_movement():
    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create the movement
    cursor.execute('''
        INSERT INTO movements (product_id, product_name, type, quantity, reason, user, date, comment) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (data['productId'], data['productName'], data['type'], data['quantity'], 
          data['reason'], data['user'], data['date'], data.get('comment', '')))
    
    movement_id = cursor.lastrowid
    
    # Update product quantity
    if data['type'] == 'entry':
        cursor.execute('UPDATE products SET quantity = quantity + ? WHERE id = ?', 
                      (data['quantity'], data['productId']))
    else:  # exit
        cursor.execute('UPDATE products SET quantity = quantity - ? WHERE id = ?', 
                      (data['quantity'], data['productId']))
    
    # Get the created movement
    cursor.execute('SELECT * FROM movements WHERE id = ?', (movement_id,))
    movement = dict(cursor.fetchone())
    
    conn.commit()
    conn.close()
    return jsonify(movement), 201

@app.route('/api/dashboard', methods=['GET'])
def get_dashboard_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get total products
    cursor.execute('SELECT COUNT(*) as total FROM products')
    total_products = cursor.fetchone()['total']
    
    # Get low stock products
    cursor.execute('SELECT COUNT(*) as low_stock FROM products WHERE quantity <= min_stock AND quantity > 0')
    low_stock = cursor.fetchone()['low_stock']
    
    # Get out of stock products
    cursor.execute('SELECT COUNT(*) as out_stock FROM products WHERE quantity = 0')
    out_stock = cursor.fetchone()['out_stock']
    
    # Get total value
    cursor.execute('SELECT SUM(quantity * price) as total_value FROM products')
    total_value = cursor.fetchone()['total_value'] or 0
    
    # Get recent movements
    cursor.execute('SELECT * FROM movements ORDER BY date DESC LIMIT 5')
    recent_movements = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return jsonify({
        'total_products': total_products,
        'low_stock': low_stock,
        'out_stock': out_stock,
        'total_value': total_value,
        'recent_movements': recent_movements
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
