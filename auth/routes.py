from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User
import hashlib

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")

    if not email or not password or not username:
        return jsonify({"error": "Email, password, and username are required"}), 400

    # 🔍 Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    # 🔐 Hash the password
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()

    # ✅ Create new user
    new_user = User(email=email, password=hashed_pw, username=username)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # 🔍 Find user by email
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 🔐 Hash input password and compare
    hashed_pw = hashlib.sha256(password.encode()).hexdigest()
    if user.password != hashed_pw:
        return jsonify({"error": "Incorrect password"}), 401

    # 🎟️ Generate JWT with email as identity
    access_token = create_access_token(identity=email)
    return jsonify({"token": access_token, "username": user.username}), 200
