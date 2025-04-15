from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_mail import Mail, Message
import random


app = Flask(__name__)
# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # or your SMTP provider
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'bradprinceltd@gmail.com'
app.config['MAIL_PASSWORD'] = 'adrs seoa sjcz uggj'  # Use app password if needed
app.config['MAIL_DEFAULT_SENDER'] = 'bradprinceltd@gmail.com'

mail = Mail(app)
app.secret_key = 'your_secret_key'

# Dummy product data
products = [
    {"id": "bundle", "name": "The Good Snus - Bundle", "price": 24.99, "image": "bundle_pot.png"},
    {"id": "original", "name": "The Good Snus - Original", "price": 6.99, "image": "black_pot.png"},
    {"id": "white", "name": "The Good Snus - Snow White", "price": 6.99, "image": "white_pot.png"},
    {"id": "blue", "name": "The Good Snus - Ocean Blue", "price": 6.99, "image": "blue_pot.png"},
    {"id": "green", "name": "The Good Snus - Herbal Green", "price": 6.99, "image": "green_pot.png"},
]

product_dict = {p["id"]: p for p in products}


@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '').lower()

    # Very basic FAQ-style logic
    if "shipping" in message:
        reply = "We offer free shipping on all orders over £30!"
    elif "return" in message:
        reply = "You can return unopened products within 14 days."
    elif "contact" in message or "email" in message:
        reply = "You can reach us at support@thegoodsnus.com."
    else:
        reply = "I'm here to help! Could you rephrase that?"

    return jsonify({'reply': reply})


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/shop')
def shop():
    return render_template('shop.html', products=products)


@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    product_id = request.form['product_id']
    cart = session.get('cart', {})
    cart[product_id] = cart.get(product_id, 0) + 1
    session['cart'] = cart
    return redirect(url_for('shop'))


@app.route('/cart', methods=['GET', 'POST'])
def cart():
    cart = session.get('cart', {})

    if request.method == 'POST':
        updated_cart = cart.copy()

        if 'update' in request.form:
            for key in list(cart.keys()):
                qty_key = f'quantity_{key}'
                if qty_key in request.form:
                    try:
                        new_qty = int(request.form[qty_key])
                        if new_qty > 0:
                            updated_cart[key] = new_qty
                        else:
                            updated_cart.pop(key, None)
                    except ValueError:
                        pass  # Skip invalid input

        elif 'remove' in request.form:
            remove_id = request.form['remove']
            updated_cart.pop(remove_id, None)

        session['cart'] = updated_cart
        return redirect(url_for('cart'))

    cart_items = {}
    total = 0
    for item_id, quantity in cart.items():
        if item_id in product_dict:
            item = product_dict[item_id]
            item_total = item["price"] * quantity
            total += item_total
            cart_items[item_id] = {
                "name": item["name"],
                "price": item["price"],
                "quantity": quantity,
                "total": f"{item_total:.2f}"
            }

    return render_template('cart.html', cart_items=cart_items, total=total)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        email = request.form['email']
        payment = request.form['payment']

        cart = session.get('cart', {})
        cart_items = []
        total = 0

        for item_id, qty in cart.items():
            product = product_dict.get(item_id)
            if product:
                item_total = product['price'] * qty
                total += item_total
                cart_items.append({
                    "name": product['name'],
                    "price": product['price'],
                    "quantity": qty,
                    "total": item_total,
                    "image_url": url_for('static', filename=f'images/{product["image"]}', _external=True)
                })

        order_number = f"GS{random.randint(1000,9999)}"

        # Use HTML template for email
        email_html = render_template('email_template.html', name=name, address=address,
                                     order_number=order_number, cart_items=cart_items, total=total)

        try:
            msg = Message(subject=f"Order Confirmation - {order_number}",
                          recipients=[email])
            msg.html = email_html
            mail.send(msg)
        except Exception as e:
            print("Email send failed:", e)

        session.pop('cart', None)
        return redirect(url_for('confirmation', name=name))

    return render_template('checkout.html')


@app.route('/confirmation')
def confirmation():
    name = request.args.get('name', 'Customer')
    return render_template('confirmation.html', name=name)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')



