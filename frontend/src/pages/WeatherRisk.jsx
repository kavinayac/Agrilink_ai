import { useState } from 'react';
import { CloudRain, Loader2, AlertTriangle, Shield, AlertCircle } from 'lucide-react';
import api from '../services/api';

export default function WeatherRisk() {
    const [crop, setCrop] = useState('wheat');
    const [region, setRegion] = useState('punjab');
    const [growthStage, setGrowthStage] = useState('flowering');
    const [loading, setLoading] = useState(false);
    const [assessment, setAssessment] = useState(null);
    const [error, setError] = useState(null);

    const handleAssess = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setAssessment(null);

        try {
            const result = await api.assessWeatherRisk(crop, region, 'weather_' + Date.now(), growthStage);
            setAssessment(result);
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
                <h1 className="text-4xl font-bold text-gray-900">Weather Risk Assessment</h1>
                <p className="text-lg text-gray-600">
                    Get AI-powered weather risk analysis and mitigation strategies
                </p>
            </div>

            {/* Form */}
            <div className="card max-w-4xl mx-auto">
                <form onSubmit={handleAssess} className="space-y-6">
                    <div className="grid md:grid-cols-3 gap-4">
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
                                Growth Stage
                            </label>
                            <select
                                value={growthStage}
                                onChange={(e) => setGrowthStage(e.target.value)}
                                className="input"
                            >
                                <option value="sowing">Sowing</option>
                                <option value="germination">Germination</option>
                                <option value="vegetative">Vegetative</option>
                                <option value="flowering">Flowering</option>
                                <option value="grain_filling">Grain Filling</option>
                                <option value="maturity">Maturity</option>
                            </select>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary w-full flex items-center justify-center space-x-2"
                    >
                        {loading ? (
                            <>
                                <Loader2 className="h-5 w-5 animate-spin" />
                                <span>Assessing Risk...</span>
                            </>
                        ) : (
                            <>
                                <CloudRain className="h-5 w-5" />
                                <span>Assess Weather Risk</span>
                            </>
                        )}
                    </button>
                </form>
            </div>

            {/* Assessment */}
            {assessment && (
                <div className="card max-w-4xl mx-auto bg-gradient-to-br from-sky-50 to-white border-sky-200">
                    <div className="flex items-start space-x-3 mb-4">
                        <AlertTriangle className="h-6 w-6 text-sky-600 flex-shrink-0 mt-1" />
                        <div className="flex-1">
                            <h3 className="text-lg font-semibold text-gray-900 mb-2">Risk Assessment</h3>
                            <div className="flex items-center space-x-4 text-sm text-gray-600 mb-4">
                                <span>Crop: {assessment.crop}</span>
                                <span>•</span>
                                <span>Region: {assessment.region}</span>
                                <span>•</span>
                                <span>Confidence: {(assessment.confidence * 100).toFixed(0)}%</span>
                            </div>
                        </div>
                    </div>

                    <div className="prose prose-sm max-w-none">
                        <p className="text-gray-800 whitespace-pre-wrap">{assessment.risk_assessment}</p>
                    </div>

                    {/* Sources */}
                    {assessment.sources && assessment.sources.length > 0 && (
                        <div className="mt-6 pt-6 border-t border-sky-200">
                            <h4 className="font-semibold text-gray-900 mb-3">Knowledge Sources</h4>
                            <div className="space-y-2">
                                {assessment.sources.map((source, idx) => (
                                    <div key={idx} className="text-sm bg-white rounded-lg p-3 border border-sky-100">
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

            {/* Weather Risks Info */}
            <div className="grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
                <div className="card bg-gradient-to-br from-orange-50 to-white border-orange-200">
                    <div className="flex items-start space-x-3">
                        <AlertTriangle className="h-6 w-6 text-orange-600 flex-shrink-0" />
                        <div>
                            <h4 className="font-semibold text-gray-900 mb-2">Common Risks</h4>
                            <ul className="text-sm text-gray-700 space-y-1">
                                <li>• Frost damage during flowering</li>
                                <li>• Heat stress in grain filling</li>
                                <li>• Heavy rainfall causing lodging</li>
                                <li>• Drought stress</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div className="card bg-gradient-to-br from-green-50 to-white border-green-200">
                    <div className="flex items-start space-x-3">
                        <Shield className="h-6 w-6 text-green-600 flex-shrink-0" />
                        <div>
                            <h4 className="font-semibold text-gray-900 mb-2">Mitigation Strategies</h4>
                            <ul className="text-sm text-gray-700 space-y-1">
                                <li>• Light irrigation before frost</li>
                                <li>• Adequate water during heat</li>
                                <li>• Proper drainage systems</li>
                                <li>• Resistant crop varieties</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
