from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User, Role, Permission
from app.services.auth_service import AuthService

class UserService:
    @staticmethod
    def create_user(
        db: Session,
        username: str,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        roles: Optional[List[str]] = None
    ) -> User:
        # Hash password
        hashed_password = AuthService.get_password_hash(password)
        
        # Create user instance
        user = User(
            username=username,
            email=email,
            password_hash=hashed_password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Add roles if provided
        if roles:
            role_instances = db.query(Role).filter(Role.name.in_(roles)).all()
            user.user_roles_rel = role_instances
        
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise ValueError("Username or email already exists")

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_users(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None
    ) -> List[User]:
        query = db.query(User)
        if role:
            query = query.join(User.user_roles_rel).filter(Role.name == role)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update_user(
        db: Session,
        user_id: int,
        update_data: Dict
    ) -> Optional[User]:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return None
            
        # Update user fields
        for key, value in update_data.items():
            if key == 'password':
                user.password_hash = AuthService.get_password_hash(value)
            elif key == 'roles':
                role_instances = db.query(Role).filter(Role.name.in_(value)).all()
                user.user_roles_rel = role_instances
            elif hasattr(user, key):
                setattr(user, key, value)
        
        try:
            db.commit()
            db.refresh(user)
            return user
        except IntegrityError:
            db.rollback()
            raise ValueError("Update failed due to constraint violation")

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        user = UserService.get_user_by_id(db, user_id)
        if not user:
            return False
            
        try:
            db.delete(user)
            db.commit()
            return True
        except:
            db.rollback()
            return False

    @staticmethod
    def create_role(
        db: Session,
        name: str,
        description: Optional[str] = None,
        permissions: Optional[List[str]] = None
    ) -> Role:
        role = Role(name=name, description=description)
        
        if permissions:
            permission_instances = db.query(Permission).filter(
                Permission.name.in_(permissions)
            ).all()
            role.permissions = permission_instances
        
        try:
            db.add(role)
            db.commit()
            db.refresh(role)
            return role
        except IntegrityError:
            db.rollback()
            raise ValueError("Role name already exists")

    @staticmethod
    def get_role_by_name(db: Session, name: str) -> Optional[Role]:
        return db.query(Role).filter(Role.name == name).first()

    @staticmethod
    def create_permission(
        db: Session,
        name: str,
        description: Optional[str] = None
    ) -> Permission:
        permission = Permission(name=name, description=description)
        
        try:
            db.add(permission)
            db.commit()
            db.refresh(permission)
            return permission
        except IntegrityError:
            db.rollback()
            raise ValueError("Permission name already exists") 