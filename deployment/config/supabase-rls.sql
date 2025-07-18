-- Row Level Security (RLS) Policies
-- Project: ai_lang_platform
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