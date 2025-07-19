from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import User, Role, Permission, user_roles, role_permissions
from app.models.course import Course, Module, Lesson
from app.models.sales import CourseRequest, SOPDocument, ClientFeedback, RequestStatus, Priority, CEFRLevel, DeliveryMethod
from app.services.auth_service import AuthService
from app.services.user_service import UserService

def create_initial_permissions(db: Session):
    """Create initial permissions"""
    permissions = [
        {"name": "create_course", "description": "Create new courses"},
        {"name": "edit_course", "description": "Edit existing courses"},
        {"name": "delete_course", "description": "Delete courses"},
        {"name": "review_course", "description": "Review and approve courses"},
        {"name": "manage_users", "description": "Manage user accounts"},
        {"name": "view_analytics", "description": "View system analytics"},
        {"name": "manage_settings", "description": "Manage system settings"},
        {"name": "access_sales", "description": "Access sales portal"},
        {"name": "access_trainer", "description": "Access trainer portal"},
        {"name": "access_student", "description": "Access student portal"},
    ]
    
    for perm_data in permissions:
        existing = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not existing:
            permission = Permission(**perm_data)
            db.add(permission)
    
    db.commit()

def create_initial_roles(db: Session):
    """Create initial roles with permissions"""
    roles_permissions = {
        "admin": [
            "create_course", "edit_course", "delete_course", "review_course",
            "manage_users", "view_analytics", "manage_settings",
            "access_sales", "access_trainer", "access_student"
        ],
        "course_manager": [
            "create_course", "edit_course", "delete_course", "review_course",
            "view_analytics"
        ],
        "sales": [
            "access_sales", "create_course"
        ],
        "trainer": [
            "access_trainer", "edit_course"
        ],
        "student": [
            "access_student"
        ]
    }
    
    for role_name, permission_names in roles_permissions.items():
        existing_role = db.query(Role).filter(Role.name == role_name).first()
        if not existing_role:
            role = Role(name=role_name, description=f"{role_name.title()} role")
            db.add(role)
            db.flush()  # Get the role ID
            
            # Add permissions to role
            permissions = db.query(Permission).filter(Permission.name.in_(permission_names)).all()
            role.permissions = permissions
    
    db.commit()

def create_initial_users(db: Session):
    """Create initial admin and demo users"""
    users_data = [
        {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "first_name": "System",
            "last_name": "Administrator",
            "roles": ["admin"]
        },
        {
            "username": "demo_sales",
            "email": "sales@example.com",
            "password": "demo123",
            "first_name": "Demo",
            "last_name": "Sales",
            "roles": ["sales"]
        },
        {
            "username": "demo_trainer",
            "email": "trainer@example.com",
            "password": "demo123",
            "first_name": "Demo",
            "last_name": "Trainer",
            "roles": ["trainer"]
        },
        {
            "username": "demo_student",
            "email": "student@example.com",
            "password": "demo123",
            "first_name": "Demo",
            "last_name": "Student",
            "roles": ["student"]
        },
        {
            "username": "demo_manager",
            "email": "manager@example.com",
            "password": "demo123",
            "first_name": "Demo",
            "last_name": "Manager",
            "roles": ["course_manager"]
        }
    ]
    
    for user_data in users_data:
        existing_user = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing_user:
            try:
                UserService.create_user(
                    db=db,
                    username=user_data["username"],
                    email=user_data["email"],
                    password=user_data["password"],
                    first_name=user_data["first_name"],
                    last_name=user_data["last_name"],
                    roles=user_data["roles"]
                )
                print(f"Created user: {user_data['username']}")
            except ValueError as e:
                print(f"Failed to create user {user_data['username']}: {e}")

def create_sample_course(db: Session):
    """Create a sample course for demonstration"""
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        return
    
    existing_course = db.query(Course).filter(Course.title == "Sample English Course").first()
    if not existing_course:
        course = Course(
            title="Sample English Course",
            description="A sample course for demonstration purposes",
            cefr_level="B1",
            status="approved",
            created_by=admin_user.id,
            approved_by=admin_user.id,
            ai_generated=False,
            course_request_id=None
        )
        db.add(course)
        db.flush()
        
        # Add sample module
        module = Module(
            course_id=course.id,
            title="Introduction to Business English",
            description="Basic business communication skills",
            sequence_number=1,
            duration_hours=4
        )
        db.add(module)
        db.flush()
        
        # Add sample lessons
        lessons = [
            {
                "title": "Greetings and Introductions",
                "content_id": "lesson_001",
                "sequence_number": 1,
                "duration_minutes": 45
            },
            {
                "title": "Email Communication",
                "content_id": "lesson_002",
                "sequence_number": 2,
                "duration_minutes": 60
            }
        ]
        
        for lesson_data in lessons:
            lesson = Lesson(
                module_id=module.id,
                title=lesson_data["title"],
                content_id=lesson_data["content_id"],
                sequence_number=lesson_data["sequence_number"],
                duration_minutes=lesson_data["duration_minutes"]
            )
            db.add(lesson)
        
        db.commit()
        print("Created sample course with modules and lessons")

def create_sample_sales_data(db: Session):
    """Create sample sales data for testing"""
    print("Creating sample sales data...")
    
    # Get sales user
    sales_user = db.query(User).filter(User.username == "demo_sales").first()
    if not sales_user:
        print("Sales user not found, skipping sales data creation")
        return
    
    # Create sample course requests
    sample_requests = [
        {
            "sales_user_id": sales_user.id,
            "company_name": "TechCorp Solutions",
            "industry": "Technology",
            "contact_person": "John Smith",
            "contact_email": "john.smith@techcorp.com",
            "contact_phone": "+1-555-0123",
            "cohort_size": 25,
            "current_cefr": CEFRLevel.B1,
            "target_cefr": CEFRLevel.B2,
            "training_objectives": "Improve technical communication skills for software development team",
            "pain_points": "Team struggles with technical documentation and client presentations",
            "specific_requirements": "Focus on technical vocabulary and presentation skills",
            "course_length_hours": 40,
            "lessons_per_module": 4,
            "delivery_method": DeliveryMethod.BLENDED,
            "preferred_schedule": "2 sessions per week, 2 hours each",
            "priority": Priority.HIGH,
            "status": RequestStatus.SUBMITTED
        },
        {
            "sales_user_id": sales_user.id,
            "company_name": "Global Finance Ltd",
            "industry": "Finance",
            "contact_person": "Sarah Johnson",
            "contact_email": "sarah.johnson@globalfinance.com",
            "contact_phone": "+1-555-0456",
            "cohort_size": 15,
            "current_cefr": CEFRLevel.A2,
            "target_cefr": CEFRLevel.B1,
            "training_objectives": "Enhance business English communication for international clients",
            "pain_points": "Difficulty in client meetings and email communication",
            "specific_requirements": "Business etiquette and financial terminology",
            "course_length_hours": 60,
            "lessons_per_module": 5,
            "delivery_method": DeliveryMethod.VIRTUAL,
            "preferred_schedule": "3 sessions per week, 1.5 hours each",
            "priority": Priority.NORMAL,
            "status": RequestStatus.IN_PROGRESS
        },
        {
            "sales_user_id": sales_user.id,
            "company_name": "MedCare Hospital",
            "industry": "Healthcare",
            "contact_person": "Dr. Michael Brown",
            "contact_email": "m.brown@medcare.com",
            "contact_phone": "+1-555-0789",
            "cohort_size": 30,
            "current_cefr": CEFRLevel.B2,
            "target_cefr": CEFRLevel.C1,
            "training_objectives": "Advanced medical English for international conferences",
            "pain_points": "Complex medical terminology and research presentation skills",
            "specific_requirements": "Medical vocabulary, research presentation, patient communication",
            "course_length_hours": 80,
            "lessons_per_module": 6,
            "delivery_method": DeliveryMethod.IN_PERSON,
            "preferred_schedule": "Weekly 4-hour intensive sessions",
            "priority": Priority.URGENT,
            "status": RequestStatus.DRAFT
        }
    ]
    
    created_requests = []
    for request_data in sample_requests:
        existing_request = db.query(CourseRequest).filter(
            CourseRequest.company_name == request_data["company_name"]
        ).first()
        
        if not existing_request:
            course_request = CourseRequest(**request_data)
            db.add(course_request)
            db.flush()  # Get the ID without committing
            created_requests.append(course_request)
            print(f"Created course request for {request_data['company_name']}")
    
    # Create sample SOP documents
    if created_requests:
        sample_sop = SOPDocument(
            request_id=created_requests[0].id,
            filename="techcorp_sop_v1.pdf",
            original_filename="TechCorp_Standard_Operating_Procedures.pdf",
            s3_key=f"sop-documents/{created_requests[0].id}/techcorp_sop_v1.pdf",
            content_type="application/pdf",
            file_size=2048576,  # 2MB
            processing_status="completed",
            extraction_status="completed",
            extracted_text_preview="This document outlines the standard operating procedures for software development...",
            upload_notes="Main SOP document for technical team training"
        )
        db.add(sample_sop)
        print("Created sample SOP document")
    
    # Create sample client feedback
    if created_requests:
        sample_feedback = ClientFeedback(
            request_id=created_requests[1].id,
            feedback_type="initial",
            rating=4,
            feedback_text="The proposed curriculum looks good, but we'd like more focus on email writing skills.",
            areas_of_concern="Email communication, formal writing",
            suggestions="Add more practical email scenarios and templates",
            feedback_by="Sarah Johnson",
            feedback_email="sarah.johnson@globalfinance.com",
            is_addressed=False
        )
        db.add(sample_feedback)
        print("Created sample client feedback")
    
    db.commit()
    print("Sample sales data created successfully!")

def init_database():
    """Initialize the database with initial data"""
    print("Initializing database...")
    
    # Create all tables
    from app.database import Base
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Creating initial permissions...")
        create_initial_permissions(db)
        
        print("Creating initial roles...")
        create_initial_roles(db)
        
        print("Creating initial users...")
        create_initial_users(db)
        
        print("Creating sample course...")
        create_sample_course(db)
        
        print("Creating sample sales data...")
        create_sample_sales_data(db)
        
        print("Database initialization completed successfully!")
        
    except Exception as e:
        print(f"Error during database initialization: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database() 