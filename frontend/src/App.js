import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import CreatorDashboard from './pages/CreatorDashboard';
import CreatorProfile from './pages/CreatorProfile';
import SubscriptionPage from './pages/SubscriptionPage';
import './App.css';

function PrivateRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" />;
}

function CreatorRoute({ children }) {
  const { user } = useAuth();
  return user && user.account_type === 'creator' ? children : <Navigate to="/" />;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Navbar />
          <main className="container mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route 
                path="/dashboard" 
                element={
                  <CreatorRoute>
                    <CreatorDashboard />
                  </CreatorRoute>
                } 
              />
              <Route path="/creator/:id" element={<CreatorProfile />} />
              <Route 
                path="/subscriptions" 
                element={
                  <PrivateRoute>
                    <SubscriptionPage />
                  </PrivateRoute>
                } 
              />
            </Routes>
          </main>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
