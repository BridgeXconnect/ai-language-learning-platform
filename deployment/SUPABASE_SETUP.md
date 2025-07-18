# 🔧 Supabase Setup Guide

## 🎯 What We'll Set Up

- ✅ **Supabase Project** - Your database and backend
- ✅ **Database Schema** - All tables for your AI Language Learning Platform
- ✅ **Row Level Security** - Data protection and access control
- ✅ **Sample Data** - Test data to get started
- ✅ **Environment Variables** - Ready for deployment

## 🚀 Quick Start

### **Step 1: Get Your Supabase Access Token**

1. Go to [https://supabase.com/dashboard/account/tokens](https://supabase.com/dashboard/account/tokens)
2. Click **"Generate new token"**
3. Give it a name: `AI Language Learning Platform`
4. Copy the token (starts with `sbp_`)

### **Step 2: Run the Setup Script**

```bash
./deployment/supabase-setup.sh
```

The script will:
- Guide you through creating your project
- Set up the complete database schema
- Configure security policies
- Save your environment variables

## 📊 Database Schema

Your database will include:

### **Core Tables**
- **Users** - Students, trainers, and admins
- **Courses** - Language courses with metadata
- **Lessons** - Individual lessons within courses
- **Course Requests** - Client requests for custom courses

### **Learning Features**
- **User Progress** - Track learning progress
- **AI Chat Sessions** - Store AI conversation history
- **AI Chat Messages** - Individual messages in conversations
- **Assessments** - Quizzes and tests
- **Assessment Questions** - Questions within assessments
- **User Assessment Results** - Student test results

### **Security Features**
- **Row Level Security (RLS)** - Data protection
- **Role-based access** - Different permissions for different user types
- **Encrypted connections** - Secure data transmission

## 🔐 Security Policies

The setup includes comprehensive security:

### **User Access**
- Users can only see their own data
- Trainers can manage their own courses
- Admins have full access

### **Data Protection**
- Email addresses are protected
- Progress data is private
- Chat sessions are user-specific

## 📝 Sample Data

The setup includes sample data for testing:

### **Users**
- Admin user: `admin@ailanguage.com`
- Trainer: `trainer@ailanguage.com`
- Student: `student@ailanguage.com`

### **Courses**
- Spanish for Beginners
- Advanced French Conversation
- Business English

## 🔧 Environment Variables

After setup, you'll get these variables:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
DATABASE_URL=postgresql://postgres:password@db.project.supabase.co:5432/postgres
```

## 🎯 Next Steps After Setup

1. **Test the connection** - Verify everything works
2. **Update environment files** - Add the variables to your config
3. **Run health checks** - Ensure database is accessible
4. **Deploy when ready** - Use `./deployment/setup.sh`

## 🆘 Troubleshooting

### **Access Token Issues**
- Make sure the token starts with `sbp_`
- Check that you have the correct permissions
- Try generating a new token if needed

### **Database Connection Issues**
- Verify your project URL is correct
- Check that your database password is set
- Ensure your IP is not blocked

### **Schema Issues**
- Run the SQL commands in order
- Check for any syntax errors
- Verify all tables were created

## 📞 Support

- **Supabase Docs**: https://supabase.com/docs
- **Supabase Support**: https://supabase.com/support
- **Community**: https://github.com/supabase/supabase/discussions

---

**🎉 Once you run the setup script, your database will be ready for deployment!** 