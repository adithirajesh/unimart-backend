import csv
import os

from flask import Flask, jsonify, request, url_for
from flask_cors import CORS
from database import db, init_db
from models import User, Product, UserActivity
from routes.auth_routes import auth

app = Flask(__name__)
CORS(
    app,
    resources={r"/api/*": {"origins": "*"}},
    supports_credentials=True
)

# Initialize DB
init_db(app)
app.register_blueprint(auth, url_prefix="/api")

# -----------------------
# Setup demo products (only if none exist)
# -----------------------
def setup_demo_products():
    with app.app_context():
        if Product.query.count() == 0:
            csv_path = os.path.join(app.root_path, "static", "listings.csv")
            image_map = {
                "Mini-Fridge": "minifridge.png",
                "Study Desk Lamp": "desklamp.png",
                "Calculus III Notes": "mathnotes.png",
                "Ergonomic Desk Chair": "chair.png",
                "Blackout Curtains (Set of 2)": "curtains.png",
                "Yoga Mat": "yogamat.png",
                "HDMI Monitor (24-inch)": "monitor.png",
                "Bike Lock (U-Lock)": "lock.png",
                "Vacuum Cleaner (Small)": "vaccuum.png",
                "Iron & Ironing Board": "iron.png",
                "Formal Wear/Suit": "suit.png",
                "Outdoor Camping Tent": "tent.png",
                "Moving Boxes (Bulk)": "boxes.png",
                "Video Game Console (Older)": "wii.png",
                "Tool Kit (Basic)": "toolkit.png",
                "Portable Projector": "projector.png",
                "Language Learning Books": "book.png",
            }

            demo_products = []
            with open(csv_path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get("Name", "").strip()
                    price_raw = row.get("Price", "0").strip()
                    description = row.get("Description", "").strip()

                    try:
                        price = float(price_raw)
                    except ValueError:
                        price = 0

                    image_filename = image_map.get(name, "book.png")
                    image_url = url_for( "static", filename=f"images/{image_filename}")

                    demo_products.append(
                        Product(
                            name=name,
                            price=price,
                            description=description,
                            image=image_url
                        )
                    )

            if demo_products:
                db.session.add_all(demo_products)
                db.session.commit()

# -----------------------
# Routes
# -----------------------
@app.route("/")
def index():
    return "Unimarket API running with SQLite!"

# Signup route
@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.json
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "Name and email required"}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"message": "User already exists", "user_id": user.id})

    new_user = User(name=name, email=email)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created", "user_id": new_user.id})

# Log user activity
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=email).first()


    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email
        }
    }), 200

@app.route("/api/activity", methods=["POST"])
def log_activity():
    data = request.get_json()
    user_id = data.get("user_id")
    product_id = data.get("product_id")
    action = data.get("action")

    if not user_id or not product_id or not action:
        return jsonify({"error": "user_id, product_id, and action required"}), 400

    activity = UserActivity(user_id=user_id, product_id=product_id, action=action)
    db.session.add(activity)
    db.session.commit()

    return jsonify({"message": "Activity logged successfully"})


# List all products
@app.route("/api/products")
def get_products():
    products = Product.query.all()
    return jsonify([
        {
            "id": p.id,
            "name": p.name,
            "price": p.price,
            "description": getattr(p, "description", ""),
            "image": getattr(p, "image", "")
        }
        for p in products
    ])
@app.route("/api/debug/db")
def debug_db():
    try:
        users_count = User.query.count()
        products_count = Product.query.count()
        return {"users": users_count, "products": products_count}
    except Exception as e:
        return {"error": str(e)}, 500
        
@app.route("/api/debug/reset-products", methods=["POST"])
def reset_products():
    Product.query.delete()
    db.session.commit()
    setup_demo_products()
    return {"message": "Products reset"}


# Get product by ID (optionally logs view if user_id is provided)
@app.route("/api/products/<int:pid>")
def get_product_by_id(pid):
    p = Product.query.get(pid)
    if not p:
        return jsonify({"error": "Product not found"}), 404

    user_id = request.args.get("user_id")  # Optional query param
    if user_id:
        activity = UserActivity(user_id=user_id, product_id=pid, action="view")
        db.session.add(activity)
        db.session.commit()

    return jsonify({
        "id": p.id,
        "name": p.name,
        "price": p.price,
        "description": getattr(p, "description", ""),
        "image": getattr(p, "image", "")
    })
setup_demo_products()

# -----------------------
# Run the app
# -----------------------
if __name__ == "__main__":
    app.run(debug=True)




