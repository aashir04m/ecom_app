from flask import Flask, request, jsonify, send_from_directory, url_for
import sqlite3
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)

# SQLite database
def connect_db():
    return sqlite3.connect('ecommerce.db')

@app.route('/', methods=['GET'])
def hello():
    return "Hello"

# Login route
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify(message='Invalid input'), 400

    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, role, logged_in FROM users WHERE username=? AND password=?', (username, password))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify(message='Invalid credentials'), 401

    # Check if the user is already logged in
    if user[2]:
        conn.close()
        return jsonify(message=f'{user[1]} is already logged in'), 401

    cursor.execute('UPDATE users SET logged_in = 1 WHERE id = ?', (user[0],))
    conn.commit()
    conn.close()

    return jsonify(message=f'Logged in successfully as {user[1]}'), 200

# Logout route
@app.route('/logout', methods=['POST'])
def logout():
    username = request.json.get('username')

    if not username:
        return jsonify(message='Invalid input'), 400

    conn = sqlite3.connect('ecommerce.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id, logged_in FROM users WHERE username=?', (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify(message='User not found'), 404

    # Check if the user is already logged out
    if not user[1]:
        conn.close()
        return jsonify(message=f'{username} is already logged out'), 401

    cursor.execute('UPDATE users SET logged_in = 0 WHERE id = ?', (user[0],))
    conn.commit()
    conn.close()

    return jsonify(message=f'Logged out successfully: {username}'), 200

# Upload product for Shopper with image
@app.route('/upload_product', methods=['POST'])
def upload_product():
    username = request.form.get('username')  # Get the username from the form data

    if not username:
        return jsonify(message='Invalid input'), 400

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id, role, logged_in FROM users WHERE username=?', (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify(message='User not found'), 404

    if user[2] == 0:  
        conn.close()
        return jsonify(message=f'{username} is not logged in'), 401

    if user[1] != 'Shopper':
        conn.close()
        return jsonify(message='Unauthorized'), 403

    product_name = request.form.get('product_name')
    price = request.form.get('price')
    uploaded_image = request.files.get('image')

    if not product_name or not price or not uploaded_image:
        conn.close()
        return jsonify(message='Invalid input'), 400

    allowed_extensions = {'jpg', 'jpeg', 'png'}
    if '.' not in uploaded_image.filename or \
            uploaded_image.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        conn.close()
        return jsonify(message='Invalid image format. Allowed formats: jpg, jpeg, png'), 400

    shopper_id = user[0]

    # Save the uploaded image
    image_filename = secure_filename(uploaded_image.filename)
    image_path = os.path.join('uploads', image_filename)
    uploaded_image.save(image_path)

    cursor.execute(
        'INSERT INTO products (product_name, price, image_path, shopper_id) VALUES (?, ?, ?, ?)',
        (product_name, price, image_path, shopper_id))
    conn.commit()
    conn.close()

    return jsonify(message='Product uploaded successfully'), 200

# Show products to Client
@app.route('/products', methods=['POST'])
def view_products():
    username = request.json.get('username')  

    if not username:
        return jsonify(message='Invalid input'), 400

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute('SELECT id, logged_in FROM users WHERE username=?', (username,))
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify(message='User not found'), 404

    if user[1] == 0:  
        conn.close()
        return jsonify(message=f'{username} is not logged in'), 401

    cursor.execute('SELECT id, product_name, price, image_path FROM products')
    products = cursor.fetchall()

    conn.close()

    product_list = []
    for product in products:
        product_dict = {
            'id': product[0],
            'product_name': product[1],
            'price': product[2],
            'image_path': product[3]
        }
        product_list.append(product_dict)

    return jsonify(products=product_list), 200

@app.route('/uploads/<filename>')
def uploaded_image(filename):
    return send_from_directory('uploads', filename)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8088)
