from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

# Association table for user roles
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    status = Column(String(20), nullable=False, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user_roles_rel = relationship("Role", secondary=user_roles, back_populates="users")
    course_requests = relationship("CourseRequest", back_populates="sales_user", lazy="dynamic")
    created_courses = relationship("Course", foreign_keys="Course.created_by", back_populates="creator", lazy="dynamic") 
    approved_courses = relationship("Course", foreign_keys="Course.approved_by", back_populates="approver", lazy="dynamic")

    @property
    def roles(self):
        return self.user_roles_rel

    def has_role(self, role_name: str) -> bool:
        return any(role.name == role_name for role in self.roles)

    def has_permission(self, permission_name: str) -> bool:
        for role in self.roles:
            if any(perm.name == permission_name for perm in role.permissions):
                return True
        return False

    def __repr__(self):
        return f"<User {self.username}>"

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'status': self.status,
            'roles': [role.name for role in self.user_roles_rel],
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

    # Relationships
    users = relationship('User', secondary=user_roles, back_populates='user_roles_rel')
    permissions = relationship('Permission', secondary='role_permissions')

    def __repr__(self):
        return f"<Role {self.name}>"

class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))

    def __repr__(self):
        return f"<Permission {self.name}>"

# Association table for role permissions
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
) 