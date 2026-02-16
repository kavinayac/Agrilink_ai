import { useState, useEffect } from 'react';
import { TrendingUp, Loader2, BarChart3, AlertCircle, DollarSign, Calendar, Package, Radio } from 'lucide-react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { CircularProgressbar, buildStyles } from 'react-circular-progressbar';
import 'react-circular-progressbar/dist/styles.css';
import api from '../services/api';
import { useWebSocket } from '../context/WebSocketContext';

// Mock initial data
const initialPriceData = [
    { month: 'Jan', price: 2100, msp: 2125 },
    { month: 'Feb', price: 2150, msp: 2125 },
    { month: 'Mar', price: 2200, msp: 2125 },
    { month: 'Apr', price: 2180, msp: 2125 },
    { month: 'May', price: 2250, msp: 2125 },
    { month: 'Jun', price: 2300, msp: 2125 },
];

const marketShare = [
    { name: 'Punjab', value: 35, color: '#22c55e' },
    { name: 'Haryana', value: 25, color: '#3b82f6' },
    { name: 'UP', value: 20, color: '#f59e0b' },
    { name: 'Others', value: 20, color: '#8b5cf6' },
];

export default function MarketDashboard() {
    const [crop, setCrop] = useState('wheat');
    const [region, setRegion] = useState('punjab');
    const [action, setAction] = useState('analyze');
    const [loading, setLoading] = useState(false);
    const [insights, setInsights] = useState(null);
    const [error, setError] = useState(null);

    // Real-time state
    const { lastMessage, isConnected } = useWebSocket();
    const [currentPrice, setCurrentPrice] = useState(2300);
    const [priceData, setPriceData] = useState(initialPriceData);
    const [priceChange, setPriceChange] = useState(8.2);

    useEffect(() => {
        if (lastMessage && lastMessage.event_type === 'price_update') {
            const newPrice = lastMessage.price;
            setCurrentPrice(newPrice);

            // Simulate dynamic price change percentage
            const change = ((newPrice - 2125) / 2125) * 100;
            setPriceChange(change.toFixed(1));

            // Update chart data with new point
            setPriceData(prev => {
                const newData = [...prev];
                // Update last month or add new one (simplified for demo)
                newData[newData.length - 1].price = newPrice;
                return newData;
            });
        }
    }, [lastMessage]);

    const handleGetInsights = async () => {
        setLoading(true);
        setError(null);
        setInsights(null);

        try {
            const result = await api.getMarketInsights(crop, region, 'market_' + Date.now(), action);
            setInsights(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Header with Live Stats */}
            <div className="text-center space-y-6">
                <div className="flex justify-center">
                    <div className="relative">
                        <div className="absolute inset-0 bg-gradient-to-r from-blue-400 to-purple-500 rounded-full blur-xl opacity-50 animate-pulse"></div>
                        <div className="relative p-6 bg-gradient-to-br from-blue-500 to-purple-600 rounded-3xl">
                            <TrendingUp className="h-16 w-16 text-white" />
                        </div>
                        {isConnected && (
                            <div className="absolute top-0 right-0 h-4 w-4 bg-green-500 rounded-full border-2 border-white" title="Connected to Real-time Feed"></div>
                        )}
                    </div>
                </div>
                <h1 className="text-6xl font-black bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent animate-slide-up">
                    Market Intelligence
                </h1>
                <p className="text-2xl text-gray-600 font-medium">
                    Real-time market analysis powered by AI
                </p>
            </div>

            {/* Live Market Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="card bg-gradient-to-br from-green-500 to-emerald-600 text-white">
                    <div className="flex items-center justify-between mb-4">
                        <DollarSign className="h-10 w-10" />
                        <div className="text-right">
                            <div className="text-3xl font-black animate-pulse">₹{currentPrice.toLocaleString()}</div>
                            <div className="text-sm opacity-90">Current Price</div>
                        </div>
                    </div>
                    <div className="flex items-center space-x-2 text-sm">
                        <TrendingUp className="h-4 w-4" />
                        <span>+{priceChange}% above MSP</span>
                    </div>
                </div>

                <div className="card bg-gradient-to-br from-blue-500 to-cyan-600 text-white">
                    <div className="flex items-center justify-between mb-4">
                        <BarChart3 className="h-10 w-10" />
                        <div className="text-right">
                            <div className="text-3xl font-black">₹2,125</div>
                            <div className="text-sm opacity-90">MSP 2024</div>
                        </div>
                    </div>
                    <div className="text-sm opacity-90">Minimum Support Price</div>
                </div>

                <div className="card bg-gradient-to-br from-purple-500 to-pink-600 text-white">
                    <div className="flex items-center justify-between mb-4">
                        <Package className="h-10 w-10" />
                        <div className="text-right">
                            <div className="text-3xl font-black">12.5K</div>
                            <div className="text-sm opacity-90">Tonnes Traded</div>
                        </div>
                    </div>
                    <div className="text-sm opacity-90">Last 7 days</div>
                </div>

                <div className="card bg-gradient-to-br from-orange-500 to-red-600 text-white">
                    <div className="flex items-center justify-between mb-4">
                        <Radio className={`h-10 w-10 ${isConnected ? 'animate-pulse' : ''}`} />
                        <div className="text-right">
                            <div className="text-3xl font-black">{isConnected ? 'LIVE' : 'OFFLINE'}</div>
                            <div className="text-sm opacity-90">Data Feed</div>
                        </div>
                    </div>
                    <div className="text-sm opacity-90">{isConnected ? 'Real-time updates active' : 'Connecting...'}</div>
                </div>
            </div>

            {/* Interactive Charts */}
            <div className="grid md:grid-cols-2 gap-6">
                {/* Price Trend Chart */}
                <div className="card">
                    <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                        <div className="p-2 bg-gradient-to-br from-blue-100 to-blue-200 rounded-lg mr-3">
                            <TrendingUp className="h-5 w-5 text-blue-600" />
                        </div>
                        Price Trend (6 Months)
                    </h3>
                    <ResponsiveContainer width="100%" height={250}>
                        <AreaChart data={priceData}>
                            <defs>
                                <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                            <XAxis dataKey="month" stroke="#6b7280" />
                            <YAxis stroke="#6b7280" />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: '#fff',
                                    border: '2px solid #3b82f6',
                                    borderRadius: '12px',
                                    boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
                                }}
                            />
                            <Area type="monotone" dataKey="price" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorPrice)" />
                            <Line type="monotone" dataKey="msp" stroke="#22c55e" strokeWidth={2} strokeDasharray="5 5" />
                        </AreaChart>
                    </ResponsiveContainer>
                    <div className="flex justify-center space-x-6 mt-4 text-sm">
                        <div className="flex items-center">
                            <div className="w-4 h-4 bg-blue-500 rounded mr-2"></div>
                            <span>Market Price</span>
                        </div>
                        <div className="flex items-center">
                            <div className="w-4 h-1 bg-green-500 rounded mr-2"></div>
                            <span>MSP</span>
                        </div>
                    </div>
                </div>

                {/* Regional Market Share */}
                <div className="card">
                    <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                        <div className="p-2 bg-gradient-to-br from-purple-100 to-purple-200 rounded-lg mr-3">
                            <BarChart3 className="h-5 w-5 text-purple-600" />
                        </div>
                        Regional Market Share
                    </h3>
                    <div className="flex items-center justify-center">
                        <div style={{ width: 200, height: 200 }}>
                            <ResponsiveContainer>
                                <PieChart>
                                    <Pie
                                        data={marketShare}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {marketShare.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3 mt-4">
                        {marketShare.map((item, idx) => (
                            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl">
                                <div className="flex items-center">
                                    <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: item.color }}></div>
                                    <span className="text-sm font-medium">{item.name}</span>
                                </div>
                                <span className="text-sm font-bold">{item.value}%</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* AI Analysis Section */}
            <div className="card bg-gradient-to-br from-indigo-50 via-white to-purple-50">
                <div className="flex items-center mb-6">
                    <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl mr-4">
                        <BarChart3 className="h-8 w-8 text-white" />
                    </div>
                    <div>
                        <h2 className="text-2xl font-black text-gray-900">AI Market Analysis</h2>
                        <p className="text-gray-600">Get personalized insights powered by Groq AI</p>
                    </div>
                </div>

                <div className="grid md:grid-cols-3 gap-4 mb-6">
                    <div className="space-y-2">
                        <label className="block text-sm font-bold text-gray-700">🌾 Crop</label>
                        <select value={crop} onChange={(e) => setCrop(e.target.value)} className="input">
                            <option value="wheat">Wheat</option>
                            <option value="rice">Rice</option>
                            <option value="cotton">Cotton</option>
                            <option value="sugarcane">Sugarcane</option>
                        </select>
                    </div>

                    <div className="space-y-2">
                        <label className="block text-sm font-bold text-gray-700">📍 Region</label>
                        <select value={region} onChange={(e) => setRegion(e.target.value)} className="input">
                            <option value="punjab">Punjab</option>
                            <option value="haryana">Haryana</option>
                            <option value="up">Uttar Pradesh</option>
                            <option value="maharashtra">Maharashtra</option>
                        </select>
                    </div>

                    <div className="space-y-2">
                        <label className="block text-sm font-bold text-gray-700">🎯 Action</label>
                        <select value={action} onChange={(e) => setAction(e.target.value)} className="input">
                            <option value="analyze">📊 Analyze</option>
                            <option value="buy">📉 Buy Signal</option>
                            <option value="sell">📈 Sell Signal</option>
                        </select>
                    </div>
                </div>

                <button
                    onClick={handleGetInsights}
                    disabled={loading}
                    className="btn-primary w-full text-lg py-4 relative overflow-hidden group"
                >
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-pink-600 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                    <div className="relative flex items-center justify-center space-x-3">
                        {loading ? (
                            <>
                                <Loader2 className="h-6 w-6 animate-spin" />
                                <span>Analyzing Market Data...</span>
                            </>
                        ) : (
                            <>
                                <BarChart3 className="h-6 w-6" />
                                <span>Get AI Insights</span>
                            </>
                        )}
                    </div>
                </button>
            </div>

            {/* AI Response with Visual Elements */}
            {insights && !loading && (
                <div className="card bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 border-2 border-blue-300 animate-slide-up">
                    <div className="flex items-start space-x-6 mb-6">
                        <div className="w-24 h-24">
                            <CircularProgressbar
                                value={insights.confidence * 100}
                                text={`${(insights.confidence * 100).toFixed(0)}%`}
                                styles={buildStyles({
                                    textSize: '24px',
                                    pathColor: `rgba(59, 130, 246, ${insights.confidence})`,
                                    textColor: '#1f2937',
                                    trailColor: '#e5e7eb',
                                    pathTransitionDuration: 1.5,
                                })}
                            />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-3xl font-black text-gray-900 mb-3">Market Intelligence Report</h3>
                            <div className="flex flex-wrap gap-2">
                                <span className="px-4 py-2 bg-white rounded-full border-2 border-blue-300 font-bold text-blue-700">
                                    🌾 {insights.crop}
                                </span>
                                <span className="px-4 py-2 bg-white rounded-full border-2 border-purple-300 font-bold text-purple-700">
                                    📍 {insights.region}
                                </span>
                                <span className="px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-full font-bold">
                                    ✨ High Confidence
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-2xl p-8 shadow-xl border-2 border-blue-200">
                        <p className="text-lg text-gray-800 leading-relaxed whitespace-pre-wrap">{insights.insights}</p>
                    </div>

                    {insights.sources && insights.sources.length > 0 && (
                        <div className="mt-6 pt-6 border-t-2 border-blue-200">
                            <h4 className="text-xl font-black text-gray-900 mb-4 flex items-center">
                                <div className="p-2 bg-blue-100 rounded-lg mr-2">
                                    📚
                                </div>
                                Knowledge Sources
                            </h4>
                            <div className="grid gap-3">
                                {insights.sources.map((source, idx) => (
                                    <div key={idx} className="bg-white rounded-xl p-4 border-2 border-blue-200 hover:border-blue-400 hover:shadow-lg transition-all">
                                        <div className="flex items-center justify-between">
                                            <span className="font-bold text-gray-900">{source.source}</span>
                                            <div className="px-4 py-1 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-full text-sm font-black">
                                                {(source.score * 100).toFixed(0)}% Match
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {error && (
                <div className="card bg-gradient-to-br from-red-100 to-pink-100 border-2 border-red-400">
                    <div className="flex items-center space-x-4">
                        <div className="p-4 bg-red-500 rounded-2xl">
                            <AlertCircle className="h-8 w-8 text-white" />
                        </div>
                        <div>
                            <h3 className="text-2xl font-black text-red-900 mb-2">Connection Error</h3>
                            <p className="text-red-700 text-lg">{error}</p>
                            <p className="text-red-600 mt-2">💡 Make sure backend server is running on port 8001</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
