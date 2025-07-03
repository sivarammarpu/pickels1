# Pickle Paradise - E-commerce Website

A Flask-based e-commerce website for selling traditional pickles with user authentication, cart functionality, and AWS DynamoDB integration.

## Features

- ✅ User Authentication (Signup, Login, Logout)
- ✅ Product Catalog (Veg & Non-Veg Pickles)
- ✅ Shopping Cart Functionality
- ✅ Responsive Design with Bootstrap 5
- ✅ DynamoDB Integration
- ✅ Session-based Cart Management
- ✅ Flash Messages for User Feedback
- ✅ AWS Deployment Ready
- ✅ Order Management System
- ✅ Search and Filter Functionality

## Project Structure

```
pickle-paradise/
│
├── static/
│   ├── CSS/
│   │   └── style.css          # Custom styles
│   ├── images/                # Product images (add your images here)
│   └── JS/
│       └── main.js           # JavaScript functionality
│
├── templates/
│   ├── base.html             # Base template with navigation
│   ├── index.html            # Landing page
│   ├── home.html             # Home page with products
│   ├── login.html            # Login form
│   ├── signup.html           # Signup form
│   ├── cart.html             # Shopping cart
│   ├── veg_pickles.html      # Vegetarian pickles
│   ├── non_veg_pickles.html  # Non-vegetarian pickles
│   ├── about.html            # About page
│   ├── contact_us.html       # Contact page
│   ├── checkout.html         # Checkout form
│   ├── success.html          # Order success page
│   ├── snacks.html           # Snacks page
│   └── order.html            # Order tracking page
│
├── app.py                    # Main Flask application
├── dynamodb_setup.py         # DynamoDB table creation script
├── requirements.txt          # Python dependencies
├── Procfile                 # AWS deployment configuration
└── README.md                # This file
```

## Local Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- AWS CLI configured (for DynamoDB)
- AWS Account with DynamoDB access

### Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd pickle-paradise
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   export AWS_REGION=us-east-1
   export SECRET_KEY=your-secret-key-here
   # On Windows:
   # set AWS_REGION=us-east-1
   # set SECRET_KEY=your-secret-key-here
   ```

5. **Create DynamoDB tables**
   ```bash
   python dynamodb_setup.py
   ```

6. **Initialize sample products (optional)**
   ```bash
   python -c "from app import init_sample_products; init_sample_products()"
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

8. **Access the website**
   - Open your browser and go to: `http://localhost:5000`

## DynamoDB Tables

The application uses the following DynamoDB tables:

### 1. pickle_users
- **Primary Key**: email (String)
- **Global Secondary Index**: id-index
- **Attributes**: id, name, password, phone, created_at

### 2. pickle_products
- **Primary Key**: id (String)
- **Global Secondary Index**: category-index
- **Attributes**: name, price, description, category, image, rating, etc.

### 3. pickle_orders
- **Primary Key**: id (String)
- **Global Secondary Index**: user_id-created_at-index
- **Attributes**: user_id, items, total, status, shipping_address, etc.

### 4. pickle_cart
- **Composite Primary Key**: user_id (Hash), product_id (Range)
- **Attributes**: product_name, product_price, quantity, added_at

## AWS Deployment

### Option 1: AWS Elastic Beanstalk (Recommended)

1. **Prepare your application**
   ```bash
   # Create deployment package
   zip -r pickle-paradise.zip . -x "venv/*" "*.pyc" "__pycache__/*"
   ```

2. **Create Elastic Beanstalk Environment**
   - Go to AWS Elastic Beanstalk Console
   - Create a new application
   - Choose "Python" platform
   - Upload your project ZIP file
   - Configure environment variables:
     ```
     AWS_REGION=us-east-1
     SECRET_KEY=your-secure-secret-key-here
     ```

3. **Set up IAM Role**
   - Ensure your EB environment has DynamoDB access
   - Attach `AmazonDynamoDBFullAccess` policy

### Option 2: AWS EC2

1. **Launch EC2 Instance**
   - Choose Amazon Linux 2 or Ubuntu
   - Configure security groups (allow HTTP/HTTPS)
   - Attach IAM role with DynamoDB access

2. **Install Dependencies**
   ```bash
   sudo yum update -y  # For Amazon Linux
   sudo yum install python3 python3-pip git -y
   
   # For Ubuntu:
   # sudo apt update
   # sudo apt install python3 python3-pip git -y
   ```

3. **Deploy Application**
   ```bash
   git clone <your-repo-url>
   cd pickle-paradise
   pip3 install -r requirements.txt
   
   # Set environment variables
   export AWS_REGION=us-east-1
   export SECRET_KEY=your-secret-key
   
   # Create DynamoDB tables
   python3 dynamodb_setup.py
   
   # Run with gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

### Option 3: AWS Lambda + API Gateway

For serverless deployment, you can use AWS Lambda with the Serverless Framework or AWS SAM.

## Environment Variables

Required environment variables:

- `AWS_REGION`: AWS region for DynamoDB (default: us-east-1)
- `SECRET_KEY`: Flask secret key for sessions
- `AWS_ACCESS_KEY_ID`: AWS access key (if not using IAM roles)
- `AWS_SECRET_ACCESS_KEY`: AWS secret key (if not using IAM roles)

## Usage

### For Users
1. **Browse Products**: Visit the home page to see all available pickles
2. **Sign Up**: Create a new account to start shopping
3. **Login**: Use your credentials to access your account
4. **Add to Cart**: Click "Add to Cart" on any product
5. **View Cart**: Click the cart icon in the navigation
6. **Checkout**: Proceed to checkout to place your order
7. **Track Orders**: View your order history in the Orders section

### For Administrators
1. **Add Products**: Use the `init_sample_products()` function or add directly to DynamoDB
2. **Manage Orders**: Access DynamoDB console to view and update order statuses
3. **User Management**: View user data in the DynamoDB users table

## Customization

### Adding Products
Add products directly to DynamoDB or modify the `init_sample_products()` function in `app.py`:

```python
sample_products = [
    {
        'id': 'new_product_id',
        'name': 'Your Pickle Name',
        'price': Decimal('299'),
        'description': 'Product description',
        'category': 'vegetarian',  # or 'non-vegetarian'
        'image': 'product_image.jpg',
        'rating': Decimal('4.5'),
        'review_count': 100,
        'in_stock': True,
        'weight': '500g',
        'ingredients': 'List of ingredients',
        'spice_level': 'medium',  # mild, medium, hot, extra-hot
        'featured': False
    }
]
```

### Adding Images
1. Place product images in `static/images/` folder
2. Update the image paths in the products data
3. Recommended image size: 400x400 pixels
4. Supported formats: JPG, PNG, WebP

### Styling
- Edit `static/CSS/style.css` for custom styles
- Modify Bootstrap classes in templates for layout changes
- Use CSS custom properties for consistent theming

## Security Features

- Password hashing using SHA-256
- Session-based authentication
- CSRF protection (can be enhanced)
- Input validation and sanitization
- Secure environment variable handling

## Performance Optimizations

- DynamoDB efficient querying with GSIs
- Image lazy loading
- CSS and JS minification (in production)
- CDN integration for static assets
- Caching strategies for product data

## Monitoring and Logging

- AWS CloudWatch integration
- Application performance monitoring
- Error tracking and alerting
- User activity analytics

## Future Enhancements

- [ ] Payment gateway integration (Stripe, Razorpay)
- [ ] Email notifications for orders
- [ ] Product reviews and ratings
- [ ] Advanced search with Elasticsearch
- [ ] Wishlist functionality
- [ ] Admin dashboard
- [ ] Mobile app API
- [ ] Multi-language support
- [ ] Inventory management
- [ ] Discount and coupon system

## Support

For issues or questions:
- Check the console for error messages
- Verify AWS credentials and permissions
- Ensure DynamoDB tables are created
- Check environment variables
- Review CloudWatch logs for detailed errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

- Email: support@pickleparadise.com
- Website: https://pickleparadise.com
- GitHub: https://github.com/your-username/pickle-paradise