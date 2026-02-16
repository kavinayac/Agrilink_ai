import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Sprout, TrendingUp, ShoppingCart, CloudRain, Home } from 'lucide-react';
import './index.css';
import HomePage from './pages/HomePage';
import FarmerPortal from './pages/FarmerPortal';
import MarketDashboard from './pages/MarketDashboard';
import BuyerPortal from './pages/BuyerPortal';
import WeatherRisk from './pages/WeatherRisk';

function NavLink({ to, icon: Icon, children }) {
  const location = useLocation();
  const isActive = location.pathname === to;

  return (
    <Link
      to={to}
      className={`flex items-center space-x-2 px-4 py-2 rounded-xl font-medium transition-all duration-300 ${isActive
        ? 'bg-gradient-to-r from-primary-600 to-primary-700 text-white shadow-lg'
        : 'text-gray-700 hover:bg-gray-100 hover:scale-105'
        }`}
    >
      <Icon className="h-5 w-5" />
      <span className="hidden sm:inline">{children}</span>
    </Link>
  );
}

import { WebSocketProvider } from './context/WebSocketContext';

function App() {
  return (
    <WebSocketProvider>
      <Router>
        <div className="min-h-screen">
          {/* Navigation */}
          <nav className="bg-white/80 backdrop-blur-lg shadow-lg border-b border-gray-200 sticky top-0 z-50">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
              <div className="flex justify-between h-20">
                <div className="flex items-center">
                  <Link to="/" className="flex items-center space-x-3 group">
                    <div className="p-2 bg-gradient-to-br from-primary-100 to-green-100 rounded-xl group-hover:scale-110 transition-transform duration-300">
                      <Sprout className="h-8 w-8 text-primary-600" />
                    </div>
                    <span className="text-3xl font-bold gradient-text">AgriLink</span>
                  </Link>
                </div>

                <div className="flex items-center space-x-2">
                  <NavLink to="/" icon={Home}>Home</NavLink>
                  <NavLink to="/farmer" icon={Sprout}>Farmer</NavLink>
                  <NavLink to="/market" icon={TrendingUp}>Market</NavLink>
                  <NavLink to="/buyer" icon={ShoppingCart}>Buyer</NavLink>
                  <NavLink to="/weather" icon={CloudRain}>Weather</NavLink>
                </div>
              </div>
            </div>
          </nav>

          {/* Main Content */}
          <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/farmer" element={<FarmerPortal />} />
              <Route path="/market" element={<MarketDashboard />} />
              <Route path="/buyer" element={<BuyerPortal />} />
              <Route path="/weather" element={<WeatherRisk />} />
            </Routes>
          </main>

          {/* Footer */}
          <footer className="bg-gradient-to-r from-gray-900 to-gray-800 text-white mt-20">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
              <div className="text-center space-y-3">
                <p className="text-lg font-semibold">
                  🌾 AgriLink - Real-time Agricultural Intelligence Platform
                </p>
                <p className="text-gray-400">
                  Powered by Groq AI, HuggingFace, and LangChain
                </p>
                <div className="flex justify-center space-x-6 text-sm text-gray-400 pt-4">
                  <span>© 2024 AgriLink</span>
                  <span>•</span>
                  <span>Built with ❤️ for Farmers</span>
                </div>
              </div>
            </div>
          </footer>
        </div>
      </Router>
    </WebSocketProvider>
  );
}

export default App;
