import React from 'react';
import { Routes, Route } from 'react-router-dom';
import SOPUploadPage from './SOPUploadPage';

const SalesPortal = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      <Routes>
        <Route index element={<SOPUploadPage />} />
        <Route path="upload" element={<SOPUploadPage />} />
      </Routes>
    </div>
  );
};

export default SalesPortal;