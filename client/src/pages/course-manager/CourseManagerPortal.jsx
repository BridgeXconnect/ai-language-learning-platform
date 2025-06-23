import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import CourseManagerDashboard from '../../components/course-manager/CourseManagerDashboard';
import VisualCourseBuilder from '../../components/ai/VisualCourseBuilder';

const CourseManagerPortal = () => {
  return (
    <Routes>
      <Route index element={<CourseManagerDashboard />} />
      <Route path="dashboard" element={<CourseManagerDashboard />} />
      <Route path="course-builder/:courseId" element={<VisualCourseBuilder />} />
      <Route path="*" element={<Navigate to="/course-manager" replace />} />
    </Routes>
  );
};

export default CourseManagerPortal;