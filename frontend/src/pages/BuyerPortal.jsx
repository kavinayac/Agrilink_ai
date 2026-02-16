import { useState } from 'react';
import { ShoppingCart, Loader2, DollarSign, AlertCircle } from 'lucide-react';
import api from '../services/api';

export default function BuyerPortal() {
    const [crop, setCrop] = useState('wheat');
    const [quantity, setQuantity] = useState('100');
    const [region, setRegion] = useState('punjab');
    const [qualityGrade, setQualityGrade] = useState('standard');
    const [askingPrice, setAskingPrice] = useState('');
    const [loading, setLoading] = useState(false);
    const [recommendation, setRecommendation] = useState(null);
    const [error, setError] = useState(null);

    const handleGetPricing = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setRecommendation(null);

        try {
            const result = await api.getBuyerPricing(
                crop,
                parseFloat(quantity),
                region,
                'buyer_' + Date.now(),
                qualityGrade,
                askingPrice ? parseFloat(askingPrice) : null
            );
            setRecommendation(result);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-4">
                <h1 className="text-4xl font-bold text-gray-900">Buyer Strategy Portal</h1>
                <p className="text-lg text-gray-600">
                    Get fair pricing recommendations and negotiation strategies
                </p>
            </div>

            {/* Form */}
            <div className="card max-w-4xl mx-auto">
                <form onSubmit={handleGetPricing} className="space-y-6">
                    <div className="grid md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Crop
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

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Quantity (quintals)
                            </label>
                            <input
                                type="number"
                                value={quantity}
                                onChange={(e) => setQuantity(e.target.value)}
                                className="input"
                                required
                                min="1"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Region
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

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                Quality Grade
                            </label>
                            <select
                                value={qualityGrade}
                                onChange={(e) => setQualityGrade(e.target.value)}
                                className="input"
                            >
                                <option value="premium">Premium</option>
                                <option value="standard">Standard</option>
                                <option value="basic">Basic</option>
                            </select>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Asking Price (₹ per quintal) - Optional
                        </label>
                        <input
                            type="number"
                            value={askingPrice}
                            onChange={(e) => setAskingPrice(e.target.value)}
                            className="input"
                            placeholder="Enter seller's asking price"
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary w-full flex items-center justify-center space-x-2"
                    >
                        {loading ? (
                            <>
                                <Loader2 className="h-5 w-5 animate-spin" />
                                <span>Analyzing Pricing...</span>
                            </>
                        ) : (
                            <>
                                <DollarSign className="h-5 w-5" />
                                <span>Get Pricing Strategy</span>
                            </>
                        )}
                    </button>
                </form>
            </div>

            {/* Recommendation */}
            {recommendation && (
                <div className="card max-w-4xl mx-auto bg-gradient-to-br from-amber-50 to-white border-amber-200">
                    <div className="flex items-start space-x-3 mb-4">
                        <ShoppingCart className="h-6 w-6 text-amber-600 flex-shrink-0 mt-1" />
                        <div className="flex-1">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">Pricing Recommendation</h3>
                            <div className="flex items-center space-x-4 text-sm text-gray-600 mb-4">
                                <span>Crop: {recommendation.crop}</span>
                                <span>•</span>
                                <span>Quantity: {recommendation.quantity} quintals</span>
                                <span>•</span>
                                <span>Confidence: {(recommendation.confidence * 100).toFixed(0)}%</span>
                            </div>
                        </div>
                    </div>

                    <div className="prose prose-sm max-w-none">
                        <p className="text-gray-800 whitespace-pre-wrap">{recommendation.recommendation}</p>
                    </div>

                    {/* Sources */}
                    {recommendation.sources && recommendation.sources.length > 0 && (
                        <div className="mt-6 pt-6 border-t border-amber-200">
                            <h4 className="font-semibold text-gray-900 mb-3">Market Data Sources</h4>
                            <div className="space-y-2">
                                {recommendation.sources.map((source, idx) => (
                                    <div key={idx} className="text-sm bg-white rounded-lg p-3 border border-amber-100">
                                        <div className="flex items-center justify-between">
                                            <span className="font-medium text-gray-900">{source.source}</span>
                                            <span className="text-xs text-gray-500">
                                                Score: {(source.score * 100).toFixed(0)}%
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Error */}
            {error && (
                <div className="card max-w-4xl mx-auto bg-red-50 border-red-200">
                    <div className="flex items-start space-x-3">
                        <AlertCircle className="h-6 w-6 text-red-600 flex-shrink-0" />
                        <div>
                            <h3 className="text-lg font-semibold text-red-900 mb-2">Error</h3>
                            <p className="text-red-700">{error}</p>
                        </div>
                    </div>
                </div>
            )}

            {/* Tips */}
            <div className="card max-w-4xl mx-auto bg-gradient-to-r from-amber-50 to-earth-50 border-amber-200">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Buyer Tips</h3>
                <ul className="space-y-2 text-sm text-gray-700">
                    <li className="flex items-start space-x-2">
                        <span className="text-amber-600">•</span>
                        <span>Check MSP (Minimum Support Price) before negotiating</span>
                    </li>
                    <li className="flex items-start space-x-2">
                        <span className="text-amber-600">•</span>
                        <span>Quality grade significantly affects fair price</span>
                    </li>
                    <li className="flex items-start space-x-2">
                        <span className="text-amber-600">•</span>
                        <span>Bulk purchases may qualify for discounts</span>
                    </li>
                    <li className="flex items-start space-x-2">
                        <span className="text-amber-600">•</span>
                        <span>Factor in transportation and storage costs</span>
                    </li>
                </ul>
            </div>
        </div>
    );
}
