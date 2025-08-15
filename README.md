# Inventory Management System

A full-stack inventory management application with a Flask backend and responsive HTML frontend.

## How to run
To run the Inventory Management System locally:

1. **Download the project files**  
   - Download or copy all files from this repository to a folder on your computer.

2. **Install Python dependencies**  
   Open a terminal in the project folder and run:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Flask backend**  
   In the same terminal, run:
   ```bash
   python app.py
   ```
   The backend will start on [http://127.0.0.1:5000](http://127.0.0.1:5000) by default.

4. **Open the frontend**  
   - Open the `repo_inventory.html` file in your web browser.
   - For best results, you can also serve the file using a local web server (e.g., `python -m http.server`) and visit [http://localhost:8000/repo_inventory.html](http://localhost:8000/repo_inventory.html).

5. **Login** using one of the default users listed below.

**Note:** No database setup is required; all data is stored in local JSON files by default.



## Features

- **Product Management**: Add, edit, delete products with categories
- **Stock Movements**: Track entries and exits with reasons and comments
- **Dashboard**: Real-time statistics and alerts
- **User Authentication**: Secure login with hashed passwords
- **Role-based Access**: Admin and Employee permissions
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Session Persistence**: Remembers user login and last viewed page

## Security Features

- **Password Hashing**: All passwords are hashed using SHA-256
- **Backend Authentication**: No hardcoded passwords in frontend
- **Session Management**: Secure client-side session storage
- **API-based**: All data operations go through secure API endpoints

## Default Users

The system comes with pre-configured users:

| User ID | Name | Role | Password | Permissions |
|---------|------|------|----------|-------------|
| admin | Admin | Administrateur | 1234 | All features |
| employee1 | Marie | Employée | 0000 | Quick entry/exit only |
| employee2 | Pierre | Employé | 0000 | Quick entry/exit only |

## Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Flask backend**:
   ```bash
   python app.py
   ```

3. **Open the frontend**:
   - Open `repo_inventory.html` in your web browser
   - Or serve it using a local web server

## API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `GET /api/auth/users` - Get all users

### Products
- `GET /api/products` - Get all products
- `POST /api/products` - Create new product
- `PUT /api/products/<id>` - Update product
- `DELETE /api/products/<id>` - Delete product

### Categories
- `GET /api/categories` - Get all categories
- `POST /api/categories` - Create new category

### Movements
- `GET /api/movements` - Get all movements
- `POST /api/movements` - Create new movement

### Dashboard
- `GET /api/dashboard` - Get dashboard statistics

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    permissions TEXT NOT NULL
);
```

### Products Table
```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    category_id INTEGER,
    quantity INTEGER DEFAULT 0,
    price REAL DEFAULT 0,
    min_stock INTEGER DEFAULT 0,
    description TEXT,
    FOREIGN KEY (category_id) REFERENCES categories (id)
);
```

### Categories Table
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT
);
```

### Movements Table
```sql
CREATE TABLE movements (
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
);
```

## Security Notes

- Passwords are hashed using SHA-256 before storage
- No passwords are stored in plain text
- Authentication is handled entirely on the backend
- Session data is stored in browser localStorage (consider using secure cookies for production)
- All API endpoints validate user permissions

## Usage

1. **Login**: Select your user and enter your password
2. **Dashboard**: View inventory statistics and recent activities
3. **Quick Entry/Exit**: Add or remove stock items quickly
4. **Products**: Manage product catalog (Admin only)
5. **Reports**: View movement history and analytics

## Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

The interface automatically adapts to screen size with appropriate navigation and layout changes.
