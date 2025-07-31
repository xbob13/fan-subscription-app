import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

// Configure axios defaults
axios.defaults.baseURL = 'http://localhost:8000/api';
axios.defaults.headers.common['Content-Type'] = 'application/json';

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Token ${token}`;
      // Fetch user profile
      fetchProfile();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchProfile = async () => {
    try {
      const response = await axios.get('/auth/profile/');
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post('/auth/register/', userData);
      const { user, token } = response.data;
      
      setUser(user);
      setToken(token);
      localStorage.setItem('token', token);
      axios.defaults.headers.common['Authorization'] = `Token ${token}`;
      
      return { success: true, user };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Registration failed' 
      };
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post('/auth/login/', { email, password });
      const { user, token } = response.data;
      
      setUser(user);
      setToken(token);
      localStorage.setItem('token', token);
      axios.defaults.headers.common['Authorization'] = `Token ${token}`;
      
      return { success: true, user };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Login failed' 
      };
    }
  };

  const logout = async () => {
    try {
      await axios.post('/auth/logout/');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setToken(null);
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await axios.patch('/auth/profile/', profileData);
      setUser(response.data);
      return { success: true, user: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data || 'Profile update failed' 
      };
    }
  };

  const verifyAge = async (dateOfBirth) => {
    try {
      const response = await axios.post('/auth/verify-age/', {
        date_of_birth: dateOfBirth
      });
      
      // Refresh user data
      await fetchProfile();
      
      return { success: true, message: response.data.message };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Age verification failed' 
      };
    }
  };

  const value = {
    user,
    token,
    loading,
    register,
    login,
    logout,
    updateProfile,
    verifyAge,
    isAuthenticated: !!user,
    isCreator: user?.account_type === 'creator',
    isSubscriber: user?.account_type === 'subscriber'
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};