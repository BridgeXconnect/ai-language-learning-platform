"""
Auth Domain - Routes
Consolidated from: auth_routes.py, server_routes_auth.py
"""

from app import db
from app.core.database import get_db
from app.domains.auth.models import User, PasswordResetToken
from app.domains.auth.schemas import (
from app.domains.auth.services import AuthService
from app.services.email_service import send_password_reset_email
from app.domains.auth.services import UserService
from datetime import datetime, timedelta
from email_validator import validate_email, EmailNotValidError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
from marshmallow import Schema, fields, validate, ValidationError
from sqlalchemy.orm import Session
from starlette.status import HTTP_401_UNAUTHORIZED
import secrets
import uuid

class LoginSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=6))



class RegisterSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    first_name = fields.Str(validate=validate.Length(max=100))
    last_name = fields.Str(validate=validate.Length(max=100))
    role = fields.Str(validate=validate.OneOf(['student', 'trainer', 'sales', 'course_manager']))



class PasswordResetRequestSchema(Schema):
    email = fields.Email(required=True)



class PasswordResetSchema(Schema):
    token = fields.Str(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))



class ProfileUpdateSchema(Schema):
    first_name = fields.Str(validate=validate.Length(max=100))
    last_name = fields.Str(validate=validate.Length(max=100))
    phone = fields.Str(validate=validate.Length(max=20))


# Routes
@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    schema = RegisterSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 409
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 409
    
    try:
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role=data.get('role', 'student'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        
        db.session.add(user)
        db.session.commit()
        
        current_app.logger.info(f'New user registered: {user.username} ({user.email})')
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Registration error: {str(e)}')
        return jsonify({'message': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return access token."""
    schema = LoginSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Find user by username or email
    user = User.get_by_username_or_email(data['username'])
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'message': 'Account is deactivated'}), 401
    
    # Create tokens
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            'username': user.username,
            'role': user.role,
            'email': user.email
        }
    )
    refresh_token = create_refresh_token(identity=user.id)
    
    # Update last login
    user.update_last_login()
    
    current_app.logger.info(f'User logged in: {user.username}')
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token using refresh token."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({'message': 'User not found or inactive'}), 404
    
    new_token = create_access_token(
        identity=user.id,
        additional_claims={
            'username': user.username,
            'role': user.role,
            'email': user.email
        }
    )
    
    return jsonify({
        'access_token': new_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout user (client-side token removal)."""
    # In a production app, you might want to blacklist the token
    # For now, we'll just return a success message
    return jsonify({'message': 'Successfully logged out'}), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user's profile."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_dict()
    }), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user's profile."""
    schema = ProfileUpdateSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Update user fields
    for field, value in data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    try:
        db.session.commit()
        
        current_app.logger.info(f'Profile updated: {user.username}')
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Profile update error: {str(e)}')
        return jsonify({'message': 'Profile update failed'}), 500


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset."""
    schema = PasswordResetRequestSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    # Always return success to prevent email enumeration
    if user:
        # Generate reset token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        
        # Create reset token record
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        
        db.session.add(reset_token)
        
        try:
            db.session.commit()
            
            # Send password reset email
            send_password_reset_email(user.email, user.username, token)
            
            current_app.logger.info(f'Password reset requested for: {user.email}')
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Password reset error: {str(e)}')
    
    return jsonify({
        'message': 'If your email is registered, you will receive password reset instructions'
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password using token."""
    schema = PasswordResetSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Find valid reset token
    reset_token = PasswordResetToken.query.filter_by(
        token=data['token']
    ).first()
    
    if not reset_token or not reset_token.is_valid:
        return jsonify({'message': 'Invalid or expired reset token'}), 400
    
    # Update user password
    user = reset_token.user
    user.set_password(data['password'])
    
    # Mark token as used
    reset_token.mark_as_used()
    
    try:
        db.session.commit()
        
        current_app.logger.info(f'Password reset completed for: {user.username}')
        
        return jsonify({'message': 'Password reset successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Password reset error: {str(e)}')
        return jsonify({'message': 'Password reset failed'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password for authenticated user."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'message': 'Current password and new password are required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'message': 'New password must be at least 6 characters'}), 400
    
    # Verify current password
    if not user.check_password(current_password):
        return jsonify({'message': 'Current password is incorrect'}), 400
    
    # Update password
    user.set_password(new_password)
    
    try:
        db.session.commit()
        
        current_app.logger.info(f'Password changed for: {user.username}')
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Password change error: {str(e)}')
        return jsonify({'message': 'Password change failed'}), 500


@auth_bp.route('/validate-token', methods=['POST'])
@jwt_required()
def validate_token():
    """Validate JWT token."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({'message': 'Invalid token or user inactive'}), 401
    
    return jsonify({
        'message': 'Token is valid',
        'user': user.to_dict()
    }), 200


# Error handlers
@auth_bp.errorhandler(400)
def bad_request(error):
    return jsonify({'message': 'Bad request'}), 400


@auth_bp.errorhandler(401)
def unauthorized(error):
    return jsonify({'message': 'Unauthorized'}), 401


@auth_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'message': 'Internal server error'}), 500

def register():
    """Register a new user."""
    schema = RegisterSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'Username already exists'}), 409
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email already exists'}), 409
    
    try:
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role=data.get('role', 'student'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        
        db.session.add(user)
        db.session.commit()
        
        current_app.logger.info(f'New user registered: {user.username} ({user.email})')
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Registration error: {str(e)}')
        return jsonify({'message': 'Registration failed'}), 500


@auth_bp.route('/login', methods=['POST'])

def login():
    """Authenticate user and return access token."""
    schema = LoginSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Find user by username or email
    user = User.get_by_username_or_email(data['username'])
    
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401
    
    if not user.is_active:
        return jsonify({'message': 'Account is deactivated'}), 401
    
    # Create tokens
    access_token = create_access_token(
        identity=user.id,
        additional_claims={
            'username': user.username,
            'role': user.role,
            'email': user.email
        }
    )
    refresh_token = create_refresh_token(identity=user.id)
    
    # Update last login
    user.update_last_login()
    
    current_app.logger.info(f'User logged in: {user.username}')
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)

def refresh():
    """Refresh access token using refresh token."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({'message': 'User not found or inactive'}), 404
    
    new_token = create_access_token(
        identity=user.id,
        additional_claims={
            'username': user.username,
            'role': user.role,
            'email': user.email
        }
    )
    
    return jsonify({
        'access_token': new_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()

def logout():
    """Logout user (client-side token removal)."""
    # In a production app, you might want to blacklist the token
    # For now, we'll just return a success message
    return jsonify({'message': 'Successfully logged out'}), 200


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()

def get_profile():
    """Get current user's profile."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    return jsonify({
        'user': user.to_dict()
    }), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()

def update_profile():
    """Update current user's profile."""
    schema = ProfileUpdateSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    # Update user fields
    for field, value in data.items():
        if hasattr(user, field):
            setattr(user, field, value)
    
    try:
        db.session.commit()
        
        current_app.logger.info(f'Profile updated: {user.username}')
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Profile update error: {str(e)}')
        return jsonify({'message': 'Profile update failed'}), 500


@auth_bp.route('/forgot-password', methods=['POST'])

def forgot_password():
    """Request password reset."""
    schema = PasswordResetRequestSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    # Always return success to prevent email enumeration
    if user:
        # Generate reset token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
        
        # Create reset token record
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at
        )
        
        db.session.add(reset_token)
        
        try:
            db.session.commit()
            
            # Send password reset email
            send_password_reset_email(user.email, user.username, token)
            
            current_app.logger.info(f'Password reset requested for: {user.email}')
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Password reset error: {str(e)}')
    
    return jsonify({
        'message': 'If your email is registered, you will receive password reset instructions'
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])

def reset_password():
    """Reset password using token."""
    schema = PasswordResetSchema()
    
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({'message': 'Validation error', 'errors': err.messages}), 400
    
    # Find valid reset token
    reset_token = PasswordResetToken.query.filter_by(
        token=data['token']
    ).first()
    
    if not reset_token or not reset_token.is_valid:
        return jsonify({'message': 'Invalid or expired reset token'}), 400
    
    # Update user password
    user = reset_token.user
    user.set_password(data['password'])
    
    # Mark token as used
    reset_token.mark_as_used()
    
    try:
        db.session.commit()
        
        current_app.logger.info(f'Password reset completed for: {user.username}')
        
        return jsonify({'message': 'Password reset successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Password reset error: {str(e)}')
        return jsonify({'message': 'Password reset failed'}), 500


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()

def change_password():
    """Change password for authenticated user."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404
    
    data = request.json
    current_password = data.get('current_password')
    new_password = data.get('new_password')
    
    if not current_password or not new_password:
        return jsonify({'message': 'Current password and new password are required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'message': 'New password must be at least 6 characters'}), 400
    
    # Verify current password
    if not user.check_password(current_password):
        return jsonify({'message': 'Current password is incorrect'}), 400
    
    # Update password
    user.set_password(new_password)
    
    try:
        db.session.commit()
        
        current_app.logger.info(f'Password changed for: {user.username}')
        
        return jsonify({'message': 'Password changed successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Password change error: {str(e)}')
        return jsonify({'message': 'Password change failed'}), 500


@auth_bp.route('/validate-token', methods=['POST'])
@jwt_required()

def validate_token():
    """Validate JWT token."""
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    
    if not user or not user.is_active:
        return jsonify({'message': 'Invalid token or user inactive'}), 401
    
    return jsonify({
        'message': 'Token is valid',
        'user': user.to_dict()
    }), 200


# Error handlers
@auth_bp.errorhandler(400)

def bad_request(error):
    return jsonify({'message': 'Bad request'}), 400


@auth_bp.errorhandler(401)

def unauthorized(error):
    return jsonify({'message': 'Unauthorized'}), 401


@auth_bp.errorhandler(500)

def internal_error(error):
    db.session.rollback()
    return jsonify({'message': 'Internal server error'}), 500