# app/api/auth.py
from flask import request, jsonify, current_app
from flask.views import MethodView
from app.extensions import db
from app.models.user import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, create_refresh_token
import datetime

# Use a Blueprint for auth routes
from flask import Blueprint
auth_bp = Blueprint('auth_bp', __name__)

class RegisterAPI(MethodView):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return jsonify({"msg": "Missing username, email, or password"}), 400

        if User.query.filter_by(username=username).first() or \
           User.query.filter_by(email=email).first():
            return jsonify({"msg": "User already exists"}), 409 # 409 Conflict

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return jsonify({"msg": "User created successfully", "user_id": user.id}), 201

class LoginAPI(MethodView):
    def post(self):
        data = request.get_json()
        username_or_email = data.get('username_or_email')
        password = data.get('password')

        if not username_or_email or not password:
            return jsonify({"msg": "Missing username/email or password"}), 400

        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()

        if user and user.check_password(password):
            access_token = create_access_token(identity=str(user.id))
            # refresh_token = create_refresh_token(identity=user.id) # If using refresh tokens
            
            return jsonify(
                access_token=access_token,
                # refresh_token=refresh_token,
                user_id=user.id,
                username=user.username
            ), 200
        else:
            return jsonify({"msg": "Bad username or password"}), 401

# If you implement refresh tokens:
# class TokenRefreshAPI(MethodView):
#     @jwt_required(refresh=True)
#     def post(self):
#         current_user_id = get_jwt_identity()
#         new_access_token = create_access_token(identity=current_user_id)
#         return jsonify(access_token=new_access_token), 200

class ProtectedAPI(MethodView):
    """ Example of a protected route """
    decorators = [jwt_required()]

    def get(self):
        current_user_id = int(get_jwt_identity())
        user = User.query.get(current_user_id)
        if not user:
             return jsonify({"msg": "User not found"}), 404
        return jsonify(logged_in_as=user.username, user_id=user.id), 200


# Registering the views with the blueprint
auth_bp.add_url_rule('/register', view_func=RegisterAPI.as_view('register_api'), methods=['POST'])
auth_bp.add_url_rule('/login', view_func=LoginAPI.as_view('login_api'), methods=['POST'])
# auth_bp.add_url_rule('/refresh', view_func=TokenRefreshAPI.as_view('refresh_api'), methods=['POST'])
auth_bp.add_url_rule('/protected', view_func=ProtectedAPI.as_view('protected_api'), methods=['GET'])

# You might also want a /logout endpoint, which for JWT typically involves
# client-side token deletion and possibly server-side token blocklisting if using refresh tokens.
# For simplicity, we'll skip blocklisting for now.