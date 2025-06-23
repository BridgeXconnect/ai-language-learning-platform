import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import EnhancedStudentDashboard from '../../components/student/EnhancedStudentDashboard';
import InteractiveLessonPlayer from '../../components/student/InteractiveLessonPlayer';

const StudentPortal = () => {
  return (
    <Routes>
      <Route index element={<EnhancedStudentDashboard />} />
      <Route path="dashboard" element={<EnhancedStudentDashboard />} />
      <Route path="lesson/:lessonId" element={<InteractiveLessonPlayer />} />
      <Route path="*" element={<Navigate to="/student" replace />} />
    </Routes>
  );
};

export default StudentPortal;