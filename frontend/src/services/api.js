// API service for AgriLink backend
const API_BASE_URL = ''; // Relative path, handled by Vite proxy

class AgriLinkAPI {
    async farmerQuery(query, userId, crop = null, region = null, season = null) {
        const response = await fetch(`${API_BASE_URL}/api/farmer/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query,
                user_id: userId,
                crop,
                region,
                season,
            }),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        return response.json();
    }

    async getMarketInsights(crop, region, userId, action = 'analyze') {
        const response = await fetch(`${API_BASE_URL}/api/market/insights`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                crop,
                region,
                user_id: userId,
                action,
            }),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        return response.json();
    }

    async getBuyerPricing(crop, quantity, region, userId, qualityGrade = 'standard', askingPrice = null) {
        const response = await fetch(`${API_BASE_URL}/api/buyer/pricing`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                crop,
                quantity,
                quality_grade: qualityGrade,
                region,
                user_id: userId,
                asking_price: askingPrice,
            }),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        return response.json();
    }

    async assessWeatherRisk(crop, region, userId, growthStage = 'unknown') {
        const response = await fetch(`${API_BASE_URL}/api/weather/risk`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                crop,
                region,
                user_id: userId,
                growth_stage: growthStage,
            }),
        });

        if (!response.ok) {
            throw new Error(`API error: ${response.statusText}`);
        }

        return response.json();
    }

    async getHealth() {
        const response = await fetch(`${API_BASE_URL}/health`);
        return response.json();
    }
}

export default new AgriLinkAPI();
