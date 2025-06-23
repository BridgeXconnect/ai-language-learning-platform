import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import TrainerDashboard from '../../components/trainer/TrainerDashboard';

const TrainerPortal = () => {
  return (
    <Routes>
      <Route index element={<TrainerDashboard />} />
      <Route path="dashboard" element={<TrainerDashboard />} />
      <Route path="*" element={<Navigate to="/trainer" replace />} />
    </Routes>
  );
};

export default TrainerPortal;