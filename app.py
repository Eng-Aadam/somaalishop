
# import os
# from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
# from supabase import create_client, Client
# from dotenv import load_dotenv
# from datetime import datetime
# import re
# from werkzeug.utils import secure_filename

# # Load environment variables
# load_dotenv()

# app = Flask(__name__)
# app.secret_key = os.getenv(
#     'FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# # ✅ FIXED: Supabase configuration with lazy initialization
# SUPABASE_URL = 'https://mhfxrhnmdhmmdlfvxjgt.supabase.co'
# SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1oZnhyaG5tZGhtbWRsZnZ4amd0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyNjM1NzUsImV4cCI6MjA3ODgzOTU3NX0.g7RYA1lthHTEYF8QFLGMQVfgIIb1MnsHONYPIbNsEsE'

# # ✅ FIXED: Lazy initialization for Vercel
# _supabase_instance = None


# def get_supabase():
#     global _supabase_instance
#     if _supabase_instance is None:
#         _supabase_instance = create_client(SUPABASE_URL, SUPABASE_KEY)
#     return _supabase_instance


# # Image upload configuration
# UPLOAD_FOLDER = 'static/uploads/products'
# ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
# MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# # Create upload folder if it doesn't exist
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# # Utility functions


# def get_current_user():
#     """Get current user from session"""
#     if 'user' in session:
#         return session['user']
#     return None


# def is_admin():
#     """Check if current user is admin"""
#     user = get_current_user()
#     if user and user.get('email') == 'daymaro94@gmail.com':
#         return True
#     return False


# def format_currency(amount):
#     """Format amount as currency"""
#     if amount is None:
#         return "$0.00"
#     try:
#         return f"${float(amount):.2f}"
#     except (ValueError, TypeError):
#         return "$0.00"


# def generate_slug(name):
#     """Generate slug from product name"""
#     if not name:
#         return "product"
#     slug = re.sub(r'[^a-zA-Z0-9\s]', '', name)
#     slug = slug.lower().strip()
#     slug = re.sub(r'\s+', '-', slug)
#     return slug[:100]


# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# def save_product_image(file):
#     """Save product image and return the URL"""
#     if file and allowed_file(file.filename):
#         filename = secure_filename(file.filename)
#         # Add timestamp to make filename unique
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
#         filename = timestamp + filename

#         file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         file.save(file_path)

#         return f'/static/uploads/products/{filename}'
#     return None

# # Template filter


# @app.template_filter('format_currency')
# def format_currency_filter(amount):
#     return format_currency(amount)

# # Context processor


# @app.context_processor
# def utility_processor():
#     return dict(
#         get_current_user=get_current_user,
#         is_admin=is_admin,
#         format_currency=format_currency,
#         min=min
#     )

# # Debug Routes


# @app.route('/debug-admin')
# def debug_admin():
#     """Debug admin access"""
#     user = get_current_user()
#     return jsonify({
#         'session_user': user,
#         'is_admin': is_admin(),
#         'session_keys': list(session.keys())
#     })


# @app.route('/force-admin')
# def force_admin():
#     """Force admin session for testing"""
#     session['user'] = {
#         'id': 'admin-test-id',
#         'email': 'daymaro94@gmail.com',
#         'full_name': 'Admin User',
#         'created_at': datetime.utcnow().isoformat()
#     }
#     flash('Admin session activated!', 'success')
#     return redirect(url_for('admin_dashboard'))

# # Main Routes


# @app.route('/')
# def index():
#     """Home page"""
#     try:
#         response = get_supabase().table('products').select('*').limit(6).execute()
#         products = response.data if response.data else []
#         return render_template('index.html', products=products)
#     except Exception as e:
#         print(f"Error fetching products: {e}")
#         return render_template('index.html', products=[])


# @app.route('/products')
# def products():
#     """Products listing page"""
#     try:
#         search = request.args.get('search', '')
#         category = request.args.get('category', '')

#         query = get_supabase().table('products').select('*')

#         if search:
#             query = query.or_(
#                 f"name.ilike.%{search}%,description.ilike.%{search}%")
#         if category:
#             query = query.eq('category', category)

#         response = query.execute()
#         products = response.data if response.data else []

#         categories_response = get_supabase().table(
#             'products').select('category').execute()
#         categories = list(set(
#             [p['category'] for p in categories_response.data])) if categories_response.data else []

#         return render_template('products.html', products=products, search=search, category=category, categories=categories)
#     except Exception as e:
#         print(f"Error fetching products: {e}")
#         return render_template('products.html', products=[], categories=[])


# @app.route('/product/<slug>')
# def product_detail(slug):
#     """Product detail page"""
#     try:
#         response = get_supabase().table('products').select('*').eq('slug', slug).execute()
#         product = response.data[0] if response.data else None

#         if not product:
#             flash('Product not found', 'error')
#             return redirect(url_for('products'))

#         return render_template('product_detail.html', product=product)
#     except Exception as e:
#         print(f"Error fetching product: {e}")
#         flash('Error loading product', 'error')
#         return redirect(url_for('products'))

# # Cart Routes


# @app.route('/cart')
# def cart():
#     """Cart page"""
#     cart_items = session.get('cart', [])
#     total = sum(item['price'] * item['quantity'] for item in cart_items)
#     return render_template('cart.html', cart_items=cart_items, total=total)


# @app.route('/add-to-cart', methods=['POST'])
# def add_to_cart():
#     """Add item to cart"""
#     try:
#         product_id = request.form.get('product_id')
#         quantity = int(request.form.get('quantity', 1))

#         response = get_supabase().table('products').select(
#             '*').eq('id', product_id).execute()
#         product = response.data[0] if response.data else None

#         if not product:
#             return jsonify({'success': False, 'message': 'Product not found'})

#         if product['stock'] < quantity:
#             return jsonify({'success': False, 'message': 'Insufficient stock'})

#         cart = session.get('cart', [])

#         item_exists = False
#         for item in cart:
#             if str(item['product_id']) == str(product_id):
#                 item['quantity'] += quantity
#                 item_exists = True
#                 break

#         if not item_exists:
#             cart.append({
#                 'product_id': product_id,
#                 'name': product['name'],
#                 'price': float(product['price']),
#                 'quantity': quantity,
#                 'image_url': product['image_url'],
#                 'slug': product['slug']
#             })

#         session['cart'] = cart
#         session.modified = True

#         return jsonify({'success': True, 'message': 'Product added to cart', 'cart_count': len(cart)})

#     except Exception as e:
#         print(f"Error adding to cart: {e}")
#         return jsonify({'success': False, 'message': 'Error adding to cart'})


# @app.route('/update-cart', methods=['POST'])
# def update_cart():
#     """Update cart item quantity"""
#     try:
#         product_id = request.form.get('product_id')
#         quantity = int(request.form.get('quantity', 0))

#         cart = session.get('cart', [])

#         if quantity <= 0:
#             # Remove item
#             cart = [item for item in cart if str(
#                 item['product_id']) != str(product_id)]
#         else:
#             # Update quantity
#             for item in cart:
#                 if str(item['product_id']) == str(product_id):
#                     item['quantity'] = quantity
#                     break

#         session['cart'] = cart
#         session.modified = True

#         total = sum(item['price'] * item['quantity'] for item in cart)
#         return jsonify({
#             'success': True,
#             'cart_count': len(cart),
#             'total': format_currency(total)
#         })

#     except Exception as e:
#         print(f"Error updating cart: {e}")
#         return jsonify({'success': False, 'message': 'Error updating cart'})

# # Checkout Routes


# @app.route('/checkout')
# def checkout():
#     """Checkout page"""
#     cart_items = session.get('cart', [])
#     if not cart_items:
#         flash('Your cart is empty', 'error')
#         return redirect(url_for('cart'))

#     total = sum(item['price'] * item['quantity'] for item in cart_items)
#     return render_template('checkout.html', cart_items=cart_items, total=total)


# @app.route('/process-payment', methods=['POST'])
# def process_payment():
#     """Process payment simulation"""
#     try:
#         user = get_current_user()
#         if not user:
#             return jsonify({'success': False, 'message': 'Please login to checkout'})

#         cart_items = session.get('cart', [])
#         if not cart_items:
#             return jsonify({'success': False, 'message': 'Cart is empty'})

#         total_amount = sum(item['price'] * item['quantity']
#                            for item in cart_items)
#         phone_number = request.form.get('phone_number')
#         pin = request.form.get('pin')

#         if not phone_number:
#             return jsonify({'success': False, 'message': 'Phone number is required'})

#         # Simulate payment processing
#         merchant_number = '+2520907251291'
#         print(
#             f"Simulating payment: ${total_amount} from {phone_number} to {merchant_number}")

#         # Create order
#         order_data = {
#             'user_id': user['id'],
#             'total_amount': total_amount,
#             'status': 'pending',
#             'payment_status': 'paid',
#             'merchant_number_used': merchant_number,
#             'customer_phone': phone_number,
#             'created_at': datetime.utcnow().isoformat()
#         }

#         order_response = get_supabase().table('orders').insert(order_data).execute()
#         order_id = order_response.data[0]['id'] if order_response.data else None

#         if order_id:
#             # Create order items and update stock
#             for item in cart_items:
#                 order_item = {
#                     'order_id': order_id,
#                     'product_id': item['product_id'],
#                     'quantity': item['quantity'],
#                     'price': item['price']
#                 }
#                 get_supabase().table('order_items').insert(order_item).execute()

#                 # Update product stock
#                 product_response = get_supabase().table('products').select(
#                     'stock').eq('id', item['product_id']).execute()
#                 if product_response.data:
#                     current_stock = product_response.data[0]['stock']
#                     new_stock = current_stock - item['quantity']
#                     get_supabase().table('products').update(
#                         {'stock': new_stock}).eq('id', item['product_id']).execute()

#         # Clear cart
#         session.pop('cart', None)

#         return jsonify({
#             'success': True,
#             'message': 'Payment processed successfully',
#             'order_id': order_id
#         })

#     except Exception as e:
#         print(f"Error processing payment: {e}")
#         return jsonify({'success': False, 'message': 'Error processing payment'})


# @app.route('/order-success/<order_id>')
# def order_success(order_id):
#     """Order success page"""
#     try:
#         response = get_supabase().table('orders').select(
#             '*, order_items(*, products(*))').eq('id', order_id).execute()
#         order = response.data[0] if response.data else None

#         if not order:
#             flash('Order not found', 'error')
#             return redirect(url_for('index'))

#         return render_template('order_success.html', order=order)
#     except Exception as e:
#         print(f"Error fetching order: {e}")
#         flash('Error loading order', 'error')
#         return redirect(url_for('index'))

# # Auth Routes


# @app.route('/login')
# def login():
#     """Login page - WITHOUT demo credentials"""
#     return render_template('login.html')


# @app.route('/signup')
# def signup():
#     """Signup page"""
#     return render_template('signup.html')


# @app.route('/logout')
# def logout():
#     """Logout user"""
#     session.pop('user', None)
#     flash('You have been logged out', 'success')
#     return redirect(url_for('index'))


# @app.route('/auth/signup', methods=['POST'])
# def auth_signup():
#     """Handle user signup"""
#     try:
#         email = request.form.get('email')
#         password = request.form.get('password')
#         full_name = request.form.get('full_name')

#         auth_response = get_supabase().auth.sign_up({
#             "email": email,
#             "password": password,
#         })

#         if auth_response.user:
#             user_data = {
#                 'id': auth_response.user.id,
#                 'email': email,
#                 'full_name': full_name,
#                 'created_at': datetime.utcnow().isoformat()
#             }

#             get_supabase().table('users').insert(user_data).execute()

#             flash(
#                 'Registration successful! Please check your email to verify your account.', 'success')
#             return redirect(url_for('login'))
#         else:
#             error_msg = auth_response.get('error', {}).get(
#                 'message', 'Registration failed')
#             flash(f'Registration failed: {error_msg}', 'error')
#             return redirect(url_for('signup'))

#     except Exception as e:
#         print(f"Signup error: {str(e)}")
#         flash(f'Registration failed: {str(e)}', 'error')
#         return redirect(url_for('signup'))


# @app.route('/auth/login', methods=['POST'])
# def auth_login():
#     """Handle user login"""
#     try:
#         email = request.form.get('email')
#         password = request.form.get('password')

#         auth_response = get_supabase().auth.sign_in_with_password({
#             "email": email,
#             "password": password
#         })

#         if auth_response.user:
#             user_response = get_supabase().table('users').select(
#                 '*').eq('id', auth_response.user.id).execute()

#             user_profile = {}
#             if user_response.data:
#                 user_profile = user_response.data[0]
#             else:
#                 user_data = {
#                     'id': auth_response.user.id,
#                     'email': email,
#                     'full_name': email.split('@')[0],
#                     'created_at': datetime.utcnow().isoformat()
#                 }
#                 get_supabase().table('users').insert(user_data).execute()
#                 user_profile = user_data

#             session['user'] = {
#                 'id': auth_response.user.id,
#                 'email': auth_response.user.email,
#                 'full_name': user_profile.get('full_name', ''),
#                 'created_at': user_profile.get('created_at')
#             }

#             flash('Login successful!', 'success')

#             if email == 'daymaro94@gmail.com':
#                 return redirect(url_for('admin_dashboard'))

#             return redirect(url_for('index'))
#         else:
#             error_msg = auth_response.get('error', {}).get(
#                 'message', 'Invalid email or password')
#             flash(f'Login failed: {error_msg}', 'error')
#             return redirect(url_for('login'))

#     except Exception as e:
#         print(f"Login error: {str(e)}")
#         flash(f'Login failed: {str(e)}', 'error')
#         return redirect(url_for('login'))

# # Admin Routes


# @app.route('/admin')
# def admin_dashboard():
#     """Admin dashboard"""
#     if not is_admin():
#         flash('Access denied. Admin privileges required.', 'error')
#         return redirect(url_for('index'))

#     try:
#         orders_response = get_supabase().table('orders').select('*').execute()
#         products_response = get_supabase().table('products').select('*').execute()
#         users_response = get_supabase().table('users').select('*').execute()

#         stats = {
#             'total_orders': len(orders_response.data) if orders_response.data else 0,
#             'total_products': len(products_response.data) if products_response.data else 0,
#             'total_users': len(users_response.data) if users_response.data else 0,
#             'revenue': sum(order['total_amount'] for order in orders_response.data) if orders_response.data else 0
#         }

#         recent_orders = orders_response.data[:5] if orders_response.data else [
#         ]

#         return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders)
#     except Exception as e:
#         print(f"Admin dashboard error: {e}")
#         flash('Error loading admin dashboard', 'error')
#         return render_template('admin/dashboard.html', stats={}, recent_orders=[])


# @app.route('/admin/products')
# def admin_products():
#     """Admin products management"""
#     if not is_admin():
#         flash('Access denied. Admin privileges required.', 'error')
#         return redirect(url_for('index'))

#     try:
#         response = get_supabase().table('products').select('*').execute()
#         products = response.data if response.data else []
#         return render_template('admin/products.html', products=products)
#     except Exception as e:
#         print(f"Admin products error: {e}")
#         flash('Error loading products', 'error')
#         return render_template('admin/products.html', products=[])


# @app.route('/admin/orders')
# def admin_orders():
#     """Admin orders management"""
#     if not is_admin():
#         flash('Access denied. Admin privileges required.', 'error')
#         return redirect(url_for('index'))

#     try:
#         response = get_supabase().table('orders').select(
#             '*, users(email, full_name)').execute()
#         orders = response.data if response.data else []

#         for order in orders:
#             items_response = get_supabase().table('order_items').select(
#                 '*, products(name)').eq('order_id', order['id']).execute()
#             order['order_items'] = items_response.data if items_response.data else []

#         return render_template('admin/orders.html', orders=orders)
#     except Exception as e:
#         print(f"Admin orders error: {e}")
#         flash('Error loading orders', 'error')
#         return render_template('admin/orders.html', orders=[])


# @app.route('/admin/users')
# def admin_users():
#     """Admin users management"""
#     if not is_admin():
#         flash('Access denied. Admin privileges required.', 'error')
#         return redirect(url_for('index'))

#     try:
#         response = get_supabase().table('users').select('*').execute()
#         users = response.data if response.data else []
#         return render_template('admin/users.html', users=users)
#     except Exception as e:
#         print(f"Admin users error: {e}")
#         flash('Error loading users', 'error')
#         return render_template('admin/users.html', users=[])

# # ✅ NEW: Delete User Route


# @app.route('/admin/delete-user/<user_id>', methods=['POST'])
# def admin_delete_user(user_id):
#     """Delete user from database"""
#     if not is_admin():
#         return jsonify({'success': False, 'message': 'Access denied'})

#     try:
#         # Check if user exists
#         user_response = get_supabase().table(
#             'users').select('*').eq('id', user_id).execute()
#         if not user_response.data:
#             return jsonify({'success': False, 'message': 'User not found'})

#         # Delete user from database
#         response = get_supabase().table('users').delete().eq('id', user_id).execute()

#         if response.data:
#             flash('User deleted successfully', 'success')
#             return jsonify({'success': True, 'message': 'User deleted successfully'})
#         else:
#             return jsonify({'success': False, 'message': 'Failed to delete user'})

#     except Exception as e:
#         print(f"Delete user error: {e}")
#         return jsonify({'success': False, 'message': 'Error deleting user'})

# # Admin Product Management with Image Upload


# @app.route('/admin/add-product', methods=['POST'])
# def admin_add_product():
#     """Add new product with image upload"""
#     if not is_admin():
#         return jsonify({'success': False, 'message': 'Access denied'})

#     try:
#         name = request.form.get('name')
#         description = request.form.get('description')
#         price = float(request.form.get('price'))
#         stock = int(request.form.get('stock'))
#         category = request.form.get('category')

#         slug = generate_slug(name)

#         # Handle image upload
#         image_url = '/static/images/placeholder.jpg'
#         if 'image' in request.files:
#             file = request.files['image']
#             if file and file.filename != '':
#                 uploaded_image_url = save_product_image(file)
#                 if uploaded_image_url:
#                     image_url = uploaded_image_url

#         product_data = {
#             'name': name,
#             'slug': slug,
#             'description': description,
#             'price': price,
#             'stock': stock,
#             'category': category,
#             'image_url': image_url,
#             'created_at': datetime.utcnow().isoformat()
#         }

#         response = get_supabase().table('products').insert(product_data).execute()

#         if response.data:
#             flash('Product added successfully', 'success')
#             return jsonify({'success': True, 'message': 'Product added successfully'})
#         else:
#             return jsonify({'success': False, 'message': 'Failed to add product'})

#     except Exception as e:
#         print(f"Add product error: {e}")
#         return jsonify({'success': False, 'message': 'Error adding product'})

# # ✅ FIXED: Edit Product Route - Fixed infinite redirect loop


# @app.route('/admin/edit-product/<product_id>', methods=['GET', 'POST'])
# def admin_edit_product(product_id):
#     """Edit existing product"""
#     # ✅ FIXED: Added proper admin authorization check
#     if not is_admin():
#         flash('Access denied. Admin privileges required.', 'error')
#         return redirect(url_for('admin_products'))

#     try:
#         if request.method == 'GET':
#             # Get product details for editing
#             response = get_supabase().table('products').select(
#                 '*').eq('id', product_id).execute()
#             product = response.data[0] if response.data else None

#             if not product:
#                 flash('Product not found', 'error')
#                 return redirect(url_for('admin_products'))

#             return render_template('admin/edit_product.html', product=product)

#         else:  # POST request - update product
#             # ✅ FIXED: Added debug logging to see what data is received
#             print(f"DEBUG: Received form data - {request.form}")
#             print(f"DEBUG: Files received - {request.files}")

#             name = request.form.get('name')
#             description = request.form.get('description')
#             price_str = request.form.get('price')
#             stock_str = request.form.get('stock')
#             category = request.form.get('category')

#             # ✅ FIXED: Better error handling for price and stock conversion
#             try:
#                 price = float(price_str) if price_str else 0.0
#             except (ValueError, TypeError):
#                 flash('Invalid price format', 'error')
#                 # ✅ FIXED: Stay on the same page instead of redirecting to avoid loop
#                 return redirect(url_for('admin_edit_product', product_id=product_id))

#             try:
#                 stock = int(stock_str) if stock_str else 0
#             except (ValueError, TypeError):
#                 flash('Invalid stock format', 'error')
#                 # ✅ FIXED: Stay on the same page instead of redirecting to avoid loop
#                 return redirect(url_for('admin_edit_product', product_id=product_id))

#             slug = generate_slug(name)

#             # Handle image upload
#             image_url = request.form.get('current_image')
#             if 'image' in request.files:
#                 file = request.files['image']
#                 if file and file.filename != '':
#                     uploaded_image_url = save_product_image(file)
#                     if uploaded_image_url:
#                         image_url = uploaded_image_url

#             product_data = {
#                 'name': name,
#                 'slug': slug,
#                 'description': description,
#                 'price': price,
#                 'stock': stock,
#                 'category': category,
#                 'image_url': image_url,
#                 'updated_at': datetime.utcnow().isoformat()
#             }

#             # ✅ FIXED: Added debug logging for the update
#             print(
#                 f"DEBUG: Updating product {product_id} with data: {product_data}")

#             response = get_supabase().table('products').update(
#                 product_data).eq('id', product_id).execute()

#             if response.data:
#                 flash('Product updated successfully', 'success')
#                 return redirect(url_for('admin_products'))
#             else:
#                 flash('Failed to update product - no data returned', 'error')
#                 # ✅ FIXED: Stay on the same page instead of redirecting to avoid loop
#                 return redirect(url_for('admin_edit_product', product_id=product_id))

#     except Exception as e:
#         print(f"Edit product error: {str(e)}")
#         flash(f'Error updating product: {str(e)}', 'error')
#         # ✅ FIXED: Stay on the same page instead of redirecting to avoid loop
#         return redirect(url_for('admin_edit_product', product_id=product_id))

# # Delete Product Route


# @app.route('/admin/delete-product/<product_id>', methods=['POST'])
# def admin_delete_product(product_id):
#     """Delete product"""
#     if not is_admin():
#         return jsonify({'success': False, 'message': 'Access denied'})

#     try:
#         response = get_supabase().table('products').delete().eq('id', product_id).execute()

#         if response.data:
#             flash('Product deleted successfully', 'success')
#             return jsonify({'success': True, 'message': 'Product deleted successfully'})
#         else:
#             return jsonify({'success': False, 'message': 'Failed to delete product'})

#     except Exception as e:
#         print(f"Delete product error: {e}")
#         return jsonify({'success': False, 'message': 'Error deleting product'})


# @app.route('/admin/update-order-status', methods=['POST'])
# def admin_update_order_status():
#     """Update order status"""
#     if not is_admin():
#         return jsonify({'success': False, 'message': 'Access denied'})

#     try:
#         order_id = request.form.get('order_id')
#         status = request.form.get('status')

#         get_supabase().table('orders').update(
#             {'status': status}).eq('id', order_id).execute()

#         flash('Order status updated successfully', 'success')
#         return jsonify({'success': True, 'message': 'Order status updated'})

#     except Exception as e:
#         print(f"Update order status error: {e}")
#         return jsonify({'success': False, 'message': 'Error updating order status'})


# if __name__ == '__main__':
#     print("🟢 Starting SomaliShop Server...")
#     print("🟢 Server will be available at: http://localhost:5000")
#     print("🟢 Press CTRL+C to stop the server")
#     app.run(debug=True, host='0.0.0.0', port=5000)






import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash, send_from_directory
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime
import re
from werkzeug.utils import secure_filename
import uuid

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Supabase configuration
SUPABASE_URL = 'https://mhfxrhnmdhmmdlfvxjgt.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im1oZnhyaG5tZGhtbWRsZnZ4amd0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMyNjM1NzUsImV4cCI6MjA3ODgzOTU3NX0.g7RYA1lthHTEYF8QFLGMQVfgIIb1MnsHONYPIbNsEsE'

# Lazy initialization for Vercel
_supabase_instance = None

def get_supabase():
    global _supabase_instance
    if _supabase_instance is None:
        _supabase_instance = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _supabase_instance

# Image upload configuration
UPLOAD_FOLDER = 'static/uploads/products'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Utility functions
def get_current_user():
    """Get current user from session"""
    if 'user' in session:
        return session['user']
    return None

def is_admin():
    """Check if current user is admin"""
    user = get_current_user()
    if user and user.get('email') == 'daymaro94@gmail.com':
        return True
    return False

def format_currency(amount):
    """Format amount as currency"""
    if amount is None:
        return "$0.00"
    try:
        return f"${float(amount):.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def generate_slug(name):
    """Generate slug from product name"""
    if not name:
        return "product"
    slug = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    slug = slug.lower().strip()
    slug = re.sub(r'\s+', '-', slug)
    return slug[:100]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_product_image(file):
    """Save product image and return the URL"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Add timestamp and UUID to make filename unique
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"{timestamp}_{unique_id}_{filename}"

        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        return f'/static/uploads/products/{filename}'
    return None

# Template filter
@app.template_filter('format_currency')
def format_currency_filter(amount):
    return format_currency(amount)

# Context processor
@app.context_processor
def utility_processor():
    return dict(
        get_current_user=get_current_user,
        is_admin=is_admin,
        format_currency=format_currency,
        min=min
    )

# Serve uploaded files
@app.route('/static/uploads/products/<filename>')
def serve_uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Main Routes
@app.route('/')
def index():
    """Home page"""
    try:
        response = get_supabase().table('products').select('*').limit(6).execute()
        products = response.data if response.data else []
        return render_template('index.html', products=products)
    except Exception as e:
        print(f"Error fetching products: {e}")
        return render_template('index.html', products=[])

@app.route('/products')
def products():
    """Products listing page"""
    try:
        search = request.args.get('search', '')
        category = request.args.get('category', '')

        query = get_supabase().table('products').select('*')

        if search:
            query = query.or_(f"name.ilike.%{search}%,description.ilike.%{search}%")
        if category:
            query = query.eq('category', category)

        response = query.execute()
        products = response.data if response.data else []

        categories_response = get_supabase().table('products').select('category').execute()
        categories = list(set([p['category'] for p in categories_response.data])) if categories_response.data else []

        return render_template('products.html', products=products, search=search, category=category, categories=categories)
    except Exception as e:
        print(f"Error fetching products: {e}")
        return render_template('products.html', products=[], categories=[])

@app.route('/product/<slug>')
def product_detail(slug):
    """Product detail page"""
    try:
        response = get_supabase().table('products').select('*').eq('slug', slug).execute()
        product = response.data[0] if response.data else None

        if not product:
            flash('Product not found', 'error')
            return redirect(url_for('products'))

        return render_template('product_detail.html', product=product)
    except Exception as e:
        print(f"Error fetching product: {e}")
        flash('Error loading product', 'error')
        return redirect(url_for('products'))

# Cart Routes
@app.route('/cart')
def cart():
    """Cart page"""
    cart_items = session.get('cart', [])
    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    """Add item to cart"""
    try:
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity', 1))

        response = get_supabase().table('products').select('*').eq('id', product_id).execute()
        product = response.data[0] if response.data else None

        if not product:
            return jsonify({'success': False, 'message': 'Product not found'})

        if product['stock'] < quantity:
            return jsonify({'success': False, 'message': 'Insufficient stock'})

        cart = session.get('cart', [])

        item_exists = False
        for item in cart:
            if str(item['product_id']) == str(product_id):
                item['quantity'] += quantity
                item_exists = True
                break

        if not item_exists:
            cart.append({
                'product_id': product_id,
                'name': product['name'],
                'price': float(product['price']),
                'quantity': quantity,
                'image_url': product['image_url'],
                'slug': product['slug']
            })

        session['cart'] = cart
        session.modified = True

        return jsonify({'success': True, 'message': 'Product added to cart', 'cart_count': len(cart)})

    except Exception as e:
        print(f"Error adding to cart: {e}")
        return jsonify({'success': False, 'message': 'Error adding to cart'})

@app.route('/update-cart', methods=['POST'])
def update_cart():
    """Update cart item quantity"""
    try:
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity', 0))

        cart = session.get('cart', [])

        if quantity <= 0:
            # Remove item
            cart = [item for item in cart if str(item['product_id']) != str(product_id)]
        else:
            # Update quantity
            for item in cart:
                if str(item['product_id']) == str(product_id):
                    item['quantity'] = quantity
                    break

        session['cart'] = cart
        session.modified = True

        total = sum(item['price'] * item['quantity'] for item in cart)
        return jsonify({
            'success': True,
            'cart_count': len(cart),
            'total': format_currency(total)
        })

    except Exception as e:
        print(f"Error updating cart: {e}")
        return jsonify({'success': False, 'message': 'Error updating cart'})

# Checkout Routes
@app.route('/checkout')
def checkout():
    """Checkout page"""
    if not get_current_user():
        flash('Please login to checkout', 'error')
        return redirect(url_for('login'))
    
    cart_items = session.get('cart', [])
    if not cart_items:
        flash('Your cart is empty', 'error')
        return redirect(url_for('cart'))

    total = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template('checkout.html', cart_items=cart_items, total=total)

@app.route('/process-payment', methods=['POST'])
def process_payment():
    """Process payment simulation"""
    try:
        user = get_current_user()
        if not user:
            return jsonify({'success': False, 'message': 'Please login to checkout'})

        cart_items = session.get('cart', [])
        if not cart_items:
            return jsonify({'success': False, 'message': 'Cart is empty'})

        total_amount = sum(item['price'] * item['quantity'] for item in cart_items)
        phone_number = request.form.get('phone_number')
        full_name = request.form.get('full_name')
        address = request.form.get('address')
        city = request.form.get('city')

        if not phone_number:
            return jsonify({'success': False, 'message': 'Phone number is required'})

        # Create order
        order_data = {
            'user_id': user['id'],
            'total_amount': total_amount,
            'status': 'pending',
            'payment_status': 'paid',
            'customer_phone': phone_number,
            'customer_name': full_name,
            'shipping_address': address,
            'shipping_city': city,
            'created_at': datetime.utcnow().isoformat()
        }

        order_response = get_supabase().table('orders').insert(order_data).execute()
        
        if not order_response.data:
            return jsonify({'success': False, 'message': 'Failed to create order'})
            
        order_id = order_response.data[0]['id']

        # Create order items and update stock
        for item in cart_items:
            order_item = {
                'order_id': order_id,
                'product_id': item['product_id'],
                'quantity': item['quantity'],
                'price': item['price']
            }
            get_supabase().table('order_items').insert(order_item).execute()

            # Update product stock
            product_response = get_supabase().table('products').select('stock').eq('id', item['product_id']).execute()
            if product_response.data:
                current_stock = product_response.data[0]['stock']
                new_stock = current_stock - item['quantity']
                get_supabase().table('products').update({'stock': new_stock}).eq('id', item['product_id']).execute()

        # Clear cart
        session.pop('cart', None)

        return jsonify({
            'success': True,
            'message': 'Payment processed successfully',
            'order_id': order_id
        })

    except Exception as e:
        print(f"Error processing payment: {e}")
        return jsonify({'success': False, 'message': 'Error processing payment'})

@app.route('/order-success/<order_id>')
def order_success(order_id):
    """Order success page"""
    try:
        response = get_supabase().table('orders').select('*, order_items(*, products(*))').eq('id', order_id).execute()
        order = response.data[0] if response.data else None

        if not order:
            flash('Order not found', 'error')
            return redirect(url_for('index'))

        return render_template('order_success.html', order=order)
    except Exception as e:
        print(f"Error fetching order: {e}")
        flash('Error loading order', 'error')
        return redirect(url_for('index'))

# Auth Routes
@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/signup')
def signup():
    """Signup page"""
    return render_template('signup.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.pop('user', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))

@app.route('/auth/signup', methods=['POST'])
def auth_signup():
    """Handle user signup"""
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')

        auth_response = get_supabase().auth.sign_up({
            "email": email,
            "password": password,
        })

        if auth_response.user:
            user_data = {
                'id': auth_response.user.id,
                'email': email,
                'full_name': full_name,
                'created_at': datetime.utcnow().isoformat()
            }

            get_supabase().table('users').insert(user_data).execute()

            flash('Registration successful! Please check your email to verify your account.', 'success')
            return redirect(url_for('login'))
        else:
            error_msg = auth_response.get('error', {}).get('message', 'Registration failed')
            flash(f'Registration failed: {error_msg}', 'error')
            return redirect(url_for('signup'))

    except Exception as e:
        print(f"Signup error: {str(e)}")
        flash(f'Registration failed: {str(e)}', 'error')
        return redirect(url_for('signup'))

@app.route('/auth/login', methods=['POST'])
def auth_login():
    """Handle user login"""
    try:
        email = request.form.get('email')
        password = request.form.get('password')

        auth_response = get_supabase().auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if auth_response.user:
            user_response = get_supabase().table('users').select('*').eq('id', auth_response.user.id).execute()

            user_profile = {}
            if user_response.data:
                user_profile = user_response.data[0]
            else:
                user_data = {
                    'id': auth_response.user.id,
                    'email': email,
                    'full_name': email.split('@')[0],
                    'created_at': datetime.utcnow().isoformat()
                }
                get_supabase().table('users').insert(user_data).execute()
                user_profile = user_data

            session['user'] = {
                'id': auth_response.user.id,
                'email': auth_response.user.email,
                'full_name': user_profile.get('full_name', ''),
                'created_at': user_profile.get('created_at')
            }

            flash('Login successful!', 'success')

            if email == 'daymaro94@gmail.com':
                return redirect(url_for('admin_dashboard'))

            return redirect(url_for('index'))
        else:
            error_msg = auth_response.get('error', {}).get('message', 'Invalid email or password')
            flash(f'Login failed: {error_msg}', 'error')
            return redirect(url_for('login'))

    except Exception as e:
        print(f"Login error: {str(e)}")
        flash(f'Login failed: {str(e)}', 'error')
        return redirect(url_for('login'))

# Admin Routes
@app.route('/admin')
def admin_dashboard():
    """Admin dashboard"""
    if not is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))

    try:
        orders_response = get_supabase().table('orders').select('*').execute()
        products_response = get_supabase().table('products').select('*').execute()
        users_response = get_supabase().table('users').select('*').execute()

        stats = {
            'total_orders': len(orders_response.data) if orders_response.data else 0,
            'total_products': len(products_response.data) if products_response.data else 0,
            'total_users': len(users_response.data) if users_response.data else 0,
            'revenue': sum(order['total_amount'] for order in orders_response.data) if orders_response.data else 0
        }

        recent_orders = orders_response.data[:5] if orders_response.data else []

        return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders)
    except Exception as e:
        print(f"Admin dashboard error: {e}")
        flash('Error loading admin dashboard', 'error')
        return render_template('admin/dashboard.html', stats={}, recent_orders=[])

@app.route('/admin/products')
def admin_products():
    """Admin products management"""
    if not is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))

    try:
        response = get_supabase().table('products').select('*').execute()
        products = response.data if response.data else []
        return render_template('admin/products.html', products=products)
    except Exception as e:
        print(f"Admin products error: {e}")
        flash('Error loading products', 'error')
        return render_template('admin/products.html', products=[])

@app.route('/admin/orders')
def admin_orders():
    """Admin orders management"""
    if not is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))

    try:
        response = get_supabase().table('orders').select('*, users(email, full_name)').execute()
        orders = response.data if response.data else []

        for order in orders:
            items_response = get_supabase().table('order_items').select('*, products(name)').eq('order_id', order['id']).execute()
            order['order_items'] = items_response.data if items_response.data else []

        return render_template('admin/orders.html', orders=orders)
    except Exception as e:
        print(f"Admin orders error: {e}")
        flash('Error loading orders', 'error')
        return render_template('admin/orders.html', orders=[])

@app.route('/admin/users')
def admin_users():
    """Admin users management"""
    if not is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('index'))

    try:
        response = get_supabase().table('users').select('*').execute()
        users = response.data if response.data else []
        return render_template('admin/users.html', users=users)
    except Exception as e:
        print(f"Admin users error: {e}")
        flash('Error loading users', 'error')
        return render_template('admin/users.html', users=[])

@app.route('/admin/delete-user/<user_id>', methods=['POST'])
def admin_delete_user(user_id):
    """Delete user from database"""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Access denied'})

    try:
        # Check if user exists
        user_response = get_supabase().table('users').select('*').eq('id', user_id).execute()
        if not user_response.data:
            return jsonify({'success': False, 'message': 'User not found'})

        # Delete user from database
        response = get_supabase().table('users').delete().eq('id', user_id).execute()

        if response.data:
            flash('User deleted successfully', 'success')
            return jsonify({'success': True, 'message': 'User deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to delete user'})

    except Exception as e:
        print(f"Delete user error: {e}")
        return jsonify({'success': False, 'message': 'Error deleting user'})

@app.route('/admin/add-product', methods=['POST'])
def admin_add_product():
    """Add new product with image upload"""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Access denied'})

    try:
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price'))
        stock = int(request.form.get('stock'))
        category = request.form.get('category')

        slug = generate_slug(name)

        # Handle image upload
        image_url = '/static/images/placeholder.jpg'
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                uploaded_image_url = save_product_image(file)
                if uploaded_image_url:
                    image_url = uploaded_image_url

        product_data = {
            'name': name,
            'slug': slug,
            'description': description,
            'price': price,
            'stock': stock,
            'category': category,
            'image_url': image_url,
            'created_at': datetime.utcnow().isoformat()
        }

        response = get_supabase().table('products').insert(product_data).execute()

        if response.data:
            flash('Product added successfully', 'success')
            return jsonify({'success': True, 'message': 'Product added successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to add product'})

    except Exception as e:
        print(f"Add product error: {e}")
        return jsonify({'success': False, 'message': 'Error adding product'})

@app.route('/admin/edit-product/<product_id>', methods=['GET', 'POST'])
def admin_edit_product(product_id):
    """Edit existing product"""
    if not is_admin():
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('admin_products'))

    try:
        if request.method == 'GET':
            # Get product details for editing
            response = get_supabase().table('products').select('*').eq('id', product_id).execute()
            product = response.data[0] if response.data else None

            if not product:
                flash('Product not found', 'error')
                return redirect(url_for('admin_products'))

            return render_template('admin/edit_product.html', product=product)

        else:  # POST request - update product
            name = request.form.get('name')
            description = request.form.get('description')
            price_str = request.form.get('price')
            stock_str = request.form.get('stock')
            category = request.form.get('category')

            try:
                price = float(price_str) if price_str else 0.0
            except (ValueError, TypeError):
                flash('Invalid price format', 'error')
                return redirect(url_for('admin_edit_product', product_id=product_id))

            try:
                stock = int(stock_str) if stock_str else 0
            except (ValueError, TypeError):
                flash('Invalid stock format', 'error')
                return redirect(url_for('admin_edit_product', product_id=product_id))

            slug = generate_slug(name)

            # Handle image upload
            image_url = request.form.get('current_image')
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '':
                    uploaded_image_url = save_product_image(file)
                    if uploaded_image_url:
                        image_url = uploaded_image_url

            product_data = {
                'name': name,
                'slug': slug,
                'description': description,
                'price': price,
                'stock': stock,
                'category': category,
                'image_url': image_url,
                'updated_at': datetime.utcnow().isoformat()
            }

            response = get_supabase().table('products').update(product_data).eq('id', product_id).execute()

            if response.data:
                flash('Product updated successfully', 'success')
                return redirect(url_for('admin_products'))
            else:
                flash('Failed to update product', 'error')
                return redirect(url_for('admin_edit_product', product_id=product_id))

    except Exception as e:
        print(f"Edit product error: {str(e)}")
        flash(f'Error updating product: {str(e)}', 'error')
        return redirect(url_for('admin_edit_product', product_id=product_id))

@app.route('/admin/delete-product/<product_id>', methods=['POST'])
def admin_delete_product(product_id):
    """Delete product"""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Access denied'})

    try:
        response = get_supabase().table('products').delete().eq('id', product_id).execute()

        if response.data:
            flash('Product deleted successfully', 'success')
            return jsonify({'success': True, 'message': 'Product deleted successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to delete product'})

    except Exception as e:
        print(f"Delete product error: {e}")
        return jsonify({'success': False, 'message': 'Error deleting product'})

@app.route('/admin/update-order-status', methods=['POST'])
def admin_update_order_status():
    """Update order status"""
    if not is_admin():
        return jsonify({'success': False, 'message': 'Access denied'})

    try:
        order_id = request.form.get('order_id')
        status = request.form.get('status')

        get_supabase().table('orders').update({'status': status}).eq('id', order_id).execute()

        flash('Order status updated successfully', 'success')
        return jsonify({'success': True, 'message': 'Order status updated'})

    except Exception as e:
        print(f"Update order status error: {e}")
        return jsonify({'success': False, 'message': 'Error updating order status'})

# Health check for Vercel
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'SomaliShop is running'})

if __name__ == '__main__':
    print("🟢 Starting SomaliShop Server...")
    print("🟢 Server will be available at: http://localhost:5000")
    print("🟢 Press CTRL+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)