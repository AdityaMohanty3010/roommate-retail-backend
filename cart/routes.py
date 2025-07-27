from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Group, CartItem

cart_bp = Blueprint("cart", __name__)

# ✅ GET /api/cart — fetch shared cart for group
@cart_bp.route('/cart', methods=['GET'])
@jwt_required()
def get_cart():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    if not user or not user.group_id:
        return jsonify({"error": "User not in a group"}), 400

    cart_items = CartItem.query.filter_by(group_id=user.group_id).all()

    cart_data = [
        {
            "item": item.name,
            "category": item.category,
            "quantity": item.quantity,
            "price": item.quantity,  # You can adjust if total pricing logic changes
            "added_by": item.contributor
        }
        for item in cart_items
    ]

    return jsonify(cart_data), 200

# ✅ POST /api/cart — add item or update quantity
@cart_bp.route('/cart', methods=['POST'])
@jwt_required()
def add_item():
    user_email = get_jwt_identity()
    data = request.get_json()

    item = data.get("item")
    category = data.get("category", "Uncategorized")
    quantity = data.get("quantity", 1)
    price = data.get("price", 0.0)
    username = data.get("username", "🧑 Unknown")

    if not item:
        return jsonify({"error": "Item name is required"}), 400

    user = User.query.filter_by(email=user_email).first()
    if not user or not user.group_id:
        return jsonify({"error": "User not in a group"}), 400

    # 🔁 Check if item already exists for the group
    existing_item = CartItem.query.filter_by(
        group_id=user.group_id, name=item
    ).first()

    if existing_item:
        existing_item.quantity += quantity
        db.session.commit()
        return jsonify({
            "message": "Quantity updated",
            "cart": get_group_cart_data(user.group_id)
        }), 200

    # ➕ Add new item
    new_item = CartItem(
        name=item,
        category=category,
        quantity=quantity,
        contributor=username,
        group_id=user.group_id
    )
    db.session.add(new_item)
    db.session.commit()

    return jsonify({
        "message": "Item added",
        "cart": get_group_cart_data(user.group_id)
    }), 201

# 🗑️ DELETE /api/cart/<item_name> — remove a specific item
@cart_bp.route('/cart/<item_name>', methods=['DELETE'])
@jwt_required()
def delete_item(item_name):
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    if not user or not user.group_id:
        return jsonify({"error": "User not in a group"}), 400

    item = CartItem.query.filter_by(group_id=user.group_id, name=item_name).first()
    if item:
        db.session.delete(item)
        db.session.commit()

    return jsonify({
        "message": f"{item_name} removed",
        "cart": get_group_cart_data(user.group_id)
    }), 200

# 🧹 DELETE /api/cart — clear all items from group cart
@cart_bp.route('/cart', methods=['DELETE'])
@jwt_required()
def clear_cart():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    if not user or not user.group_id:
        return jsonify({"error": "User not in a group"}), 400

    CartItem.query.filter_by(group_id=user.group_id).delete()
    db.session.commit()

    return jsonify({
        "message": "Cart cleared successfully",
        "cart": []
    }), 200

# 🔧 Helper: Get all items in group cart
def get_group_cart_data(group_id):
    cart_items = CartItem.query.filter_by(group_id=group_id).all()
    return [
        {
            "item": item.name,
            "category": item.category,
            "quantity": item.quantity,
            "price": item.quantity,  # You can adjust pricing here
            "added_by": item.contributor
        }
        for item in cart_items
    ]
