from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Group

group_bp = Blueprint("group", __name__)

# ✅ Create a new group
@group_bp.route('/create-group', methods=['POST'])
@jwt_required()
def create_group():
    data = request.get_json()
    group_name = data.get("groupName")
    user_email = get_jwt_identity()

    if not group_name:
        return jsonify({"error": "Group name is required"}), 400

    existing_group = Group.query.filter_by(name=group_name).first()
    if existing_group:
        return jsonify({"error": "Group already exists"}), 400

    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.group_id is not None:
        return jsonify({"error": "User already in a group"}), 400

    # Create and commit new group
    new_group = Group(name=group_name, budget=0)
    db.session.add(new_group)
    db.session.commit()

    # Assign user to group
    user.group_id = new_group.id
    db.session.commit()

    # Fetch usernames of members
    members = User.query.filter_by(group_id=new_group.id).all()
    member_usernames = ["👤 " + member.username for member in members]

    return jsonify({
        "message": f"Group '{group_name}' created",
        "groupName": group_name,
        "groupId": new_group.id,
        "members": member_usernames,
        "budget": new_group.budget
    }), 201

# ✅ Join an existing group
@group_bp.route('/join-group', methods=['POST'])
@jwt_required()
def join_group():
    data = request.get_json()
    group_name = data.get("groupName")
    user_email = get_jwt_identity()

    if not group_name:
        return jsonify({"error": "Group name is required"}), 400

    group = Group.query.filter_by(name=group_name).first()
    if not group:
        return jsonify({"error": "Group does not exist"}), 404

    user = User.query.filter_by(email=user_email).first()
    if not user:
        return jsonify({"error": "User not found"}), 404
    if user.group_id is not None:
        return jsonify({"error": "User already in a group"}), 400

    user.group_id = group.id
    db.session.commit()

    members = User.query.filter_by(group_id=group.id).all()
    member_usernames = ["👤 " + member.username for member in members]

    return jsonify({
        "message": f"Joined group '{group_name}'",
        "groupName": group.name,
        "groupId": group.id,
        "members": member_usernames,
        "budget": group.budget
    }), 200

# ✅ Get the group info of the logged-in user
@group_bp.route('/group-info', methods=['GET'])
@jwt_required()
def get_group_info():
    user_email = get_jwt_identity()
    user = User.query.filter_by(email=user_email).first()

    if not user or not user.group_id:
        return jsonify({"error": "You are not a part of any group yet!"}), 404

    group = Group.query.get(user.group_id)
    members = User.query.filter_by(group_id=group.id).all()
    member_usernames = ["👤 " + member.username for member in members]

    return jsonify({
        "groupName": group.name,
        "groupId": group.id,
        "members": member_usernames,
        "budget": group.budget
    }), 200
