import { useState } from 'react';
import { Send, Loader2, CheckCircle2, AlertCircle, BookOpen, Sparkles } from 'lucide-react';
import api from '../services/api';

export default function FarmerPortal() {
    const [query, setQuery] = useState('');
    const [crop, setCrop] = useState('wheat');
    const [region, setRegion] = useState('punjab');
    const [season, setSeason] = useState('rabi');
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState(null);
    const [error, setError] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResponse(null);

        try {
            const result = await api.farmerQuery(query, 'farmer_' + Date.now(), crop, region, season);
            setResponse(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const exampleQuestions = [
        "When should I plant wheat in Punjab?",
        "What is the irrigation schedule for rice?",
        "How do I control pests in wheat crops?",
        "What fertilizers should I use for rice?",
    ];

    return (
        <div className="space-y-8 animate-fade-in">
            {/* Header */}
            <div className="text-center space-y-4">
                <div className="flex justify-center">
                    <div className="p-4 bg-gradient-to-br from-primary-100 to-green-100 rounded-2xl animate-pulse-slow">
                        <Sparkles className="h-12 w-12 text-primary-600" />
                    </div>
                </div>
                <h1 className="text-5xl font-bold gradient-text animate-slide-up">Farmer Advisory Portal</h1>
                <p className="text-xl text-gray-600">
                    Get AI-powered farming advice backed by agricultural knowledge
                </p>
            </div>

            {/* Query Form */}
            <div className="card max-w-4xl mx-auto">
                <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Crop and Region Selection */}
                    <div className="grid md:grid-cols-3 gap-4">
                        <div className="space-y-2">
                            <label className="block text-sm font-semibold text-gray-700">
                                🌾 Crop
                            </label>
                            <select
                                value={crop}
                                onChange={(e) => setCrop(e.target.value)}
                                className="input"
                            >
                                <option value="wheat">Wheat</option>
                                <option value="rice">Rice</option>
                                <option value="cotton">Cotton</option>
                                <option value="sugarcane">Sugarcane</option>
                            </select>
                        </div>

                        <div className="space-y-2">
                            <label className="block text-sm font-semibold text-gray-700">
                                📍 Region
                            </label>
                            <select
                                value={region}
                                onChange={(e) => setRegion(e.target.value)}
                                className="input"
                            >
                                <option value="punjab">Punjab</option>
                                <option value="haryana">Haryana</option>
                                <option value="up">Uttar Pradesh</option>
                                <option value="maharashtra">Maharashtra</option>
                            </select>
                        </div>

                        <div className="space-y-2">
                            <label className="block text-sm font-semibold text-gray-700">
                                🌤️ Season
                            </label>
                            <select
                                value={season}
                                onChange={(e) => setSeason(e.target.value)}
                                className="input"
                            >
                                <option value="rabi">Rabi (Winter)</option>
                                <option value="kharif">Kharif (Monsoon)</option>
                                <option value="zaid">Zaid (Summer)</option>
                            </select>
                        </div>
                    </div>

                    {/* Question Input */}
                    <div className="space-y-2">
                        <label className="block text-sm font-semibold text-gray-700">
                            💬 Your Question
                        </label>
                        <textarea
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Ask any farming question..."
                            rows={4}
                            className="input resize-none"
                            required
                        />
                    </div>

                    {/* Submit Button */}
                    <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary w-full flex items-center justify-center space-x-2 relative overflow-hidden group"
                    >
                        {loading ? (
                            <>
                                <Loader2 className="h-5 w-5 animate-spin" />
                                <span>Getting AI Advice...</span>
                            </>
                        ) : (
                            <>
                                <Send className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                                <span>Get Advice</span>
                            </>
                        )}
                    </button>
                </form>

                {/* Example Questions */}
                <div className="mt-8 pt-6 border-t border-gray-200">
                    <p className="text-sm font-semibold text-gray-700 mb-3">💡 Example Questions:</p>
                    <div className="flex flex-wrap gap-2">
                        {exampleQuestions.map((q, idx) => (
                            <button
                                key={idx}
                                onClick={() => setQuery(q)}
                                className="text-sm px-4 py-2 bg-gradient-to-r from-gray-50 to-gray-100 hover:from-primary-50 hover:to-primary-100 rounded-xl text-gray-700 hover:text-primary-700 transition-all duration-300 border border-gray-200 hover:border-primary-300 hover:scale-105"
                            >
                                {q}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Loading Skeleton */}
            {loading && (
                <div className="card max-w-4xl mx-auto bg-gradient-to-br from-primary-50 to-white border-primary-200 animate-pulse">
                    <div className="space-y-4">
                        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                        <div className="h-4 bg-gray-200 rounded w-full"></div>
                        <div className="h-4 bg-gray-200 rounded w-5/6"></div>
                    </div>
                </div>
            )}

            {/* Response */}
            {response && !loading && (
                <div className="card max-w-4xl mx-auto bg-gradient-to-br from-primary-50 via-white to-green-50 border-primary-300 animate-slide-up">
                    <div className="flex items-start space-x-4 mb-6">
                        <div className="p-3 bg-gradient-to-br from-primary-500 to-primary-600 rounded-xl">
                            <CheckCircle2 className="h-7 w-7 text-white" />
                        </div>
                        <div className="flex-1">
                            <h3 className="text-2xl font-bold text-gray-900 mb-2">AI Response</h3>
                            <div className="flex items-center space-x-4 text-sm text-gray-600">
                                <span className="px-3 py-1 bg-white rounded-full border border-primary-200">
                                    🤖 {response.agent_name}
                                </span>
                                <span className="px-3 py-1 bg-white rounded-full border border-primary-200">
                                    ✨ {(response.confidence * 100).toFixed(0)}% Confidence
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="prose prose-lg max-w-none bg-white rounded-xl p-6 shadow-inner">
                        <p className="text-gray-800 whitespace-pre-wrap leading-relaxed">{response.recommendation || response.answer}</p>
                    </div>

                    {/* Sources */}
                    {response.sources && response.sources.length > 0 && (
                        <div className="mt-6 pt-6 border-t border-primary-200">
                            <div className="flex items-center space-x-2 mb-4">
                                <BookOpen className="h-6 w-6 text-primary-600" />
                                <h4 className="font-bold text-lg text-gray-900">Knowledge Sources</h4>
                            </div>
                            <div className="grid gap-3">
                                {response.sources.map((source, idx) => (
                                    <div key={idx} className="bg-white rounded-xl p-4 border-2 border-primary-100 hover:border-primary-300 transition-all hover:scale-[1.02]">
                                        <div className="flex items-center justify-between mb-2">
                                            <span className="font-semibold text-gray-900">📚 {source.source}</span>
                                            <span className="px-3 py-1 bg-gradient-to-r from-primary-100 to-green-100 text-primary-700 rounded-full text-xs font-bold">
                                                {(source.score * 100).toFixed(0)}% Match
                                            </span>
                                        </div>
                                        <p className="text-gray-600 text-sm leading-relaxed">{source.excerpt}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Error */}
            {error && !loading && (
                <div className="card max-w-4xl mx-auto bg-gradient-to-br from-red-50 to-white border-red-300 animate-slide-up">
                    <div className="flex items-start space-x-4">
                        <div className="p-3 bg-gradient-to-br from-red-500 to-red-600 rounded-xl">
                            <AlertCircle className="h-7 w-7 text-white" />
                        </div>
                        <div>
                            <h3 className="text-xl font-bold text-red-900 mb-2">Error</h3>
                            <p className="text-red-700">{error}</p>
                            <p className="text-sm text-red-600 mt-2">
                                💡 Tip: Make sure the backend server is running on port 8001
                            </p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
