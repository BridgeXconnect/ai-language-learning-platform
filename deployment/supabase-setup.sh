#!/bin/bash

# 🔧 Supabase Setup Script
# This script helps you set up Supabase access token and configure your database

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${BLUE}→${NC} $1"
}

# Function to get Supabase access token
get_supabase_token() {
    print_header "Setting up Supabase Access Token"
    
    echo -e "${BLUE}To use Supabase MCP, you need to get your access token:${NC}"
    echo ""
    print_step "1. Go to https://supabase.com/dashboard/account/tokens"
    print_step "2. Click 'Generate new token'"
    print_step "3. Give it a name like 'AI Language Learning Platform'"
    print_step "4. Copy the token (it starts with 'sbp_')"
    echo ""
    
    read -p "Enter your Supabase access token: " SUPABASE_ACCESS_TOKEN
    
    if [ -z "$SUPABASE_ACCESS_TOKEN" ]; then
        print_error "Access token is required"
        exit 1
    fi
    
    if [[ ! $SUPABASE_ACCESS_TOKEN =~ ^sbp_ ]]; then
        print_error "Invalid access token format. Should start with 'sbp_'"
        exit 1
    fi
    
    # Save token to environment file
    echo "SUPABASE_ACCESS_TOKEN=$SUPABASE_ACCESS_TOKEN" >> .env
    export SUPABASE_ACCESS_TOKEN="$SUPABASE_ACCESS_TOKEN"
    
    print_success "Access token saved to .env file"
}

# Function to create Supabase project
create_supabase_project() {
    print_header "Creating Supabase Project"
    
    print_step "This will create a new Supabase project for your AI Language Learning Platform"
    echo ""
    
    read -p "Enter project name (default: ai-language-learning): " PROJECT_NAME
    PROJECT_NAME=${PROJECT_NAME:-ai-language-learning}
    
    read -p "Enter database password (default: ai_lang_secure_pass): " DB_PASSWORD
    DB_PASSWORD=${DB_PASSWORD:-ai_lang_secure_pass}
    
    print_status "Creating project: $PROJECT_NAME"
    
    # Note: This would use the MCP once we have the token
    echo -e "${YELLOW}Note:${NC} Once you have your access token, we can create the project automatically"
    echo -e "${YELLOW}For now, please create the project manually:${NC}"
    echo ""
    print_step "1. Go to https://supabase.com/dashboard"
    print_step "2. Click 'New Project'"
    print_step "3. Choose your organization"
    print_step "4. Enter project name: $PROJECT_NAME"
    print_step "5. Enter database password: $DB_PASSWORD"
    print_step "6. Choose a region close to your users"
    print_step "7. Wait for the project to be created"
    echo ""
    
    read -p "Press Enter when your project is created..."
}

# Function to set up database schema
setup_database_schema() {
    print_header "Setting up Database Schema"
    
    print_step "You'll need to run the SQL commands in your Supabase SQL editor"
    echo ""
    
    # Create the SQL schema file
    cat > deployment/config/supabase-schema.sql << 'EOF'
-- AI Language Learning Platform Database Schema
-- Run this in your Supabase SQL editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) DEFAULT 'student' CHECK (role IN ('student', 'trainer', 'admin')),
    avatar_url TEXT,
    is_active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    language VARCHAR(50) NOT NULL,
    level VARCHAR(50) NOT NULL CHECK (level IN ('beginner', 'intermediate', 'advanced')),
    duration_hours INTEGER DEFAULT 0,
    price DECIMAL(10,2) DEFAULT 0.00,
    is_published BOOLEAN DEFAULT false,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Course requests table
CREATE TABLE IF NOT EXISTS course_requests (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    client_name VARCHAR(255) NOT NULL,
    client_email VARCHAR(255) NOT NULL,
    language VARCHAR(50) NOT NULL,
    level VARCHAR(50) NOT NULL CHECK (level IN ('beginner', 'intermediate', 'advanced')),
    requirements TEXT,
    budget_range VARCHAR(100),
    timeline VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    assigned_trainer_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Lessons table
CREATE TABLE IF NOT EXISTS lessons (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    order_index INTEGER NOT NULL,
    duration_minutes INTEGER DEFAULT 30,
    is_published BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User progress table
CREATE TABLE IF NOT EXISTS user_progress (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    lesson_id UUID REFERENCES lessons(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    completed BOOLEAN DEFAULT false,
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    time_spent_minutes INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, lesson_id)
);

-- AI chat sessions table
CREATE TABLE IF NOT EXISTS ai_chat_sessions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    course_id UUID REFERENCES courses(id) ON DELETE SET NULL,
    session_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI chat messages table
CREATE TABLE IF NOT EXISTS ai_chat_messages (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    session_id UUID REFERENCES ai_chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Assessments table
CREATE TABLE IF NOT EXISTS assessments (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    course_id UUID REFERENCES courses(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    passing_score INTEGER DEFAULT 70 CHECK (passing_score >= 0 AND passing_score <= 100),
    time_limit_minutes INTEGER DEFAULT 30,
    is_published BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Assessment questions table
CREATE TABLE IF NOT EXISTS assessment_questions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL CHECK (question_type IN ('multiple_choice', 'true_false', 'short_answer', 'essay')),
    correct_answer TEXT,
    options JSONB, -- For multiple choice questions
    points INTEGER DEFAULT 1,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User assessment results table
CREATE TABLE IF NOT EXISTS user_assessment_results (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
    score INTEGER NOT NULL CHECK (score >= 0),
    max_score INTEGER NOT NULL CHECK (max_score > 0),
    passed BOOLEAN NOT NULL,
    time_taken_minutes INTEGER,
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_courses_language ON courses(language);
CREATE INDEX IF NOT EXISTS idx_courses_level ON courses(level);
CREATE INDEX IF NOT EXISTS idx_courses_created_by ON courses(created_by);
CREATE INDEX IF NOT EXISTS idx_course_requests_status ON course_requests(status);
CREATE INDEX IF NOT EXISTS idx_course_requests_language ON course_requests(language);
CREATE INDEX IF NOT EXISTS idx_lessons_course_id ON lessons(course_id);
CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);
CREATE INDEX IF NOT EXISTS idx_user_progress_course_id ON user_progress(course_id);
CREATE INDEX IF NOT EXISTS idx_ai_chat_sessions_user_id ON ai_chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_chat_messages_session_id ON ai_chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_assessments_course_id ON assessments(course_id);
CREATE INDEX IF NOT EXISTS idx_assessment_questions_assessment_id ON assessment_questions(assessment_id);
CREATE INDEX IF NOT EXISTS idx_user_assessment_results_user_id ON user_assessment_results(user_id);

-- Add updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_courses_updated_at BEFORE UPDATE ON courses FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_course_requests_updated_at BEFORE UPDATE ON course_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_lessons_updated_at BEFORE UPDATE ON lessons FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_user_progress_updated_at BEFORE UPDATE ON user_progress FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_ai_chat_sessions_updated_at BEFORE UPDATE ON ai_chat_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_assessments_updated_at BEFORE UPDATE ON assessments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert sample data
INSERT INTO users (email, password_hash, full_name, role) VALUES
('admin@ailanguage.com', '$2b$12$example_hash', 'Admin User', 'admin'),
('trainer@ailanguage.com', '$2b$12$example_hash', 'Sample Trainer', 'trainer'),
('student@ailanguage.com', '$2b$12$example_hash', 'Sample Student', 'student')
ON CONFLICT (email) DO NOTHING;

-- Insert sample courses
INSERT INTO courses (title, description, language, level, duration_hours, price, is_published, created_by) VALUES
('Spanish for Beginners', 'Learn the basics of Spanish language', 'Spanish', 'beginner', 20, 99.99, true, (SELECT id FROM users WHERE email = 'trainer@ailanguage.com')),
('Advanced French Conversation', 'Master French conversation skills', 'French', 'advanced', 30, 149.99, true, (SELECT id FROM users WHERE email = 'trainer@ailanguage.com')),
('Business English', 'Professional English for the workplace', 'English', 'intermediate', 25, 129.99, false, (SELECT id FROM users WHERE email = 'trainer@ailanguage.com'))
ON CONFLICT DO NOTHING;
EOF
    
    print_success "Database schema created: deployment/config/supabase-schema.sql"
    print_step "Copy and paste this SQL into your Supabase SQL editor"
    echo ""
    
    read -p "Press Enter when you've run the SQL commands..."
}

# Function to configure Row Level Security (RLS)
setup_rls() {
    print_header "Setting up Row Level Security"
    
    cat > deployment/config/supabase-rls.sql << 'EOF'
-- Row Level Security (RLS) Policies
-- Run this after creating the tables

-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE course_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE lessons ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_progress ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessment_questions ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_assessment_results ENABLE ROW LEVEL SECURITY;

-- Users policies
CREATE POLICY "Users can view their own profile" ON users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON users
    FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Admins can view all users" ON users
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role = 'admin'
        )
    );

-- Courses policies
CREATE POLICY "Anyone can view published courses" ON courses
    FOR SELECT USING (is_published = true);

CREATE POLICY "Trainers can view their own courses" ON courses
    FOR SELECT USING (created_by = auth.uid());

CREATE POLICY "Trainers can create courses" ON courses
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role IN ('trainer', 'admin')
        )
    );

CREATE POLICY "Trainers can update their own courses" ON courses
    FOR UPDATE USING (created_by = auth.uid());

-- Course requests policies
CREATE POLICY "Users can view their own requests" ON course_requests
    FOR SELECT USING (client_email = (SELECT email FROM users WHERE id = auth.uid()));

CREATE POLICY "Anyone can create course requests" ON course_requests
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Admins and trainers can view all requests" ON course_requests
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE id = auth.uid() AND role IN ('trainer', 'admin')
        )
    );

-- Lessons policies
CREATE POLICY "Anyone can view lessons of published courses" ON lessons
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM courses 
            WHERE id = lessons.course_id AND is_published = true
        )
    );

CREATE POLICY "Trainers can manage lessons for their courses" ON lessons
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM courses 
            WHERE id = lessons.course_id AND created_by = auth.uid()
        )
    );

-- User progress policies
CREATE POLICY "Users can view their own progress" ON user_progress
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can update their own progress" ON user_progress
    FOR UPDATE USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own progress" ON user_progress
    FOR INSERT WITH CHECK (user_id = auth.uid());

-- AI chat sessions policies
CREATE POLICY "Users can view their own chat sessions" ON ai_chat_sessions
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can create their own chat sessions" ON ai_chat_sessions
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own chat sessions" ON ai_chat_sessions
    FOR UPDATE USING (user_id = auth.uid());

-- AI chat messages policies
CREATE POLICY "Users can view messages in their sessions" ON ai_chat_messages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM ai_chat_sessions 
            WHERE id = ai_chat_messages.session_id AND user_id = auth.uid()
        )
    );

CREATE POLICY "Users can insert messages in their sessions" ON ai_chat_messages
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM ai_chat_sessions 
            WHERE id = ai_chat_messages.session_id AND user_id = auth.uid()
        )
    );

-- Assessments policies
CREATE POLICY "Anyone can view published assessments" ON assessments
    FOR SELECT USING (is_published = true);

CREATE POLICY "Trainers can manage assessments for their courses" ON assessments
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM courses 
            WHERE id = assessments.course_id AND created_by = auth.uid()
        )
    );

-- Assessment questions policies
CREATE POLICY "Anyone can view questions of published assessments" ON assessment_questions
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM assessments 
            WHERE id = assessment_questions.assessment_id AND is_published = true
        )
    );

CREATE POLICY "Trainers can manage questions for their assessments" ON assessment_questions
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM assessments a
            JOIN courses c ON a.course_id = c.id
            WHERE a.id = assessment_questions.assessment_id AND c.created_by = auth.uid()
        )
    );

-- User assessment results policies
CREATE POLICY "Users can view their own results" ON user_assessment_results
    FOR SELECT USING (user_id = auth.uid());

CREATE POLICY "Users can insert their own results" ON user_assessment_results
    FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY "Trainers can view results for their courses" ON user_assessment_results
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM assessments a
            JOIN courses c ON a.course_id = c.id
            WHERE a.id = user_assessment_results.assessment_id AND c.created_by = auth.uid()
        )
    );
EOF
    
    print_success "RLS policies created: deployment/config/supabase-rls.sql"
    print_step "Run this SQL after the main schema to enable security"
    echo ""
    
    read -p "Press Enter when you've run the RLS commands..."
}

# Function to get project details
get_project_details() {
    print_header "Getting Project Details"
    
    print_step "You'll need these details for your environment variables:"
    echo ""
    
    read -p "Enter your Supabase project URL (https://xxx.supabase.co): " PROJECT_URL
    read -p "Enter your Supabase anon key: " ANON_KEY
    read -p "Enter your Supabase service role key: " SERVICE_ROLE_KEY
    
    # Save to environment file
    cat > deployment/config/supabase-env.txt << EOF
# Supabase Configuration
SUPABASE_URL=$PROJECT_URL
SUPABASE_ANON_KEY=$ANON_KEY
SUPABASE_SERVICE_ROLE_KEY=$SERVICE_ROLE_KEY
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
EOF
    
    print_success "Project details saved to: deployment/config/supabase-env.txt"
    print_step "Use these values in your environment variables"
}

# Main execution
main() {
    print_header "Supabase Database Setup"
    
    echo -e "${BLUE}This script will help you set up your Supabase database${NC}"
    echo -e "${BLUE}for the AI Language Learning Platform${NC}"
    echo ""
    
    # Get access token
    get_supabase_token
    
    # Create project
    create_supabase_project
    
    # Setup schema
    setup_database_schema
    
    # Setup RLS
    setup_rls
    
    # Get project details
    get_project_details
    
    print_header "Setup Complete!"
    echo -e "${GREEN}✅ Your Supabase database is ready!${NC}"
    echo ""
    echo -e "${BLUE}Next steps:${NC}"
    echo "1. Update your environment variables with the values from supabase-env.txt"
    echo "2. Test the database connection"
    echo "3. Run the deployment setup when ready: ./deployment/setup.sh"
    echo ""
    echo -e "${YELLOW}Your database includes:${NC}"
    echo "- User management (students, trainers, admins)"
    echo "- Course management with lessons"
    echo "- AI chat sessions and messages"
    echo "- Assessments and progress tracking"
    echo "- Row Level Security (RLS) for data protection"
    echo "- Sample data for testing"
}

# Run main function
main "$@" 