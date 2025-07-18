# 🔧 Troubleshooting Supabase SQL Editor

## Common Issues and Solutions

### **Issue 1: "Cannot run multiple statements"**
**Problem**: Supabase SQL editor sometimes has issues with large scripts.

**Solution**: Run the schema in smaller chunks:

#### **Step 1: Enable Extensions**
```sql
-- Run this first
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

#### **Step 2: Create Tables (Part 1)**
```sql
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
```

#### **Step 3: Create Tables (Part 2)**
```sql
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
```

#### **Step 4: Create Tables (Part 3)**
```sql
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
```

#### **Step 5: Create Tables (Part 4)**
```sql
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
```

#### **Step 6: Create Tables (Part 5)**
```sql
-- Assessment questions table
CREATE TABLE IF NOT EXISTS assessment_questions (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL CHECK (question_type IN ('multiple_choice', 'true_false', 'short_answer', 'essay')),
    correct_answer TEXT,
    options JSONB,
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
```

### **Issue 2: "Permission denied"**
**Problem**: You might not have the right permissions.

**Solution**: 
1. Make sure you're logged into the correct Supabase account
2. Check that you're in the right project (`ai_lang_platform`)
3. Try refreshing the page

### **Issue 3: "Connection timeout"**
**Problem**: The SQL editor might be timing out.

**Solution**:
1. Refresh the SQL editor page
2. Try running smaller chunks of SQL
3. Wait a few minutes and try again

### **Issue 4: "Syntax error"**
**Problem**: There might be a syntax issue in the SQL.

**Solution**: 
1. Copy and paste exactly as shown above
2. Run each statement individually
3. Check for any extra characters or spaces

## 🚀 **Alternative Method: Use the Table Editor**

If SQL editor continues to fail, you can create tables manually:

### **Step 1: Go to Table Editor**
1. In your Supabase dashboard
2. Click "Table Editor" in the left sidebar
3. Click "Create a new table"

### **Step 2: Create Tables One by One**

#### **Users Table**
- Name: `users`
- Columns:
  - `id` (uuid, primary key, default: `uuid_generate_v4()`)
  - `email` (varchar, unique, not null)
  - `password_hash` (varchar, not null)
  - `full_name` (varchar)
  - `role` (varchar, default: 'student')
  - `avatar_url` (text)
  - `is_active` (boolean, default: true)
  - `email_verified` (boolean, default: false)
  - `created_at` (timestamptz, default: now())
  - `updated_at` (timestamptz, default: now())

#### **Courses Table**
- Name: `courses`
- Columns:
  - `id` (uuid, primary key, default: `uuid_generate_v4()`)
  - `title` (varchar, not null)
  - `description` (text)
  - `language` (varchar, not null)
  - `level` (varchar, not null)
  - `duration_hours` (integer, default: 0)
  - `price` (decimal, default: 0.00)
  - `is_published` (boolean, default: false)
  - `created_by` (uuid, foreign key to users.id)
  - `created_at` (timestamptz, default: now())
  - `updated_at` (timestamptz, default: now())

## 🔍 **Check Your Progress**

After creating tables, you can verify they exist:

```sql
-- Check if tables were created
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

## 📞 **Still Having Issues?**

1. **Screenshot the error** and share it
2. **Try a different browser**
3. **Clear browser cache**
4. **Contact Supabase support**: https://supabase.com/support

## 🎯 **Quick Test**

Try this simple test first:

```sql
-- Test if SQL editor works
SELECT 'Hello World' as test;
```

If this works, then the issue is with the schema. If it doesn't work, there's a broader issue with your Supabase setup. 