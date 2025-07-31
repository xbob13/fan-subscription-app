import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';

const HomePage = () => {
  const [featuredCreators, setFeaturedCreators] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [featuredResponse, categoriesResponse] = await Promise.all([
        axios.get('/creators/featured/'),
        axios.get('/creators/categories/')
      ]);
      
      setFeaturedCreators(featuredResponse.data);
      setCategories(categoriesResponse.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-64">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <section className="text-center py-12 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg">
        <h1 className="text-4xl font-bold mb-4">
          Support Your Favorite Creators
        </h1>
        <p className="text-xl mb-8 max-w-2xl mx-auto">
          Subscribe to exclusive content, send tips, and connect directly with creators you love.
        </p>
        <div className="space-x-4">
          <Link to="/register" className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100">
            Start Exploring
          </Link>
          <Link to="/register" className="border-2 border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600">
            Become a Creator
          </Link>
        </div>
      </section>

      {/* Categories */}
      <section>
        <h2 className="text-2xl font-bold mb-6">Browse Categories</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
          {categories.map((category) => (
            <Link
              key={category.key}
              to={`/?category=${category.key}`}
              className="bg-white rounded-lg p-4 text-center shadow-md hover:shadow-lg transition-shadow"
            >
              <div className="text-2xl mb-2">
                {getCategoryIcon(category.key)}
              </div>
              <div className="text-sm font-medium text-gray-700">
                {category.label}
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Featured Creators */}
      <section>
        <h2 className="text-2xl font-bold mb-6">Featured Creators</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {featuredCreators.map((creator) => (
            <div key={creator.id} className="creator-card">
              {creator.cover_image && (
                <img
                  src={creator.cover_image}
                  alt={creator.display_name}
                  className="w-full h-48 object-cover"
                />
              )}
              <div className="p-6">
                <div className="flex items-center mb-4">
                  {creator.user.profile_picture ? (
                    <img
                      src={creator.user.profile_picture}
                      alt={creator.display_name}
                      className="w-12 h-12 rounded-full mr-4"
                    />
                  ) : (
                    <div className="w-12 h-12 bg-gray-300 rounded-full mr-4 flex items-center justify-center">
                      <span className="text-lg font-medium text-gray-700">
                        {creator.display_name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  )}
                  <div>
                    <h3 className="text-lg font-semibold">{creator.display_name}</h3>
                    <p className="text-sm text-gray-600">@{creator.user.username}</p>
                  </div>
                </div>
                
                <p className="text-gray-600 mb-4 line-clamp-3">
                  {creator.description}
                </p>
                
                <div className="flex justify-between items-center">
                  <div className="text-sm text-gray-500">
                    {creator.subscriber_count} subscribers
                  </div>
                  <div className="text-lg font-bold text-blue-600">
                    ${creator.subscription_price}/month
                  </div>
                </div>
                
                <Link
                  to={`/creator/${creator.id}`}
                  className="btn-primary w-full mt-4 text-center block"
                >
                  View Profile
                </Link>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Stats Section */}
      <section className="bg-gray-100 rounded-lg p-8 text-center">
        <h2 className="text-2xl font-bold mb-6">Join Our Community</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="text-3xl font-bold text-blue-600 mb-2">10,000+</div>
            <div className="text-gray-600">Active Creators</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-blue-600 mb-2">100,000+</div>
            <div className="text-gray-600">Subscribers</div>
          </div>
          <div>
            <div className="text-3xl font-bold text-blue-600 mb-2">$1M+</div>
            <div className="text-gray-600">Paid to Creators</div>
          </div>
        </div>
      </section>
    </div>
  );
};

const getCategoryIcon = (category) => {
  const icons = {
    fitness: '💪',
    cooking: '🍳',
    art: '🎨',
    music: '🎵',
    lifestyle: '✨',
    education: '📚',
    adult: '🔞'
  };
  return icons[category] || '📁';
};

export default HomePage;