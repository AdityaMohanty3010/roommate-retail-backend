from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
import os
import traceback

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize Flask app
app = Flask(__name__)

# ✅ JWT Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY") or "default-secret"
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
jwt = JWTManager(app)

# ✅ CORS Configuration for frontend
CORS(
    app,
    resources={r"/api/*": {"origins": [
        "http://localhost:5173",
        "https://roommate-retail-frontend-btca.vercel.app"
    ]}},
    supports_credentials=True,
    methods=["GET", "POST", "OPTIONS", "DELETE"]
)

# ✅ SQLAlchemy Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///dev.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ✅ Initialize DB
from models import db  # models.py in same directory
db.init_app(app)

# 🟢 Create DB Tables on startup (Flask 3.x safe)
with app.app_context():
    db.create_all()

# ✅ Import and register blueprints
from auth.routes import auth_bp
from group.routes import group_bp
from cart.routes import cart_bp

app.register_blueprint(auth_bp, url_prefix="/api")
app.register_blueprint(group_bp, url_prefix="/api")
app.register_blueprint(cart_bp, url_prefix="/api")

# ✅ AI Shopping List Handler
from ai.huddle_ai import get_structured_shopping_list

@app.route("/api/huddle", methods=["POST"])
def huddle_ai():
    try:
        data = request.get_json()
        preferences = data.get("prompt", "")
        if not preferences:
            return jsonify({"error": "Prompt is required"}), 400

        result = get_structured_shopping_list(preferences, "medium")
        if isinstance(result, dict) and result.get("error"):
            return jsonify(result), 500

        return jsonify({"categories": result})
    except Exception as e:
        print("❌ Exception in /api/huddle")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# ✅ Health Check Routes
@app.route("/")
def home():
    return jsonify({"message": "RoomMate Retail backend is running!"})

@app.route("/ping")
def ping():
    return jsonify({"status": "ok"})

# ✅ Run the Flask server
if __name__ == "__main__":
    app.run(debug=True, port=5000)
