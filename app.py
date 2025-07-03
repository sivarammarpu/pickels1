from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import boto3
from botocore.exceptions import ClientError
import hashlib
import uuid
from datetime import datetime
import os
from decimal import Decimal
import json
import threading

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

# AWS DynamoDB Configuration
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

# DynamoDB Tables
users_table = dynamodb.Table('pickle_users')
products_table = dynamodb.Table('pickle_products')
orders_table = dynamodb.Table('pickle_orders')
cart_table = dynamodb.Table('pickle_cart')

USERS_JSON_PATH = os.path.join(os.path.dirname(__file__), 'users.json')
USERS_JSON_LOCK = threading.Lock()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_sample_products():
    """Initialize sample products in DynamoDB"""
    sample_products = [
        {
            'id': '1',
            'name': 'Traditional Mango Pickle',
            'price': Decimal('299'),
            'original_price': Decimal('350'),
            'description': 'Authentic homemade mango pickle with traditional spices and mustard oil.',
            'category': 'vegetarian',
            'image': 'mango_pickle.jpg',
            'rating': Decimal('4.8'),
            'review_count': 124,
            'in_stock': True,
            'weight': '500g',
            'ingredients': 'Raw Mango, Mustard Oil, Red Chili, Turmeric, Salt, Fenugreek',
            'spice_level': 'medium',
            'featured': True
        },
        {
            'id': '2',
            'name': 'Spicy Lime Pickle',
            'price': Decimal('249'),
            'description': 'Tangy and spicy lime pickle perfect for all meals.',
            'category': 'vegetarian',
            'image': 'lime_pickle.jpg',
            'rating': Decimal('4.6'),
            'review_count': 89,
            'in_stock': True,
            'weight': '400g',
            'ingredients': 'Lime, Chili Powder, Salt, Turmeric, Asafoetida, Mustard Seeds',
            'spice_level': 'hot',
            'featured': True
        },
        {
            'id': '3',
            'name': 'Mixed Vegetable Pickle',
            'price': Decimal('329'),
            'description': 'A delightful mix of seasonal vegetables pickled with aromatic spices.',
            'category': 'vegetarian',
            'image': 'mixed_veg_pickle.jpg',
            'rating': Decimal('4.7'),
            'review_count': 156,
            'in_stock': True,
            'weight': '600g',
            'ingredients': 'Mixed Vegetables, Mustard Oil, Spices, Salt, Vinegar',
            'spice_level': 'medium'
        },
        {
            'id': '4',
            'name': 'Fish Pickle (Bengali Style)',
            'price': Decimal('449'),
            'original_price': Decimal('499'),
            'description': 'Traditional Bengali fish pickle made with fresh fish and mustard oil.',
            'category': 'non-vegetarian',
            'image': 'fish_pickle.jpg',
            'rating': Decimal('4.9'),
            'review_count': 203,
            'in_stock': True,
            'weight': '400g',
            'ingredients': 'Fresh Fish, Mustard Oil, Turmeric, Red Chili, Salt, Garlic',
            'spice_level': 'hot',
            'featured': True
        },
        {
            'id': '5',
            'name': 'Prawn Pickle',
            'price': Decimal('399'),
            'description': 'Coastal style prawn pickle with coconut and traditional spices.',
            'category': 'non-vegetarian',
            'image': 'prawn_pickle.jpg',
            'rating': Decimal('4.5'),
            'review_count': 78,
            'in_stock': True,
            'weight': '350g',
            'ingredients': 'Prawns, Coconut Oil, Curry Leaves, Tamarind, Spices',
            'spice_level': 'medium'
        },
        {
            'id': '6',
            'name': 'Garlic Pickle',
            'price': Decimal('199'),
            'description': 'Strong and flavorful garlic pickle that enhances any meal.',
            'category': 'vegetarian',
            'image': 'garlic_pickle.jpg',
            'rating': Decimal('4.4'),
            'review_count': 92,
            'in_stock': True,
            'weight': '300g',
            'ingredients': 'Garlic, Sesame Oil, Red Chili, Salt, Fenugreek',
            'spice_level': 'mild'
        },
        {
            'id': '7',
            'name': 'Chicken Pickle',
            'price': Decimal('499'),
            'description': 'Tender chicken pieces pickled with aromatic spices.',
            'category': 'non-vegetarian',
            'image': 'chicken_pickle.jpg',
            'rating': Decimal('4.8'),
            'review_count': 167,
            'in_stock': False,
            'weight': '450g',
            'ingredients': 'Chicken, Yogurt, Ginger-Garlic, Spices, Oil',
            'spice_level': 'hot'
        },
        {
            'id': '8',
            'name': 'Green Chili Pickle',
            'price': Decimal('179'),
            'description': 'Fresh green chilies pickled with mustard oil and spices.',
            'category': 'vegetarian',
            'image': 'green_chili_pickle.jpg',
            'rating': Decimal('4.3'),
            'review_count': 134,
            'in_stock': True,
            'weight': '250g',
            'ingredients': 'Green Chilies, Mustard Oil, Salt, Turmeric, Mustard Seeds',
            'spice_level': 'extra-hot',
            'featured': True
        }
    ]
    
    try:
        for product in sample_products:
            products_table.put_item(Item=product)
        print("Sample products initialized successfully!")
    except Exception as e:
        print(f"Error initializing products: {e}")

def get_all_products():
    """Get all products from DynamoDB"""
    try:
        response = products_table.scan()
        return response['Items']
    except Exception as e:
        print(f"Error fetching products: {e}")
        return []

def get_product_by_id(product_id):
    """Get a specific product by ID"""
    try:
        response = products_table.get_item(Key={'id': product_id})
        return response.get('Item')
    except Exception as e:
        print(f"Error fetching product: {e}")
        return None

def get_cart_items(user_id):
    """Get cart items for a user"""
    try:
        response = cart_table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
        )
        return response['Items']
    except Exception as e:
        print(f"Error fetching cart: {e}")
        return []

def read_local_users():
    if not os.path.exists(USERS_JSON_PATH):
        return []
    with USERS_JSON_LOCK, open(USERS_JSON_PATH, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return []

def write_local_users(users):
    with USERS_JSON_LOCK, open(USERS_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)

def find_local_user_by_email(email):
    users = read_local_users()
    for user in users:
        if user['email'] == email:
            return user
    return None

def add_local_user(user_data):
    users = read_local_users()
    users.append(user_data)
    write_local_users(users)

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/home')
def home():
    """Home page with all products"""
    products = get_all_products()
    return render_template('home.html', products=products)

@app.route('/veg_pickles')
def veg_pickles():
    """Vegetarian pickles page"""
    products = get_all_products()
    veg_products = [p for p in products if p.get('category') == 'vegetarian']
    return render_template('veg_pickles.html', products=veg_products)

@app.route('/non_veg_pickles')
def non_veg_pickles():
    """Non-vegetarian pickles page"""
    products = get_all_products()
    non_veg_products = [p for p in products if p.get('category') == 'non-vegetarian']
    return render_template('non_veg_pickles.html', products=non_veg_products)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User registration"""
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        phone = request.form.get('phone', '')
        # Check if user already exists (DynamoDB first, fallback to local)
        try:
            response = users_table.get_item(Key={'email': email})
            if 'Item' in response:
                flash('Email already registered. Please login.', 'error')
                return redirect(url_for('signup'))
        except Exception:
            # Fallback to local
            if find_local_user_by_email(email):
                flash('Email already registered. Please login.', 'error')
                return redirect(url_for('signup'))
        # Create new user
        user_data = {
            'id': str(uuid.uuid4()),
            'email': email,
            'name': name,
            'password': hash_password(password),
            'phone': phone,
            'created_at': datetime.now().isoformat()
        }
        try:
            users_table.put_item(Item=user_data)
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
        except Exception:
            # Fallback to local
            add_local_user(user_data)
            flash('Account created successfully! Please login. (Local)', 'success')
            return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            response = users_table.get_item(Key={'email': email})
            if 'Item' in response:
                user = response['Item']
                if user['password'] == hash_password(password):
                    session['user_id'] = user['id']
                    session['user_name'] = user['name']
                    session['user_email'] = user['email']
                    flash('Login successful!', 'success')
                    return redirect(url_for('home'))
                else:
                    flash('Invalid password.', 'error')
                    return redirect(url_for('login'))
            else:
                flash('Email not found. Please signup first.', 'error')
                return redirect(url_for('login'))
        except Exception:
            # Fallback to local
            user = find_local_user_by_email(email)
            if user:
                if user['password'] == hash_password(password):
                    session['user_id'] = user['id']
                    session['user_name'] = user['name']
                    session['user_email'] = user['email']
                    flash('Login successful! (Local)', 'success')
                    return redirect(url_for('home'))
                else:
                    flash('Invalid password.', 'error')
                    return redirect(url_for('login'))
            else:
                flash('Email not found. Please signup first.', 'error')
                return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    """User logout"""
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    """Add product to cart"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    product_id = request.form['product_id']
    quantity = int(request.form.get('quantity', 1))
    
    # Get product details
    product = get_product_by_id(product_id)
    if not product:
        return jsonify({'success': False, 'message': 'Product not found'})
    
    # Check if item already in cart
    try:
        response = cart_table.get_item(
            Key={'user_id': session['user_id'], 'product_id': product_id}
        )
        
        if 'Item' in response:
            # Update quantity
            new_quantity = response['Item']['quantity'] + quantity
            cart_table.update_item(
                Key={'user_id': session['user_id'], 'product_id': product_id},
                UpdateExpression='SET quantity = :q',
                ExpressionAttributeValues={':q': new_quantity}
            )
        else:
            # Add new item
            cart_item = {
                'user_id': session['user_id'],
                'product_id': product_id,
                'product_name': product['name'],
                'product_price': product['price'],
                'product_image': product['image'],
                'quantity': quantity,
                'added_at': datetime.now().isoformat()
            }
            cart_table.put_item(Item=cart_item)
        
        return jsonify({'success': True, 'message': 'Added to cart successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error adding to cart'})

@app.route('/cart')
def cart():
    """Shopping cart page"""
    if 'user_id' not in session:
        flash('Please login to view cart.', 'error')
        return redirect(url_for('login'))
    
    cart_items = get_cart_items(session['user_id'])
    total = sum(float(item['product_price']) * item['quantity'] for item in cart_items)
    
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/update_cart', methods=['POST'])
def update_cart():
    """Update cart item quantity"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    product_id = request.form['product_id']
    quantity = int(request.form['quantity'])
    
    try:
        if quantity <= 0:
            # Remove item from cart
            cart_table.delete_item(
                Key={'user_id': session['user_id'], 'product_id': product_id}
            )
        else:
            # Update quantity
            cart_table.update_item(
                Key={'user_id': session['user_id'], 'product_id': product_id},
                UpdateExpression='SET quantity = :q',
                ExpressionAttributeValues={':q': quantity}
            )
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error updating cart'})

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    """Remove item from cart"""
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Please login first'})
    
    product_id = request.form['product_id']
    
    try:
        cart_table.delete_item(
            Key={'user_id': session['user_id'], 'product_id': product_id}
        )
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Error removing item'})

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    """Checkout page"""
    if 'user_id' not in session:
        flash('Please login to checkout.', 'error')
        return redirect(url_for('login'))
    
    cart_items = get_cart_items(session['user_id'])
    if not cart_items:
        flash('Your cart is empty.', 'error')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        # Process order
        order_data = {
            'id': str(uuid.uuid4()),
            'user_id': session['user_id'],
            'user_name': session['user_name'],
            'user_email': session['user_email'],
            'items': cart_items,
            'total': sum(float(item['product_price']) * item['quantity'] for item in cart_items),
            'shipping_address': {
                'name': request.form['name'],
                'phone': request.form['phone'],
                'address': request.form['address'],
                'city': request.form['city'],
                'state': request.form['state'],
                'pincode': request.form['pincode']
            },
            'status': 'pending',
            'created_at': datetime.now().isoformat()
        }
        
        try:
            # Save order
            orders_table.put_item(Item=order_data)
            
            # Clear cart
            for item in cart_items:
                cart_table.delete_item(
                    Key={'user_id': session['user_id'], 'product_id': item['product_id']}
                )
            
            session['order_id'] = order_data['id']
            return redirect(url_for('success'))
        except Exception as e:
            flash('Error processing order. Please try again.', 'error')
    
    total = sum(float(item['product_price']) * item['quantity'] for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/success')
def success():
    """Order success page"""
    order_id = session.get('order_id')
    if not order_id:
        return redirect(url_for('home'))
    
    return render_template('success.html', order_id=order_id)

@app.route('/orders')
def orders():
    """User orders page"""
    if 'user_id' not in session:
        flash('Please login to view orders.', 'error')
        return redirect(url_for('login'))
    
    try:
        response = orders_table.query(
            IndexName='user_id-created_at-index',
            KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(session['user_id']),
            ScanIndexForward=False
        )
        orders = response['Items']
    except Exception as e:
        orders = []
    
    return render_template('order.html', orders=orders)

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        # Handle contact form submission
        flash('Thank you for your message! We will get back to you soon.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact_us.html')

@app.route('/snacks')
def snacks():
    """Snacks page"""
    return render_template('snacks.html')

if __name__ == '__main__':
    # Initialize sample products on first run
    init_sample_products()
    app.run(debug=True, host='0.0.0.0', port=5000)