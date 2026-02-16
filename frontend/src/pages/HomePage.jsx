import { Link } from 'react-router-dom';
import { Sprout, TrendingUp, ShoppingCart, CloudRain, Sparkles, Shield, Zap, ArrowRight } from 'lucide-react';

export default function HomePage() {
    return (
        <div className="space-y-16 animate-fade-in">
            {/* Hero Section */}
            <div className="text-center space-y-8 py-12">
                <div className="flex justify-center animate-pulse-slow">
                    <div className="p-6 bg-gradient-to-br from-primary-100 to-green-100 rounded-full">
                        <Sprout className="h-24 w-24 text-primary-600" />
                    </div>
                </div>
                <h1 className="text-6xl font-bold text-gray-900 animate-slide-up">
                    Welcome to <span className="gradient-text">AgriLink</span>
                </h1>
                <p className="text-2xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
                    Real-time agricultural intelligence platform powered by AI. Get expert advice, market insights, and risk assessments for your farming needs.
                </p>
                <div className="flex justify-center gap-4 pt-4">
                    <Link to="/farmer" className="btn-primary flex items-center gap-2">
                        Get Started <ArrowRight className="h-5 w-5" />
                    </Link>
                    <a href="#features" className="btn-secondary">
                        Learn More
                    </a>
                </div>
            </div>

            {/* Features Grid */}
            <div id="features" className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                <Link to="/farmer" className="card group cursor-pointer">
                    <div className="flex flex-col items-center text-center space-y-4">
                        <div className="p-5 bg-gradient-to-br from-primary-100 to-primary-200 rounded-2xl group-hover:scale-110 transition-transform duration-300">
                            <Sprout className="h-10 w-10 text-primary-600" />
                        </div>
                        <h3 className="text-2xl font-bold text-gray-900">Farmer Advisory</h3>
                        <p className="text-gray-600 leading-relaxed">
                            Get personalized farming advice powered by RAG-grounded AI
                        </p>
                        <div className="text-primary-600 font-semibold flex items-center gap-2 group-hover:gap-3 transition-all">
                            Explore <ArrowRight className="h-4 w-4" />
                        </div>
                    </div>
                </Link>

                <Link to="/market" className="card group cursor-pointer">
                    <div className="flex flex-col items-center text-center space-y-4">
                        <div className="p-5 bg-gradient-to-br from-blue-100 to-blue-200 rounded-2xl group-hover:scale-110 transition-transform duration-300">
                            <TrendingUp className="h-10 w-10 text-blue-600" />
                        </div>
                        <h3 className="text-2xl font-bold text-gray-900">Market Intelligence</h3>
                        <p className="text-gray-600 leading-relaxed">
                            Analyze prices, trends, and get buy/sell recommendations
                        </p>
                        <div className="text-blue-600 font-semibold flex items-center gap-2 group-hover:gap-3 transition-all">
                            Explore <ArrowRight className="h-4 w-4" />
                        </div>
                    </div>
                </Link>

                <Link to="/buyer" className="card group cursor-pointer">
                    <div className="flex flex-col items-center text-center space-y-4">
                        <div className="p-5 bg-gradient-to-br from-amber-100 to-amber-200 rounded-2xl group-hover:scale-110 transition-transform duration-300">
                            <ShoppingCart className="h-10 w-10 text-amber-600" />
                        </div>
                        <h3 className="text-2xl font-bold text-gray-900">Buyer Strategy</h3>
                        <p className="text-gray-600 leading-relaxed">
                            Fair pricing, negotiation tips, and market valuations
                        </p>
                        <div className="text-amber-600 font-semibold flex items-center gap-2 group-hover:gap-3 transition-all">
                            Explore <ArrowRight className="h-4 w-4" />
                        </div>
                    </div>
                </Link>

                <Link to="/weather" className="card group cursor-pointer">
                    <div className="flex flex-col items-center text-center space-y-4">
                        <div className="p-5 bg-gradient-to-br from-sky-100 to-sky-200 rounded-2xl group-hover:scale-110 transition-transform duration-300">
                            <CloudRain className="h-10 w-10 text-sky-600" />
                        </div>
                        <h3 className="text-2xl font-bold text-gray-900">Weather Risk</h3>
                        <p className="text-gray-600 leading-relaxed">
                            Assess crop risks and get mitigation strategies
                        </p>
                        <div className="text-sky-600 font-semibold flex items-center gap-2 group-hover:gap-3 transition-all">
                            Explore <ArrowRight className="h-4 w-4" />
                        </div>
                    </div>
                </Link>
            </div>

            {/* Key Features */}
            <div className="card bg-gradient-to-br from-primary-50 via-white to-green-50 border-primary-200">
                <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Why Choose AgriLink?</h2>
                <div className="grid md:grid-cols-3 gap-8">
                    <div className="flex items-start space-x-4">
                        <div className="p-3 bg-primary-100 rounded-xl">
                            <Sparkles className="h-7 w-7 text-primary-600" />
                        </div>
                        <div>
                            <h4 className="font-bold text-lg text-gray-900 mb-2">AI-Powered Insights</h4>
                            <p className="text-gray-600 leading-relaxed">
                                Groq LLM with RAG grounding ensures accurate, cited recommendations
                            </p>
                        </div>
                    </div>

                    <div className="flex items-start space-x-4">
                        <div className="p-3 bg-primary-100 rounded-xl">
                            <Shield className="h-7 w-7 text-primary-600" />
                        </div>
                        <div>
                            <h4 className="font-bold text-lg text-gray-900 mb-2">Trusted Knowledge</h4>
                            <p className="text-gray-600 leading-relaxed">
                                All advice backed by agricultural knowledge base with citations
                            </p>
                        </div>
                    </div>

                    <div className="flex items-start space-x-4">
                        <div className="p-3 bg-primary-100 rounded-xl">
                            <Zap className="h-7 w-7 text-primary-600" />
                        </div>
                        <div>
                            <h4 className="font-bold text-lg text-gray-900 mb-2">Real-Time Processing</h4>
                            <p className="text-gray-600 leading-relaxed">
                                Event-driven architecture with multi-agent coordination
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="card text-center bg-gradient-to-br from-primary-50 to-white">
                    <div className="text-5xl font-bold gradient-text mb-2">6</div>
                    <div className="text-gray-600 font-medium">AI Agents</div>
                </div>
                <div className="card text-center bg-gradient-to-br from-blue-50 to-white">
                    <div className="text-5xl font-bold bg-gradient-to-r from-blue-600 to-blue-700 bg-clip-text text-transparent mb-2">3</div>
                    <div className="text-gray-600 font-medium">Knowledge Bases</div>
                </div>
                <div className="card text-center bg-gradient-to-br from-green-50 to-white">
                    <div className="text-5xl font-bold gradient-text mb-2">100%</div>
                    <div className="text-gray-600 font-medium">RAG Grounded</div>
                </div>
                <div className="card text-center bg-gradient-to-br from-amber-50 to-white">
                    <div className="text-5xl font-bold bg-gradient-to-r from-amber-600 to-amber-700 bg-clip-text text-transparent mb-2">24/7</div>
                    <div className="text-gray-600 font-medium">Available</div>
                </div>
            </div>
        </div>
    );
}
