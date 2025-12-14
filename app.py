from flask import Flask, jsonify, request
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
            demo_products = [
                Product(
                    name="Organic Chemistry Textbook",
                    price=20,
                    description="Year 1 chem textbook, light notes",
                    image="https://picsum.photos/300?random=1"
                ),
                Product(
                    name="IB Biology HL Textbook",
                    price=18,
                    description="Used but clean",
                    image="https://picsum.photos/300?random=2"
                ),
                Product(
                    name="Casio FX-CG50 Calculator",
                    price=45,
                    description="Allowed in exams",
                    image="https://picsum.photos/300?random=3"
                ),
                Product(
                    name="Imperial College Hoodie",
                    price=25,
                    description="Size M, worn twice",
                    image="https://picsum.photos/300?random=4"
                ),
                Product(
                    name="Desk Lamp",
                    price=12,
                    description="LED, adjustable brightness",
                    image="https://picsum.photos/300?random=5"
                ),
                Product(
                    name="Rice Cooker",
                    price=32,
                    description="Great for dorm cooking",
                    image="https://picsum.photos/300?random=6"
                ),
                Product(
                    name="Sony Noise Cancelling Headphones",
                    price=70,
                    description="XM3 model",
                    image="https://picsum.photos/300?random=7"
                ),
                Product(
                    name="Board Game – Catan",
                    price=20,
                    description="All pieces included",
                    image="https://picsum.photos/300?random=8"
                ),
                Product(
                    name="Lab Coat",
                    price=20,
                    description="Year 1 chem textbook, light notes",
                    image="https://picsum.photos/300?random=1"
                ),
                Product(
                    name="Sneakers",
                    price=18,
                    description="Used but clean",
                    image="https://picsum.photos/300?random=2"
                ),
                Product(
                    name="Mountain bike",
                    price=45,
                    description="Allowed in exams",
                    image="https://picsum.photos/300?random=3"
                ),
                Product(
                    name="Bedside table",
                    price=25,
                    description="Size M, worn twice",
                    image="https://picsum.photos/300?random=4"
                ),
                Product(
                    name="Water bottle",
                    price=12,
                    description="LED, adjustable brightness",
                    image="https://picsum.photos/300?random=5"
                ),
                Product(
                    name="Rice Cooker",
                    price=32,
                    description="Great for dorm cooking",
                    image="https://picsum.photos/300?random=6"
                ),
                Product(
                    name="Sony Noise Cancelling Headphones",
                    price=70,
                    description="XM3 model",
                    image="https://picsum.photos/300?random=7"
                ),
                Product(
                    name="Board Game – Catan",
                    price=20,
                    description="All pieces included",
                    image="https://picsum.photos/300?random=8"
                ),
            ]


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
